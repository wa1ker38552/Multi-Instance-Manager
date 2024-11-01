from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

def setBackground(self, color):
    self.setAutoFillBackground(True)
    palette = self.palette()
    palette.setColor(self.backgroundRole(), QColor(color))
    self.setPalette(palette)

def string(text):
    return '\n'.join([l.strip() for l in text.split('\n')])

class Text(QLabel):
    def __init__(self, text, size=14, width=None):
        super().__init__()
        self.setText(text)
        self.setStyleSheet(f"font-size: {size}px;")

        if width:
            self.setFixedWidth(width)

class Button(QPushButton):
    def __init__(self, text, width, styles):
        super().__init__()
        self.setText(text)
        self.setFixedWidth(width)
        self.setStyleSheet(styles)
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

class Spacer(QWidget):
    def __init__(self, height):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addItem(QSpacerItem(0, height, QSizePolicy.Minimum, QSizePolicy.Fixed))

class FileButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText('Select Directory')
        self.setFixedWidth(150)
        self.setStyleSheet(string('''                        
        QPushButton {
            border: 1px solid #d4d4d4; 
            border-radius: 5px; 
            padding: 5px;
        }
        QPushButton:hover {
            background: #ebebeb;
        }'''))
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.clicked.connect(self.open_file)
        self.path = None

    def open_file(self):
        self.path = QFileDialog.getExistingDirectory(self, "Select a Folder")
        if self.path:
            self.setText(self.path[-30:])
            self.setStyleSheet('border: 1px solid #d4d4d4; border-radius: 5px; padding: 5px; text-align: right;')

class TerminalLine(QLabel):
    def __init__(self, text, fira_code, error=False):
        super().__init__()
        self.setText(text)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFont(fira_code)
        
        if (error):
            self.setStyleSheet('color: red;')