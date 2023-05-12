from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os, subprocess, threading
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import *
import sys

from ui import file
from status import *
from gitfilestate import *


class Browser(file.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        self.setupUi(self)
        self.populate()
        self.setWindowTitle("Git Scroll")

    def populate(self):
        path = "C:\Windows"
        self.model = GitFileState()
        self.model.setRootPath(QtCore.QDir.rootPath())
        self.treeView.setModel(self.model)
        # self.treeView.setRootIndex(self.model.index(path))
        # self.treeView.setSortingEnabled(True)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.context_menu)
        # self.treeView.doubleClicked.connect(self.open_file)

    def context_menu(self):
        menu = QtWidgets.QMenu()
        open = menu.addAction("Open")
        open.triggered.connect(self.open_file)

        index = self.treeView.currentIndex()
        index = index.siblingAtColumn(1)
        filepath = self.model.filePath(index)

        if is_git_repository(filepath) and os.path.isfile(filepath):
            file_stat = get_status(filepath, False)

            if file_stat == 'untracked':
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

        elif os.path.isdir(filepath):
            git_init = menu.addAction("git_init")
            git_init.triggered.connect(self.git_init)
            git_commit = menu.addAction("git_commit")
            git_commit.triggered.connect(self.git_commit)

        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())

    def open_file(self):

        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        os.startfile(filepath)
    
    #git init
    def git_init(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        os.chdir(filepath)
        os.system('git init')

    #git add
    def git_add(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git add " + name
        os.system(Str)
        get_status(filepath, True)


    #git restore
    def git_restore(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git restore " + name
        os.system(Str)
        get_status(filepath, True)

    #git restore staged
    def git_restore_staged(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git restore --staged " + name
        os.system(Str)
        get_status(filepath, True)

    #git rm cached
    def git_rm_cached(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git rm --cached " + name
        os.system(Str)
        get_status(filepath, True)

    #git rm
    def git_rm(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git rm " + name
        os.system(Str)
        get_status(filepath, True)

    #git mv
    def git_mv(self):        
        self.new_window = ChangeName()
        self.new_window.name_entered.connect(self.handle_name_entered)
        self.new_window.show()

    def handle_name_entered(self, changed_name):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        file_list = self.get_file_in_directory(Ppath)
        file_list_check_result = self.file_list_check(file_list, changed_name)
        if changed_name =="" or file_list_check_result == False:
            self.name_change_error()
        else:
            os.chdir(Ppath)
            Str = "git mv " + name.rstrip() + " " + changed_name
            os.system(Str)

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
    

    #git commit
    def git_commit(self):
        self.file_list = QListWidget(self)

        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)

        commitable_files = self.get_commitable_files(filepath)
        self.show_commitable_files(commitable_files)

    def get_commitable_files(self, directory):
        repo = git.Repo(directory, search_parent_directories=True)
        if len(list(repo.branches)) == 0:
            staged_files = [item[0] for item in repo.index.entries]
        else:
            diffs = repo.index.diff("HEAD")
            staged_files = [item.a_path for item in diffs]
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
        staged_files = self.get_commitable_files(filepath)
        os.chdir(filepath)
        Str = "git commit -m \"" + commit_message + "\""
        os.system(Str)
        process_staged_files(filepath, staged_files)


class CommitableFileWindow(QDialog):
    ok_clicked = QtCore.pyqtSignal(bool)

    def __init__(self, commitable_files, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Commitable Files")
        self.setGeometry(100, 100, 400, 300)

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

    def open_get_commit_message(self):
        self.ok_clicked.emit(True)
        self.close()


class CommitMessageWindow(QWidget):
    message_entered = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Write Commit Message")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel("Write Commit Message: ", self)
        self.layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        self.layout.addWidget(self.line_edit)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.emit_message_entered)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def emit_message_entered(self):
        commit_message = self.line_edit.text()
        self.message_entered.emit(commit_message)
        self.close()


class ChangeName(QWidget):
    name_entered = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Change file name")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel("Change name:", self)
        self.layout.addWidget(self.label)

        self.line_edit = QLineEdit(self)
        self.layout.addWidget(self.line_edit)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.emit_name_entered)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def emit_name_entered(self):
        changed_name = self.line_edit.text()
        self.name_entered.emit(changed_name)
        self.close()

class NameChangeError(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Name Change Error")
        self.setGeometry(100,100,400,300)

        self.layout = QVBoxLayout()

        self.label = QLabel("Please enter an empty or non-overlappint file name")
        self.layout.addWidget(self.label)

        self.button = QPushButton("OK", self)
        self.button.clicked.connect(self.close)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    fb = Browser()
    fb.show()
    app.exec_()
