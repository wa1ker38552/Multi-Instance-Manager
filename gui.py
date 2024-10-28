import sys
import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from QSwitchControl import SwitchControl
from qframelesswindow import FramelessWindow


def setBackground(self, color):
    self.setAutoFillBackground(True)
    palette = self.palette()
    palette.setColor(self.backgroundRole(), QColor(color))
    self.setPalette(palette)

def string(text):
    return '\n'.join([l.strip() for l in text.split('\n')])

class Text(QLabel):
    def __init__(self, text, size=14):
        super().__init__()
        self.setText(text)
        self.setStyleSheet(f"font-size: {size}px")

class ConfigOption(QWidget):
    def __init__(self, name, description):
        super().__init__()
        self.layout = QHBoxLayout(self)

        v = QVBoxLayout()
        v.setSpacing(0)
        v.addWidget(Text(name))
        v.addWidget(Text(description, 12))
        
        self.layout.addLayout(v)
        setBackground(self, '#f7f7f7')

    def execute(self, code):
        exec(code)

class Button(QPushButton):
    def __init__(self, text, width, styles):
        super().__init__()
        self.setText(text)
        self.setFixedWidth(width)
        self.setStyleSheet(styles)
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

class AccountRow(QWidget):
    def __init__(self):
        super().__init__()
        self.ch = QGridLayout(self)
        self.ch.setContentsMargins(0, 0, 0, 0)

        self.columns = []
        for i, name in enumerate(['Username', 'Vip Server', 'Cookie']):
            col1 = QWidget()
            v = QVBoxLayout(col1)
            v.addWidget(Text(name, 10))
            
            _input = QLineEdit(self)
            _input.setStyleSheet('font-size: 12px')
            v.addWidget(_input)
            self.columns.append(_input)

            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(0)
            self.ch.addWidget(col1, 0, i)

        def delete_account_row():
            self.deleteLater()

        delete_button = QPushButton("")
        delete_button.setIcon(QIcon("assets/icon_delete.png"))
        delete_button.setIconSize(QSize(20, 20))
        delete_button.setStyleSheet("padding: 15px 0px 0px 0px;")
        delete_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        delete_button.clicked.connect(delete_account_row)
        self.ch.addWidget(delete_button, 0, 3)

    def get_row_data(self):
        return {
            'username': self.columns[0].text().strip(),
            'vip': self.columns[1].text().strip(),
            'cookie': self.columns[2].text().strip()
        }

