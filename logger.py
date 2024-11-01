from objects import TerminalLine
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Logger:
    def __init__(self, terminal, fira_code):
        self.terminal = terminal
        self.fira_code = fira_code
    
    def push_message(self, message, error=False):
        self.terminal.addWidget(TerminalLine(f'[{datetime.now().time()}] {message}', self.fira_code, error))