from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


def load_fonts():
    fid = QFontDatabase.addApplicationFont('assets/fonts/OpenSans-VariableFont_wdth,wght.ttf')
    font = QFont(QFontDatabase.applicationFontFamilies(fid)[0])

    fira_code_id = QFontDatabase.addApplicationFont('assets/fonts/FiraCode-VariableFont_wght.ttf')
    fira_code = QFont(QFontDatabase.applicationFontFamilies(fira_code_id)[0])

    QApplication.setFont(font)
    return font, fira_code
    