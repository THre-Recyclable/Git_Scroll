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
        
        self.file_status_cache = {}  # 파일 상태 캐시

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super().columnCount(parent) + 1

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if section == super().columnCount():
            return "Branch"
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
                file_status = self.get_file_status(filepath)  # 파일 상태 캐시 사용
                return self.icons.get(file_status, super().data(index, role))

        return super().data(index, role)

    def get_file_status(self, filepath):
        if filepath in self.file_status_cache:  # 캐시에 파일 상태가 이미 저장된 경우
            return self.file_status_cache[filepath]
        
        file_status = get_git_status(filepath)  # 파일 상태 계산
        self.file_status_cache[filepath] = file_status  # 캐시에 파일 상태 저장
        
        return file_status