class CreateConfigPage(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.setWidgetResizable(True)
        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        self.setLayout(QVBoxLayout())
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.parent = parent

        vb = QWidget()
        v = QVBoxLayout(vb)
        v.addWidget(QLabel("Create Configuration"))
        v.addWidget(Text("Create a new set of rules and accounts", 12))
        v.setSpacing(0)
        v.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(vb)

        self.config_name = ConfigOption('Config Name', 'Choose a name for this configuration')
        self.config_name.execute(string('''
            self.input_name = QLineEdit(self)
            self.input_name.setFixedWidth(200)
            self.input_name.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_name)
        '''))
 
        self.config_vip = ConfigOption('VIP Server', 'All alts will join this server if set, otherwise random server')
        self.config_vip.execute(string('''
            self.input_vip = QLineEdit(self)
            self.input_vip.setFixedWidth(200)
            self.input_vip.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_vip)
        '''))

        self.config_potato = ConfigOption('Potato Mode', 'Run all instances on potato graphics')
        self.config_potato.execute(string('''
            self.sc = SwitchControl(bg_color="#d4d4d4", circle_color="#f7f7f7", active_color="#00A4CD", animation_duration=0)
            self.layout.addWidget(self.sc)
        '''))
        
        self.config_fps = ConfigOption('Cap FPS', 'Cap the FPS on each instance, leave empty for 60')
        self.config_fps.execute(string('''
            self.input_fps = QLineEdit(self)
            self.input_fps.setFixedWidth(200)
            self.input_fps.setText('60')
            self.input_fps.setValidator(QIntValidator(0, 240))
            self.input_fps.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_fps)
        '''))
        
        layout.addWidget(self.config_name)
        layout.addWidget(self.config_vip)
        layout.addWidget(self.config_potato)
        layout.addWidget(self.config_fps)

        self.account_list = AccountList()
        layout.addWidget(QLabel("Add Accounts"))

        def add_account():
            self.account_list.add(AccountRow())

        create_account_button = Button("Add Account", 150, string('''
        QPushButton {
            background: #00A4CD;
            border-radius: 5px;
            color: white;   
            text-align: center;
            padding: 5px;
        }    
        QPushButton:hover {
            background: #0083a3;
        }                                   
        '''))
        create_account_button.clicked.connect(add_account)
        layout.addWidget(self.account_list)
        layout.addWidget(create_account_button)
        layout.addWidget(QLabel("Launch Settings"))

        self.config_delay = ConfigOption('Launch Delay', 'The delay after launching each instance, leave empty for 5s')
        self.config_delay.execute(string('''
            self.input_delay = QLineEdit(self)
            self.input_delay.setFixedWidth(50)
            self.input_delay.setText('5')
            self.input_delay.setValidator(QIntValidator(0, 9999))
            self.input_delay.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_delay)
        '''))

        self.config_retries = ConfigOption('Launch Retries', 'How many times it tries to re-launch an instance, leave empty for 5')
        self.config_retries.execute(string('''
            self.input_retries = QLineEdit(self)
            self.input_retries.setFixedWidth(50)
            self.input_retries.setText('5')
            self.input_retries.setValidator(QIntValidator(0, 9999))
            self.input_retries.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_retries)
        '''))

        layout.addWidget(self.config_delay)
        layout.addWidget(self.config_retries)

        layout.addWidget(QLabel("Window Settings"))
        self.config_x_offset = ConfigOption('Window X Offset', 'The x offset of each window, leave empty for 400px')
        self.config_x_offset.execute(string('''
            self.input_x_offset = QLineEdit(self)
            self.input_x_offset.setFixedWidth(50)
            self.input_x_offset.setText('400')
            self.input_x_offset.setValidator(QIntValidator(0, 1000))
            self.input_x_offset.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_x_offset)
        '''))

        self.config_y_offset = ConfigOption('Window Y Offset', 'The y offset of each window, leave empty for 300px')
        self.config_y_offset.execute(string('''
            self.input_y_offset = QLineEdit(self)
            self.input_y_offset.setFixedWidth(50)
            self.input_y_offset.setText('300')
            self.input_y_offset.setValidator(QIntValidator(0, 800))
            self.input_y_offset.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_y_offset)
        '''))

        self.config_stacking = ConfigOption('Stack Windows', 'X and Y Offset increment with each instance')
        self.config_stacking.execute(string('''
            self.sc = SwitchControl(bg_color="#d4d4d4", circle_color="#f7f7f7", active_color="#00A4CD", animation_duration=0)
            self.layout.addWidget(self.sc)
        '''))

        layout.addWidget(self.config_stacking)
        layout.addWidget(self.config_x_offset)
        layout.addWidget(self.config_y_offset)

        create_config_button = Button("Create", 80, string('''
        QPushButton {
            background: #00A4CD;
            border-radius: 5px;
            color: white;   
            text-align: center;
            padding: 5px;
        }    
        QPushButton:hover {
            background: #0083a3;
        }                                   
        '''))
        create_config_button.clicked.connect(self.create_config)
        layout.addWidget(create_config_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)
    
    def create_config(self):
        config_name = self.config_name.input_name.text().strip()
        config_vip = self.config_vip.input_vip.text().strip()
        config_potato = self.config_potato.sc.isChecked()
        config_fps = int(self.config_fps.input_fps.text())
        config_delay = int(self.config_delay.input_delay.text())
        config_retries = int(self.config_retries.input_retries.text())
        config_stacking = self.config_stacking.sc.isChecked()
        config_x_offset = int(self.config_x_offset.input_x_offset.text())
        config_y_offset = int(self.config_y_offset.input_y_offset.text())

        accounts = [row.get_row_data() for row in self.account_list.rows]
        accounts = [a for a in accounts if a['cookie']]

        errors = []
        if not config_name: errors.append('Invalid config name')
        if len(accounts) == 0: errors.append('Must add at least 1 user')
        for a in accounts:
            if not a['cookie'] or not a['username']:
                errors.append('Invalid username or cookie for user')
        if int(config_x_offset > 1000): errors.append('Invalid x offset (<= 1000)')
        if int(config_y_offset > 800): errors.append('Invalid y offset (<= 800)')
        if config_name in config_list: errors.append('Config already exists')
    
        if errors:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('\n'.join(errors))
            msg.setWindowTitle("Invalid Input")
            msg.exec_()
        else:
            config_list[config_name] = {
                'name': config_name,
                'vip': config_vip,
                'potato': config_potato,
                'fps': config_fps,
                'delay': config_delay,
                'retries': config_retries,
                'stacking': config_stacking,
                'x_offset': config_x_offset,
                'y_offset': config_y_offset
            }
            with open('multi_instance_client_data/config_list.json', 'w') as file:
                file.write(json.dumps(config_list, indent=2))

            self.parent.change_page(0)

class AccountList(QWidget):
    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.rows = []

    def add(self, widget):
        self.layout.addWidget(widget)
        self.rows.append(widget)
        
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

    def open_file(self):
        path = QFileDialog.getExistingDirectory(self, "Select a Folder")
        if path:
            self.setText(path[-30:])
            self.setStyleSheet('border: 1px solid #d4d4d4; border-radius: 5px; padding: 5px; text-align: right;')

class CreateSettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings"))

        config_bloxstrap = ConfigOption('Bloxstrap', 'Set Bloxstrap directory')
        config_bloxstrap.execute(string('''
            self.layout.addWidget(FileButton())
        ''').strip())

        layout.addWidget(config_bloxstrap)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/icon.png"))  
        self.setWindowTitle("Multi Instance Manager")
        self.setMinimumSize(800, 400)
        self.resize(800, 400)
        self.setStyleSheet(open('style.css', 'r').read())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        self.nav_buttons = QVBoxLayout()
        self.buttons = []
        for i, name in enumerate(['Configs', 'Create Config', 'Settings']):
            btn = QPushButton(space+name+space)
            btn.setIcon(QIcon('assets/icon_'+name))
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(lambda _, index=i: self.change_page(index))
            btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            self.nav_buttons.addWidget(btn)
            self.buttons.append(btn)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.nav_buttons.addItem(spacer)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(QLabel("This is Page 1"))
        self.stacked_widget.addWidget(CreateConfigPage(self))
        self.stacked_widget.addWidget(CreateSettingsPage())

        self.layout.addLayout(self.nav_buttons)
        self.layout.addWidget(self.stacked_widget)
        self.change_page(1)

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, button in enumerate(self.buttons):
            if i == index:
                button.setStyleSheet('border-color: #00A4CD; background: #d4d4d4')
            else:
                button.setStyleSheet('')


space = '‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎'
app = QApplication(sys.argv)
fid = QFontDatabase.addApplicationFont('OpenSans-VariableFont_wdth,wght.ttf')
font = QFont(QFontDatabase.applicationFontFamilies(fid)[0])
QApplication.setFont(font)

os.makedirs('multi_instance_client_data', exist_ok=True)
if not os.path.exists('multi_instance_client_data/config_list.json'):
    with open('multi_instance_client_data/config_list.json', 'w') as file:
        file.write(json.dumps({}))

with open('multi_instance_client_data/config_list.json', 'r') as file:
    config_list = json.loads(file.read())

window = MainWindow()
window.show()
sys.exit(app.exec_())
