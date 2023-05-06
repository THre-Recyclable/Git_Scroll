from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os, subprocess, threading

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
        self.treeView.doubleClicked.connect(self.open_file)
    
        
    def context_menu(self):
        menu = QtWidgets.QMenu()
        open = menu.addAction("Open")
        open.triggered.connect(self.open_file)

        git_init = menu.addAction("git_init")
        git_init.triggered.connect(self.git_init)
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
        #git_mv = menu.addAction("git_mv")
        #git_mv.triggered.connect(self.git_mv)
        #git_commit = menu.addAction("git_commit")
        #git_commit.triggered.connect(self.git_commit)

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

    #def git_mv(self):

    #def git_commit(self):

    

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    fb = Browser()
    fb.show()
    app.exec_()
