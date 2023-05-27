from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os, subprocess, threading
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
import sys


def get_current_branch(filepath):
    try:
        result = subprocess.check_output(['git', '-C', filepath, 'symbolic-ref', '--short', 'HEAD'], stderr=subprocess.DEVNULL, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError:
        return None


def getCommitHistory(branch):
    #command = ['git', 'log', branch, '--format=%H,%an,%s', '--graph']
    command = ['git', 'log', '--format=%H,%an,%s', '--graph']
    
    output = subprocess.check_output(command).decode('utf-8')
    blank_line = ''
    log_entries = []
    for line in output.splitlines():
        index =0
        for char in line:
            if  char.isalpha() or  char.isdigit():
                break
            index += 1
        if(len(line)<=index):
            commit_graph = line
            commit_hash = blank_line
            author_name = blank_line  
            commit_message = blank_line
        else:   
            commit_graph, commit_hash, author_name, commit_message = line[:index], line[index:].split(',')[0], line[index:].split(',')[1], line[index:].split(',')[2]
        log_entries.append({
            'commit_graph': commit_graph,
            'commit_hash': commit_hash,
            'author_name': author_name,
            'commit_message': commit_message
        })
    return log_entries

class showCommitHistory(QWidget):
    def __init__(self, filepath):
        super().__init__()
        self.initUI(filepath)

    def initUI(self, filepath):
        self.setWindowTitle('Commit History')

        branch = get_current_branch(filepath)
        commit_log = getCommitHistory(branch)
        
        table_widget = QTableWidget(self)
        
        table_widget.setColumnCount(4)
        table_widget.setRowCount(len(commit_log))
        
        table_widget.setGeometry(0,0,1000,1000)
        
        table_widget.setStyleSheet("QTableWidget { border: none; }")
        table_widget.horizontalHeader().setVisible(False)
        table_widget.verticalHeader().setVisible(False)

        table_widget.setColumnWidth(0,100)
        table_widget.setColumnWidth(1,200)
        table_widget.setColumnWidth(2,300)
        table_widget.setColumnWidth(3,400)

        row =0
        for log in commit_log:
            temp_graph = log['commit_graph']
            temp_hash = log['commit_hash']
            temp_name = log['author_name']
            temp_message = log['commit_message']
            for col in range(table_widget.columnCount()):
                if col ==0:
                    item = QTableWidgetItem(f'{temp_graph}')    
                elif col ==1:
                    item = QTableWidgetItem(f'{temp_hash}')
                elif col ==2:
                    item = QTableWidgetItem(f'{temp_name}')
                elif col==3:
                    item = QTableWidgetItem(f'{temp_message}')
                table_widget.setItem(row, col, item)
            row += 1
        

        self.setGeometry(300, 300, 1000, 1000)
        self.show()

        
