from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import git
from status import *
import os

class GitFileState(QtWidgets.QFileSystemModel):
    def __init__(self, parent=None):
        super(GitFileState, self).__init__(parent)
        
        self.icons = {
            "untracked": QtGui.QIcon("resources/untracked_icon.PNG"),
            "modified": QtGui.QIcon("resources/modified_icon.PNG"),
            "staged": QtGui.QIcon("resources/staged_icon.PNG"),
            "committed": QtGui.QIcon("resources/committed_icon.PNG")
        }

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super().columnCount(parent)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        return super().headerData(section, orientation, role)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        if column == super().columnCount():
            filepath = self.filePath(index.siblingAtColumn(0))
            if is_git_repository(filepath) and self.isDir(index) and is_root(filepath):
                repo = git.Repo(filepath, search_parent_directories=True)
                branch = repo.active_branch.name
                if role == QtCore.Qt.TextAlignmentRole:
                    return int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                return branch
            else:
                return ""
        elif role == QtCore.Qt.DecorationRole and column == 0:
            file_info = self.fileInfo(index)
            filepath = self.filePath(index)

            if os.path.exists(filepath) and is_git_repository(filepath) and not is_root(filepath):
                file_status = get_git_status(filepath)
                return self.icons.get(file_status, super().data(index, role))

        return super().data(index, role)