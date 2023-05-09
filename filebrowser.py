from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os, subprocess, threading
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import *
import sys

from ui import file

class Browser(file.Ui_MainWindow,QtWidgets.QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        self.setupUi(self)
        self.populate()
        self.setWindowTitle("File Browser By SHADOW")

    def populate(self):
        path = "C:\Windows"
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(QtCore.QDir.rootPath())
        self.treeView.setModel(self.model)
        #self.treeView.setRootIndex(self.model.index(path))
        #self.treeView.setSortingEnabled(True)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.context_menu)
        #self.treeView.doubleClicked.connect(self.open_file)
    
        
    def context_menu(self):
        menu = QtWidgets.QMenu()
        open = menu.addAction("Open")
        open.triggered.connect(self.open_file)

        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)

        if os.path.isfile(filepath):
            git_add = menu.addAction("git_add")
            git_add.triggered.connect(self.git_add)
            git_restore = menu.addAction("git_restore")
            git_restore.triggered.connect(self.git_restore)
            git_restore_staged = menu.addAction("git_restore_staged")
            git_restore_staged.triggered.connect(self.git_restore_staged)
            git_rm_cached = menu.addAction("git_rm_cached")
            git_rm_cached.triggered.connect(self.git_rm_cached)
            git_rm = menu.addAction("git_rm")
            git_rm.triggered.connect(self.git_rm)
            git_mv = menu.addAction("git_mv")
            git_mv.triggered.connect(self.git_mv)
        

        if os.path.isdir(filepath):
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
    
    def git_init(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        os.chdir(filepath)
        os.system('git init')

    def git_add(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git add " + name
        os.system(Str)

    def git_restore(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git restore " + name
        os.system(Str)
    
    def git_restore_staged(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git restore --staged " + name
        os.system(Str)

    def git_rm_cached(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git rm --cached " + name
        os.system(Str)

    def git_rm(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git rm " + name
        os.system(Str)

        


    def git_mv(self):
        
        self.new_window = ChangeName()
        self.new_window.name_entered.connect(self.handle_name_entered)
        self.new_window.show()
    
    def handle_name_entered(self, changed_name):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        Ppath = os.path.abspath(os.path.join(filepath, os.pardir))
        name = self.model.fileName(index)
        os.chdir(Ppath)
        Str = "git mv " + name.rstrip() + " " + changed_name
        self.do_git_mv(Str)
        os.system(Str)

    def do_git_mv(self, Str):
        os.system(Str)
        print(Str)

    def dialog_close(self):
        self.dialog.close()

    #파일 상태 추출
    #git status --porcelain 파일경로
    #스태이징 파일 목록 추출
    #git diff --name-only --cached

    def git_commit(self):
        index = self.treeView.currentIndex()
        filepath = self.model.filePath(index)
        os.chdir(filepath)
        command = "git diff --name-only --cached"
        result = os.popen(command).read().strip()
        
        self.dialog=QDialog()

        self.dialog.setWindowTitle('staged file list')
        self.dialog.setWindowModality(1)
        self.dialog.resize(400,200)
        self.dialog.show()

        staged_file = QLabel(result, self.dialog)
        staged_file.move(50,50)


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


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    fb = Browser()
    fb.show()
    app.exec_()
