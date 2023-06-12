from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os, subprocess, threading
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
import sys
import getpass

from commitHistory import *
from ui import file
from status import *
from gitfilestate import *


class Browser(file.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        self.setupUi(self)
        self.populate()
        self.setWindowTitle("Git Scroll")

        # 추가 2
        self.create_action = QtWidgets.QAction("Branch_Create", self)
        self.create_action.triggered.connect(self.create_branch)

        self.delete_action = QtWidgets.QAction("Branch_Delete", self)
        self.delete_action.triggered.connect(self.delete_branch)

        self.rename_action = QtWidgets.QAction("Branch_Rename", self)
        self.rename_action.triggered.connect(self.rename_branch)

        self.checkout_action = QtWidgets.QAction("Branch_Checkout", self)
        self.checkout_action.triggered.connect(self.checkout_branch)

        self.merge_action = QtWidgets.QAction("Branch_Merge", self)
        self.merge_action.triggered.connect(self.merge_branch)

        self.clone_action = QtWidgets.QAction("git_clone", self)
        self.clone_action.triggered.connect(self.clone_repo)

        # self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.treeView.customContextMenuRequested.connect(self.context_menu)

        # 추가 1
        self.branch_label = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.branch_label)
        self.branch_cache = {}  # 브랜치 캐시 추가        

    def populate(self):
        path = "C:\Windows"
        self.model = GitFileState()
        self.model.setRootPath(QtCore.QDir.rootPath())
        self.treeView.setModel(self.model)
        # self.treeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # self.treeView.setRootIndex(self.model.index(path))
        # self.treeView.setSortingEnabled(True)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.context_menu)
        # self.treeView.doubleClicked.connect(self.open_file)

        # 추가 1
        self.model.dataChanged.connect(self.update_branch_label)
        self.treeView.clicked.connect(self.update_branch_label)

    def context_menu(self, point):
        menu = QtWidgets.QMenu()
        open = menu.addAction("Open")
        open.triggered.connect(self.open_file)

        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)

        if self.model.isDir(index):
            if is_git_repository(filepath):
                # Add branch-related actions
                menu.addAction(self.create_action)
                menu.addAction(self.delete_action)
                menu.addAction(self.rename_action)
                menu.addAction(self.checkout_action)
                menu.addAction(self.merge_action)
                commit_history = menu.addAction("Commit History")
                commit_history.triggered.connect(self.commit_history)

                git_commit = menu.addAction("git_commit")
                git_commit.triggered.connect(self.git_commit)

                menu.addAction(self.clone_action)

            else:
                git_init = menu.addAction("git_init")
                git_init.triggered.connect(self.git_init)

                menu.addAction(self.clone_action)
        else:
            # Add file-related actions
            file_stat = get_git_status(filepath)

            if file_stat == 'untracked' or file_stat == 'ignored':
                git_add = menu.addAction("git_add")
                git_add.triggered.connect(self.git_add)

            elif file_stat == 'committed':
                git_rm_cached = menu.addAction("git_rm_cached")
                git_rm_cached.triggered.connect(self.git_rm_cached)
                git_rm = menu.addAction("git_rm")
                git_rm.triggered.connect(self.git_rm)
                git_mv = menu.addAction("git_mv")
                git_mv.triggered.connect(self.git_mv)

            elif file_stat == 'modified':
                git_add = menu.addAction("git_add")
                git_add.triggered.connect(self.git_add)
                git_restore = menu.addAction("git_restore")
                git_restore.triggered.connect(self.git_restore)

            elif file_stat == 'staged':
                git_restore_staged = menu.addAction("git_restore_staged")
                git_restore_staged.triggered.connect(self.git_restore_staged)

        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())
        menu.clear()
        self.update_branch_label(index)  # 브랜치 레이블 업데이트

    def open_file(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        os.startfile(filepath)

    def commit_history(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        self.new_window = showCommitHistory(filepath)
        self.new_window.show()

    # git init
    def git_init(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        os.chdir(filepath)
        os.system('git init')

    # git add
    def git_add(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index.siblingAtColumn(0))
        os.chdir(Ppath)
        Str = "git add " + name
        if get_git_status(filepath) == 'ignored':
            Str += " -f"
        os.system(Str)
        calculate_status(filepath)

    # git restore
    def git_restore(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index.siblingAtColumn(0))
        os.chdir(Ppath)
        Str = "git restore " + name
        os.system(Str)
        calculate_status(filepath)

    # git restore staged
    def git_restore_staged(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index.siblingAtColumn(0))
        os.chdir(Ppath)
        Str = "git restore --staged " + name
        os.system(Str)
        calculate_status(filepath)

    # git rm cached
    def git_rm_cached(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index.siblingAtColumn(0))
        os.chdir(Ppath)
        Str = "git rm --cached " + name
        os.system(Str)
        calculate_status(filepath)

    # git rm
    def git_rm(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        repo = git.Repo(filepath, search_parent_directories=True)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index.siblingAtColumn(0))
        os.chdir(Ppath)
        Str = "git rm " + name
        os.system(Str)
        calculate_status(repo.working_tree_dir)

    # git mv
    def git_mv(self):
        self.new_window = ChangeName()
        self.new_window.name_entered.connect(self.handle_name_entered)
        self.new_window.show()

    def handle_name_entered(self, changed_name):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        repo = git.Repo(filepath, search_parent_directories=True)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index.siblingAtColumn(0))
        file_list = self.get_file_in_directory(Ppath)
        file_list_check_result = self.file_list_check(file_list, changed_name)
        if changed_name == "" or file_list_check_result == False:
            self.name_change_error()
        else:
            os.chdir(Ppath)
            Str = "git mv " + name.rstrip() + " " + changed_name
            os.system(Str)
            calculate_status(repo.working_tree_dir)

    def get_file_in_directory(self, directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
        return file_list

    def file_list_check(self, file_list, changed_name):
        for file in file_list:
            file_name = os.path.basename(file)
            if file_name == changed_name:
                return False
        return True

    def name_change_error(self):
        self.new_window = NameChangeError()
        self.new_window.show()

    # git commit
    def git_commit(self):
        self.file_list = QListWidget(self)

        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)

        commitable_files = self.get_commitable_files(filepath)
        self.show_commitable_files(commitable_files)

    def get_commitable_files(self, directory):
        repo = git.Repo(directory, search_parent_directories=True)
        # if len(list(repo.branches)) == 0:
        #     staged_files = [item[0] for item in repo.index.entries]
        # else:
        #     diffs = repo.index.diff("HEAD")
        #     staged_files = [item.a_path for item in diffs]
        # return staged_files
        status_output = repo.git.execute(['git', 'status', '--porcelain', '--ignored']).splitlines()
        staged_files = []
        for line in status_output:
            status, filepath = line[:2], line[3:]
            if '->' in filepath:
                _, filepath = filepath.split(' -> ')

            if status == 'A ':
                staged_files.append('(new) ' + filepath)
            elif status == 'M ':
                staged_files.append('(modified) ' + filepath)
            elif status == 'D ':
                staged_files.append('(deleted) ' + filepath)
            elif status == 'R ':
                staged_files.append('(renamed) ' + filepath)
            elif status == 'C ':
                staged_files.append('(copied) ' + filepath)
            elif status == 'U ':
                staged_files.append('(Unmerged) ' + filepath)

        return staged_files

    def show_commitable_files(self, commitable_files):
        commitable_files_window = CommitableFileWindow(commitable_files, parent=self)
        commitable_files_window.ok_clicked.connect(self.handle_ok_clicked)
        commitable_files_window.show()

    def handle_ok_clicked(self):
        self.new_window = CommitMessageWindow()
        self.new_window.message_entered.connect(self.handle_message_entered)
        self.new_window.show()

    def handle_message_entered(self, commit_message):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        repo = git.Repo(filepath, search_parent_directories=True)
        staged_files = self.get_commitable_files(filepath)
        if len(commit_message.strip()) == 0:
            self.commit_message_change_error()
        else:
            os.chdir(filepath)
            Str = "git commit -m \"" + commit_message + "\""
            os.system(Str)
            if len(commit_message.strip()) != 0 and len(staged_files) > 0:
                # process_staged_files(filepath, staged_files)
                # process_staged_directories(filepath)
                calculate_status(repo.working_tree_dir)

    def commit_message_change_error(self):
        self.new_CMC_window = CommitMessageError()
        self.new_CMC_window.show()

    # 추가 2
    # Create branch
    def create_branch(self):
        branch_name, ok = QtWidgets.QInputDialog.getText(self, "Create Branch", "Enter branch name:")
        while ok and not branch_name:
            QtWidgets.QMessageBox.warning(self, "Error", "Branch name is required.")
            branch_name, ok = QtWidgets.QInputDialog.getText(self, "Create Branch", "Enter branch name:")
        if ok and branch_name:
            index = self.treeView.currentIndex()
            filepath = self.model.filePath(index)
            repo = git.Repo(filepath, search_parent_directories=True)
            try:
                repo.git.branch(branch_name)
            except git.GitCommandError as e:
                QtWidgets.QMessageBox.critical(self, "Error", str(e))

    # Delete branch
    def delete_branch(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        repo = git.Repo(filepath, search_parent_directories=True)
        branches = [b.name for b in repo.branches]
        branch, ok = QtWidgets.QInputDialog.getItem(self, "Delete Branch", "Select branch to delete:", branches,
                                                    editable=False)
        if ok and branch:
            if branch == repo.active_branch.name:
                QtWidgets.QMessageBox.warning(self, "Warning", "Cannot delete currently checked out branch.")
            else:
                try:
                    repo.git.branch("-D", branch)
                except git.GitCommandError as e:
                    QtWidgets.QMessageBox.critical(self, "Error", str(e))

    # Rename branch
    def rename_branch(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        repo = git.Repo(filepath, search_parent_directories=True)
        branches = [b.name for b in repo.branches]
        branch, ok = QtWidgets.QInputDialog.getItem(self, "Rename Branch", "Select branch to rename:", branches,
                                                    editable=False)
        if ok and branch:
            new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename Branch", "Enter new branch name:")
            while ok and not new_name:
                QtWidgets.QMessageBox.warning(self, "Error", "Branch name is required.")
                new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename Branch", "Enter new branch name:")
            if ok and new_name:
                if branch == repo.active_branch.name:
                    QtWidgets.QMessageBox.warning(self, "Warning", "Cannot rename currently checked out branch.")
                else:
                    try:
                        repo.git.branch("-m", branch, new_name)
                    except git.GitCommandError as e:
                        QtWidgets.QMessageBox.critical(self, "Error", str(e))

    # Checkout branch
    def checkout_branch(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        repo = git.Repo(filepath, search_parent_directories=True)
        branches = [b.name for b in repo.branches if b.name != repo.active_branch.name]

        if not branches:
            QtWidgets.QMessageBox.warning(self, "Warning", "No other branches to checkout.")
            return

        branch, ok = QtWidgets.QInputDialog.getItem(self, "Checkout Branch", "Select branch to checkout:", branches,
                                                    editable=False)
        if ok and branch:
            if branch == repo.active_branch.name:
                QtWidgets.QMessageBox.warning(self, "Warning", "Already on the selected branch.")
            else:
                try:
                    repo.git.checkout(branch)
                    self.update_branch_label(index)
                except git.GitCommandError as e:
                    QtWidgets.QMessageBox.critical(self, "Error", str(e))

    # Merge branch
    def merge_branch(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        repo = git.Repo(filepath, search_parent_directories=True)
        current_branch = repo.active_branch.name
        branches = [b.name for b in repo.branches if b.name != current_branch]

        if not branches:
            QtWidgets.QMessageBox.warning(self, "Warning", "No other branches to merge.")
            return

        branch, ok = QtWidgets.QInputDialog.getItem(self, "Merge Branch", "Select branch to merge:", branches,
                                                    editable=False)
        if ok and branch:
            if branch == current_branch:
                QtWidgets.QMessageBox.warning(self, "Warning", "Already on the selected branch.")
            else:
                try:
                    repo.git.merge(branch)
                    QtWidgets.QMessageBox.information(self, "Success",
                                                      f"Merged branch '{branch}' into '{current_branch}' successfully.")
                except git.GitCommandError as e:
                    unmerged_paths = "\n".join(f"{path}" for path, _ in repo.index.unmerged_blobs().items())
                    QtWidgets.QMessageBox.critical(self, "Error", f"{str(e)}\n\nUnmerged paths:\n{unmerged_paths}")

    def clone_repo(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        clone_dialog = CloneDialog(filepath)
        if clone_dialog.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Success", f"Repository cloned successfully.")

    def update_branch_label(self, index):
        filepath = self.model.filePath(index)
        if is_git_repository(filepath):
            repo = git.Repo(filepath, search_parent_directories=True)
            branch = repo.active_branch.name
            root_index = index.siblingAtColumn(0)
            root_path = self.model.filePath(root_index)
            self.branch_label.setText(f"Current Path\t: {root_path}\nCurrent Branch\t: {branch}")
        else:
            self.branch_label.setText("")
            # self.branch_label.setText("Current Branch\t: N/A")


class CommitableFileWindow(QDialog):
    ok_clicked = QtCore.pyqtSignal(bool)

    def __init__(self, commitable_files, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Commitable Files")
        self.setGeometry(300, 300, 400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel("Commitable Files : ", self)
        self.layout.addWidget(self.label)

        file_list = QListWidget(self)
        self.layout.addWidget(file_list)
        for file_path in commitable_files:
            list_item = QListWidgetItem(file_path)
            file_list.addItem(list_item)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.open_get_commit_message)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        font = QFont("Arial", 10)
        self.setFont(font)

    def open_get_commit_message(self):
        self.ok_clicked.emit(True)
        self.close()


class CommitMessageWindow(QWidget):
    message_entered = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Write Commit Message")
        self.setGeometry(300, 300, 400, 100)

        self.layout = QVBoxLayout()

        self.label = QLabel("Write Commit Message: ", self)
        self.layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        self.layout.addWidget(self.line_edit)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.emit_message_entered)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        font = QFont("Arial", 10)
        self.setFont(font)

    def emit_message_entered(self):
        commit_message = self.line_edit.text()
        self.message_entered.emit(commit_message)
        self.close()


class ChangeName(QWidget):
    name_entered = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Change file name")
        self.setGeometry(300, 300, 400, 100)

        self.layout = QVBoxLayout()

        self.label = QLabel("Change name:", self)
        self.layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        self.layout.addWidget(self.line_edit)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.emit_name_entered)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        font = QFont("Arial", 10)
        self.setFont(font)

    def emit_name_entered(self):
        changed_name = self.line_edit.text()
        self.name_entered.emit(changed_name)
        self.close()


class NameChangeError(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Name Change Error")
        self.setGeometry(300, 200, 400, 100)

        self.layout = QVBoxLayout()

        self.label = QLabel("Empty or duplicated name is not allowed.")
        self.layout.addWidget(self.label)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.close)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        font = QFont("Arial", 10)
        self.setFont(font)


class CommitMessageError(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Commit Message Error")
        self.setGeometry(300, 200, 400, 100)

        self.layout = QVBoxLayout()

        self.label = QLabel("Empty Commit Message is not allowed.")
        self.layout.addWidget(self.label)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.close)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        font = QFont("Arial", 10)
        self.setFont(font)


class CloneDialog(QtWidgets.QDialog):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.url_input = QtWidgets.QLineEdit(self)
        self.confirm_button = QtWidgets.QPushButton('Clone', self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.init_ui()

    def init_ui(self):
        self.layout.addWidget(QtWidgets.QLabel('Repository URL:', self))
        self.layout.addWidget(self.url_input)
        self.confirm_button.clicked.connect(self.clone_repository)
        self.layout.addWidget(self.confirm_button)

    def clone_repository(self):
        url = self.url_input.text().strip()

        if not url:
            QtWidgets.QMessageBox.warning(self, "Warning", "Repository URL is required.")
            return

        repo_name = url.split("/")[-1]  # URL에서 저장소 이름 추출
        if ".git" in repo_name:
            repo_name = repo_name.replace(".git", "")
        clone_dir = self.filepath  # 받은 파일 경로를 클론 경로로 사용

        # Try cloning the repository with the provided URL
        try:
            git.Repo.clone_from(url, os.path.join(clone_dir, repo_name))
            self.accept()
            return
        except git.exc.GitCommandError:
            pass

        # If cloning with the provided URL fails, ask the user what to do next
        messageBox = QtWidgets.QMessageBox()
        messageBox.setIcon(QtWidgets.QMessageBox.Question)
        messageBox.setWindowTitle("Clone failed")
        messageBox.setText("Cloning with the provided URL failed. What do you want to do next?")
        messageBox.addButton(QtWidgets.QPushButton('Try with saved credentials'), QtWidgets.QMessageBox.YesRole)
        messageBox.addButton(QtWidgets.QPushButton('Enter new credentials'), QtWidgets.QMessageBox.NoRole)
        messageBox.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.RejectRole)

        result = messageBox.exec_()

        if result == 0:  # Try with saved credentials
            if not self.try_with_saved_credentials(url, clone_dir, repo_name):
                self.enter_new_credentials(url, clone_dir, repo_name)
        elif result == 1:  # Enter new credentials
            self.enter_new_credentials(url, clone_dir, repo_name)
        else:  # Cancel
            self.reject()

    def try_with_saved_credentials(self, url, clone_dir, repo_name):
        if os.path.exists("credentials.txt"):
            with open("credentials.txt", "r") as file:
                credentials = [line.strip().split(",") for line in file.readlines()]
                for id_, token in credentials:
                    try:
                        https_url = url[:8] + id_ + ':' + token + '@' + url[8:]
                        git.Repo.clone_from(https_url, os.path.join(clone_dir, repo_name))
                        QtWidgets.QMessageBox.information(self, "Cloned", f"Cloned with ID: {id_} and token: {token}")
                        self.accept()
                        return True
                    except git.exc.GitCommandError:
                        pass

        QtWidgets.QMessageBox.critical(self, "Error", "Cloning failed with stored credentials.")
        return False

    def enter_new_credentials(self, url, clone_dir, repo_name):
        credential_dialog = CredentialDialog(self)

        if credential_dialog.exec_() == QtWidgets.QDialog.Accepted:
            id_ = credential_dialog.id_input.text().strip()
            token = credential_dialog.token_input.text().strip()

            if id_ and token:
                try:
                    https_url = url[:8] + id_ + ':' + token + '@' + url[8:]
                    git.Repo.clone_from(https_url, os.path.join(clone_dir, repo_name))
                    with open("credentials.txt", "a") as file:
                        file.write(f"{id_},{token}\n")
                    self.accept()
                except git.exc.GitCommandError as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Cloning failed with provided credentials: {str(e)}")
            else:
                QtWidgets.QMessageBox.critical(self, "Error",
                                               "You need to provide both ID and token to clone a private repository.")

        else:
            self.reject()


class CredentialDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.id_input = QtWidgets.QLineEdit(self)
        self.token_input = QtWidgets.QLineEdit(self)
        self.confirm_button = QtWidgets.QPushButton('Confirm', self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.init_ui()

    def init_ui(self):
        self.layout.addWidget(QtWidgets.QLabel('ID (only for private repository):', self))
        self.layout.addWidget(self.id_input)

        self.layout.addWidget(QtWidgets.QLabel('Token (only for private repository):', self))
        self.layout.addWidget(self.token_input)

        self.confirm_button.clicked.connect(self.accept)
        self.layout.addWidget(self.confirm_button)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    fb = Browser()
    fb.show()
    app.exec_()
