from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Logger:
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
    
    def push_message(self, message, status=0):
        self.worker.emit(f'[{datetime.now().strftime("%H:%M:%S")}] {message}', status)