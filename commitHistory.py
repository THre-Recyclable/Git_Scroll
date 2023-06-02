from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import os, subprocess, threading
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
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

def get_commit_info(commit_hash):
    command = ['git', 'show', commit_hash]
    output = subprocess.check_output(command).decode('utf-8')
    return output


class showCommitHistory(QWidget):
    def __init__(self, filepath):
        super().__init__()
        self.initUI(filepath)

    def initUI(self, filepath):
        self.setWindowTitle('Commit History')

        branch = get_current_branch(filepath)
        commit_log = getCommitHistory(branch)
        
        table_widget = QTableWidget(self)
        
        graph_cnt = self.get_max_graph(commit_log)
        table_widget.setColumnCount(graph_cnt + 2)
        table_widget.setRowCount(len(commit_log))

        widget_width = 50*graph_cnt + 600

        table_widget.setGeometry(0,0,1000,widget_width)
        
        table_widget.setStyleSheet("QTableWidget { border: none; }")
        table_widget.horizontalHeader().setVisible(False)
        table_widget.verticalHeader().setVisible(False)

        for i in range(graph_cnt):
            table_widget.setColumnWidth(i, 5)
        #table_widget.setColumnWidth(0,100)
        #table_widget.setColumnWidth(1,400)
        #table_widget.setColumnWidth(2,100)
        #table_widget.setColumnWidth(3,400)
        table_widget.setColumnWidth(graph_cnt, 100)
        table_widget.setColumnWidth(graph_cnt + 1, 500)
        
        hash_list = self.get_hash_list(commit_log)

        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        #table_widget.itemClicked.connect(self.handle_cell_clicked)
        table_widget.itemClicked.connect(lambda item: self.handle_cell_clicked(item, hash_list))

        row =0
        for log in commit_log:
            temp_graph = log['commit_graph']
            temp_hash = log['commit_hash']
            temp_name = log['author_name']
            temp_message = log['commit_message']
            for col in range(graph_cnt):
                if len(temp_graph) > col:
                    graph_frag = ""
                    if temp_graph[col] == "|":
                        graph_frag = "\u2191"
                    elif temp_graph[col] == "*":
                        graph_frag = "*"
                    elif temp_graph[col] == "/":
                        graph_frag = "\u2197"
                    elif temp_graph[col] == "\\":
                        graph_frag = "\u2196"
                    elif temp_graph[col] == "_":
                        graph_frag = "-"

                    item = QTableWidgetItem(f'{graph_frag}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table_widget.setItem(row, col, item)
                else :
                    empty_string = ""
                    item = QTableWidgetItem(f'{empty_string}')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table_widget.setItem(row, col, item)
                
            item = QTableWidgetItem(f'{temp_name}')
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table_widget.setItem(row, graph_cnt, item)
            
            item = QTableWidgetItem(f'{temp_message}')
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table_widget.setItem(row, graph_cnt + 1, item)
    
            row += 1
        

        self.setGeometry(100, 100, 1000, widget_width)
        self.setFixedSize(1000,widget_width)
        self.show()
       
    def handle_cell_clicked(self, input_item, hash_list):
        row = input_item.row()
        
        item = hash_list[row]
        #item = input_item.text()
        if item is not None:
            commit_info = get_commit_info(item)
            self.new_window = showCommitInfo(commit_info)
            self.new_window.show()

    def get_max_graph(self, commit_log):
        max_graph = 0
        for log in commit_log:
            count = 0
            temp_graph = log['commit_graph']
            for col in range(len(temp_graph)):
                if temp_graph[col] == "|" or temp_graph[col] == "*" or temp_graph[col] == "/" or temp_graph[col] == "\\" or temp_graph[col] == "_":
                    count += 1
                elif temp_graph[col] == " ":
                    if col+1 < len(temp_graph) and (temp_graph[col+1] == "|" or temp_graph[col+1] == "*" or temp_graph[col+1] == "/" or temp_graph[col+1] == "\\" or temp_graph[col+1] == "_"):
                        count += 1

            if max_graph < count:
                max_graph = count
        return max_graph
    
    def get_hash_list(self, commit_log):
        hash_list = []
        for log in commit_log:
            temp_hash = log['commit_hash']
            hash_list.append(temp_hash)
        return hash_list

class showCommitInfo(QWidget):
    def __init__(self, commit_info):
        super().__init__()
        
        self.setWindowTitle("Commit Information")
        self.setGeometry(300, 300, 400, 300)

        self.layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(commit_info)
        content_layout.addWidget(text_edit)
       
        scroll_area.setWidget(content_widget)
        self.layout.addWidget(scroll_area)



        self.setLayout(self.layout)

        self.show()
