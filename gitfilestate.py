from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from status import *

class GitFileState(QtWidgets.QFileSystemModel):
    def __init__(self, parent=None):
        super(GitFileState, self).__init__(parent)
    
        self.icons = {
            "untracked": QtGui.QIcon("resources/untracked_icon.PNG"),
            "modified": QtGui.QIcon("resources/modified_icon.PNG"),
            "staged": QtGui.QIcon("resources/staged_icon.PNG"),
            "committed": QtGui.QIcon("resources/committed_icon.PNG")
        }

    def data(self, index, role):
        if role == QtCore.Qt.DecorationRole and index.column() == 0:
            file_info = self.fileInfo(index)

            if file_info.isFile():
                filepath = self.filePath(index)

                if os.path.exists(filepath) and is_git_repository(filepath):
                    file_status = get_status(filepath, False)
                    return self.icons.get(file_status, super().data(index, role))

            elif file_info.isDir():
                dirpath = self.filePath(index)

                if os.path.exists(dirpath) and is_git_repository(dirpath) and is_root(dirpath) is False:
                    dir_status = get_directory_status(dirpath)
                    return self.icons.get(dir_status, super().data(index, role))
    
        return super().data(index, role)
