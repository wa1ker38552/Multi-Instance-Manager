from objects import TerminalLine
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

fira_code_id = QFontDatabase.addApplicationFont('assets/fonts/FiraCode-VariableFont_wght.ttf')
fira_code = QFont(QFontDatabase.applicationFontFamilies(fira_code_id)[0])

class Logger:
    def __init__(self, terminal):
        self.terminal = terminal
    
    def push_message(self, message, error=False):
        self.terminal.addWidget(TerminalLine(message, fira_code, error))