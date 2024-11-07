from account_manager import AccountManager
from QSwitchControl import SwitchControl
from PyQt5.QtWidgets import *
from threading import Thread
from fonts import load_fonts
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from logger import Logger
from PyQt5 import QtCore
from objects import *
from helpers import *
import copy
import json
import time
import sys
import os

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
        try:
            return {
                'username': self.columns[0].text().strip(),
                'vip': self.columns[1].text().strip(),
                'cookie': self.columns[2].text().strip()
            }
        except RuntimeError: 
            return {
                'username': None,
                'vip': None,
                'cookie': None
            }
    

class CreateConfigList(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.update_configs()
        self.parent = parent

    def update_configs(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for config in config_list:
            c = QPushButton()
            c.setObjectName("config-parent")
            hstack = QHBoxLayout(c)
            hstack.setContentsMargins(0, 0, 0, 0)

            icon = QPushButton('')
            icon.setIcon(QIcon("assets/icon_forward.png"))

            text_container = QWidget()
            l = QVBoxLayout(text_container)
            l.setSpacing(0)
            l.addWidget(Text(config_list[config]['name']))
            l.addWidget(Text(relative_time(config_list[config]['last_updated']), 12))
            c.setStyleSheet(string('''  
                #config-parent {
                    border: 1px solid #d4d4d4;
                    border-radius: 5px;
                    background: #f7f7f7
                }
                
                #config-parent:hover {
                    background: #ebebeb;
                }
            '''))
            c.setFixedHeight(55)
            c.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

            hstack.addWidget(text_container)
            hstack.addStretch()
            hstack.addWidget(icon)
            self.layout.addWidget(c)

            c.clicked.connect(lambda: self.view_config_details(config_list[config]))
        
        if not config_list:
            t = Text("<i>No configs yet!<i>", 14)
            t.setStyleSheet(t.styleSheet()+'color: #707070;')
            self.layout.addWidget(t)

    def view_config_details(self, config_data):
        self.parent.change_page(3)
        self.parent.config_details.update_configs(config_data)

class ConfigDetails(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.setLayout(QVBoxLayout())
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.layout.setSpacing(0)
        self.update_configs(None)
        self.parent = parent

        self.update_configs(config_list['Test 1'])
        # self.run_config(config_list['caden'])

    def update_configs(self, data):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if data:
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.addWidget(QLabel(f'''Config "{data['name']}"'''))
            c1 = string('''
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
            ''')
            c2 = string('''
                background: #dbdbdb;
                border-radius: 5px;
                color: white;   
                text-align: center;
                padding: 5px;       
            ''')
            self.run_button = Button("Run Config", 100, c2 if is_running else c1)
            self.run_button.clicked.connect(lambda: self.run_config(data))
            
            self.delete_button = Button("Delete Config", 120, string('''
                QPushButton {
                    border: 1px solid #00A4CD;
                    border-radius: 5px;
                    color: #00A4CD;   
                    text-align: center;
                    padding: 5px;
                }
                QPushButton:hover {
                    border-color: #0083a3;
                    color: #0083a3;
                } '''))
            self.delete_button.clicked.connect(lambda: self.delete_config(data))

            header_layout.addWidget(self.run_button)
            header_layout.addWidget(self.delete_button)

            self.layout.addWidget(header)
            self.layout.addWidget(Text("View and run config here", 12))
            self.layout.addWidget(Spacer(20))

            self.layout.addWidget(QLabel("Config Settings"))
            self.layout.addWidget(Text("Data is in JSON format, do not edit unless you know what you're doing, entries are NOT checked for validity", 12))
            self.layout.addWidget(Spacer(10))
            self.edit = QTextEdit()
            self.edit.setStyleSheet(string('''
                QTextEdit {
                    font-size: 12px;
                    border: 1px solid #d4d4d4;
                }

                QTextEdit:focus {
                    border-color: #00A4CD;
                }
                               
            '''))
            self.edit.setPlainText(json.dumps(data, indent=4))
            self.edit.setFont(fira_code)
            self.edit.setLineWrapMode(QTextEdit.NoWrap)
            self.layout.addWidget(self.edit)

            button_row = QWidget()
            button_row_layout = QHBoxLayout(button_row)
            button_row_layout.setContentsMargins(0, 0, 0, 0)
            button_row_layout.setSpacing(10)

            save_button = Button("Save", 60, string('''
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
            save_button.clicked.connect(self.save_configs)

            reset_button = Button("Reset", 80, string('''
            QPushButton {
                border: 1px solid #00A4CD;
                border-radius: 5px;
                color: #00A4CD;   
                text-align: center;
                padding: 5px;
            }
            QPushButton:hover {
                border-color: #0083a3;
                color: #0083a3;
            } 
            '''))
            reset_button.clicked.connect(lambda: self.edit.setPlainText(json.dumps(data, indent=4)))

            self.layout.addWidget(Spacer(10))
            button_row_layout.addWidget(save_button)
            button_row_layout.addWidget(reset_button)
            for i in range(4): button_row_layout.addWidget(QLabel("")) # create manual spacer because the stupid spacer policy doesn't work

            self.layout.addWidget(button_row)

            spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.layout.addItem(spacer)

    def save_configs(self):
        try:
            data = json.loads(self.edit.toPlainText())
        except json.decoder.JSONDecodeError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f'Error: {e}')
            msg.setWindowTitle("Invalid Input")
            msg.exec_()
            return 
        config_list[data['name']] = data
        with open('multi_instance_client_data/config_list.json', 'w') as file:
            file.write(json.dumps(config_list, indent=2))
       
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Saved successfully")
        msg.setWindowTitle("Invalid Input")
        msg.exec_()

    def delete_confirmation(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirm Deletion")
        msg_box.setText("Are you sure?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg_box.exec_() == QMessageBox.Yes

    def delete_config(self, data):
        if self.delete_confirmation():
            del config_list[data['name']]
            with open('multi_instance_client_data/config_list.json', 'w') as file:
                file.write(json.dumps(config_list, indent=2))
            self.parent.home_page.configs.update_configs()
            self.parent.change_page(0)

    def run_config(self, data):
        global is_running
        if is_running: return

        is_running = True
        self.run_button.setStyleSheet(string('''
        QPushButton {
            background: #dbdbdb;
            border-radius: 5px;
            color: white;   
            text-align: center;
            padding: 5px;
        }
        '''))
        
        self.sub_window = InstanceManager(data, self)
        self.sub_window.show()
        self.sub_window.run() # test run

class InstanceManager(QMainWindow):
    def __init__(self, data, parent):
        super().__init__()
        self.data = data
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setWindowTitle(f'Instance Manager - {data["name"]}')    
        self.setMinimumSize(600, 300)
        self.resize(600, 300)
        self.parent = parent

        self.main = QWidget()
        self.setCentralWidget(self.main)
        self.layout = QVBoxLayout(self.main)

        self.terminal_container = QScrollArea()
        self.terminal_container.setWidgetResizable(True)
        self.terminal_container.setFixedHeight(200)

        self.terminal = QWidget()
        self.terminal_container.setWidget(self.terminal)
        self.setObjectName("terminal-container")
        self.terminal_layout = QVBoxLayout(self.terminal)
        self.terminal_container.setStyleSheet(string('''
            QLabel {
                font-size: 12px;
                background: black;
                color: white;
            }

            QWidget {
                background: black;
            }
                                                     
            QScrollArea {
                border: none;
            }

            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 5px;
                margin: 26px 0 26px 0;
            }

            QScrollBar::handle:vertical {
                background: rgb(72, 72, 72);
                min-height: 26px;
            }

            QScrollBar::add-line:vertical {
                background: transparent;
                height: 26px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::sub-line:vertical {
                background: transparent;
                height: 26px;
                subcontrol-position: top left;
                subcontrol-origin: margin;
                position: absolute;
            }

            QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
                width: 26px;
                height: 26px;
                background: transparent;
                image: url('./glass.png');
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        '''))
        self.terminal_layout.setSpacing(0)
        self.terminal_layout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.terminal_container)

        stop_button = Button("Stop Instances", 150, string('''
            QPushButton {
                background: #00A4CD;
                border-radius: 5px;
                color: white;   
                text-align: center;
                padding: 5px;
                font-size: 13px;
            }    
            QPushButton:hover {
                background: #0083a3;
            }                      
        '''))
        stop_button.clicked.connect(self.stop)
        self.layout.addWidget(stop_button)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)

    def closeEvent(self, event):
        global is_running
        is_running = False
        self.parent.update_configs(self.data)
        event.accept()

    def run(self):
        if 'bloxstrap_path' in settings:
            launch_path = settings['bloxstrap_path']
            self.logger = Logger(self.terminal_layout, fira_code)
            self.account_manager = AccountManager(self.data, self.logger, launch_path, screen_x, screen_y)
            self.logger.thread = self.account_manager
            self.logger.thread.message_signal.connect(self.logger.push_message)
            self.logger.thread.start()

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bloxstrap directory not set!")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.logger.push_message(f'Bloxstrap directory not set', error=True)
    
    def stop(self):
        self.account_manager.kill_all_accounts()

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

class CreateConfigList(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.update_configs()
        self.parent = parent
        self.is_running = False

    def update_configs(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for config in config_list:
            c = QPushButton()
            c.setObjectName("config-parent")
            hstack = QHBoxLayout(c)
            hstack.setContentsMargins(0, 0, 0, 0)

            icon = QPushButton('')
            icon.setIcon(QIcon("assets/icon_forward.png"))

            text_container = QWidget()
            l = QVBoxLayout(text_container)
            l.setSpacing(0)
            l.addWidget(Text(config_list[config]['name']))
            l.addWidget(Text(relative_time(config_list[config]['last_updated']), 12))
            c.setStyleSheet(string('''  
                #config-parent {
                    border: 1px solid #d4d4d4;
                    border-radius: 5px;
                    background: #f7f7f7
                }
                
                #config-parent:hover {
                    background: #ebebeb;
                }
            '''))
            c.setFixedHeight(55)
            c.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

            hstack.addWidget(text_container)
            hstack.addStretch()
            hstack.addWidget(icon)

            cd = copy.copy(config_list[config])
            self.layout.addWidget(c)
            c.clicked.connect(lambda _, cd=cd: self.view_config_details(cd))
        
        if not config_list:
            t = Text("<i>No configs yet!<i>", 14)
            t.setStyleSheet(t.styleSheet()+'color: #707070;')
            self.layout.addWidget(t)

    def view_config_details(self, data):
        self.parent.change_page(3)
        self.parent.config_details.update_configs(data)


class CreateHomePage(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.setLayout(QVBoxLayout())
        self.setWidget(self.container)
        self.setWidgetResizable(True)

        self.layout.addWidget(QLabel("My Configs"))

        self.configs = CreateConfigList(parent)
        self.layout.addWidget(self.configs)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)

class CreateSettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings"))

        self.config_bloxstrap = ConfigOption('Bloxstrap', 'Set Bloxstrap directory')
        self.config_bloxstrap.execute(string('''
            self.fb = FileButton()
            self.layout.addWidget(self.fb)
        ''').strip())

        layout.addWidget(self.config_bloxstrap)

        save_button = Button("Save", 80, string('''
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
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)

    def save_settings(self):
        dir_path = self.config_bloxstrap.fb.path
        if dir_path:
            if os.path.exists(dir_path):
                # app good
                settings['bloxstrap_path'] = dir_path
                with open('multi_instance_client_data/settings.json', 'w') as file:
                    file.write(json.dumps(settings, indent=2))

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Saved Successfully")
                msg.setWindowTitle("Success")
                msg.exec_()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Invalid directory")
                msg.setWindowTitle("Invalid")
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Invalid directory")
            msg.setWindowTitle("Invalid")
            msg.exec_()

class CreateConfigPage(QScrollArea):
    def __init__(self, parent):
        super().__init__()
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

        self.config_place = ConfigOption('Place ID', 'The ID of the Roblox game')
        self.config_place.execute(string('''
            self.input_place = QLineEdit(self)
            self.input_place.setFixedWidth(200)
            self.input_place.setStyleSheet('font-size: 12px')
            self.input_place.setValidator(QIntValidator())
            self.layout.addWidget(self.input_place)
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

        self.config_ui = ConfigOption('Disable UI', 'Disable all UI on instances')
        self.config_ui.execute(string('''
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
        layout.addWidget(self.config_place)
        layout.addWidget(self.config_vip)
        layout.addWidget(self.config_potato)
        layout.addWidget(self.config_ui)
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

        self.config_relaunch_delay = ConfigOption('Relaunch Delay', 'The time to wait after an instance fails to launch, leave empty for 10s')
        self.config_relaunch_delay.execute(string('''
            self.input_relaunch_delay = QLineEdit(self)
            self.input_relaunch_delay.setFixedWidth(50)
            self.input_relaunch_delay.setText('10')
            self.input_relaunch_delay.setValidator(QIntValidator(0, 9999))
            self.input_relaunch_delay.setStyleSheet('font-size: 12px')
            self.layout.addWidget(self.input_relaunch_delay)
        '''))

        layout.addWidget(self.config_delay)
        layout.addWidget(self.config_relaunch_delay)

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

        self.config_target = ConfigOption('Window Target', 'The coordinates at which the program clicks to prevent disconnection')
        self.config_target.execute(string('''
            self.input_x = QLineEdit(self)
            self.input_x.setFixedWidth(35)
            self.input_x.setText('200')
            self.input_x.setValidator(QIntValidator(0, 500))
            self.input_x.setStyleSheet('font-size: 12px')
                                          
            self.input_y = QLineEdit(self)
            self.input_y.setFixedWidth(35)
            self.input_y.setText('200')
            self.input_y.setValidator(QIntValidator(0, 500))
            self.input_y.setStyleSheet('font-size: 12px')
                                          
            self.layout.addWidget(Text('X: ', 12, width=10))
            self.layout.addWidget(self.input_x)
            self.layout.addWidget(Text('Y: ', 12, width=10))
            self.layout.addWidget(self.input_y)
        '''))

        layout.addWidget(self.config_stacking)
        layout.addWidget(self.config_x_offset)
        layout.addWidget(self.config_y_offset)
        layout.addWidget(self.config_target)

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
        global config_list
        errors = []


        config_name = self.config_name.input_name.text().strip()

        try: config_place = int(self.config_place.input_place.text().strip())
        except ValueError: config_place = None

        config_vip = self.config_vip.input_vip.text().strip()
        config_potato = self.config_potato.sc.isChecked()
        config_fps = int(self.config_fps.input_fps.text())
        config_ui = self.config_ui.sc.isChecked()
        config_delay = int(self.config_delay.input_delay.text())
        config_relaunch_delay = int(self.config_relaunch_delay.input_relaunch_delay.text())
        config_stacking = self.config_stacking.sc.isChecked()
        config_x_offset = int(self.config_x_offset.input_x_offset.text())
        config_y_offset = int(self.config_y_offset.input_y_offset.text())
        config_target_x = int(self.config_target.input_x.text())
        config_target_y = int(self.config_target.input_y.text())

        accounts = [row.get_row_data() for row in self.account_list.rows]
        accounts = [a for a in accounts if a['cookie']]

        if not config_name: errors.append('Invalid config name')
        if not config_place: errors.append('Invalid place id')
        if len(accounts) == 0: errors.append('Must add at least 1 user')
        for a in accounts:
            if not a['cookie'] or not a['username']:
                errors.append('Invalid username or cookie for user')
        if int(config_x_offset > 1000): errors.append('Invalid x offset (<= 1000)')
        if int(config_y_offset > 800): errors.append('Invalid y offset (<= 800)')
        if config_name in config_list: errors.append('Config already exists')
        if config_target_x > 500 or config_target_y > 500: errors.append('Invalid target range (0-500)')
    
        if errors:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('\n'.join(errors))
            msg.setWindowTitle("Invalid Input")
            msg.exec_()
        else:
            config_list[config_name] = {
                'name': config_name,
                'place_id': config_place,
                'vip': config_vip,
                'potato': config_potato,
                'ui': config_ui,
                'fps': config_fps,
                'delay': config_delay,
                'relaunch_delay': config_relaunch_delay,
                'stacking': config_stacking,
                'x_offset': config_x_offset,
                'y_offset': config_y_offset,
                'target_x': config_target_x,
                'target_y': config_target_y,
                'last_updated': time.time(),
                'accounts': accounts
            }
            with open('multi_instance_client_data/config_list.json', 'w') as file:
                file.write(json.dumps(config_list, indent=2))

            self.parent.change_page(0)
            self.parent.home_page.configs.update_configs() # force update to home page

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/icon.png"))  
        self.setWindowTitle("Multi Instance Manager")
        self.setMinimumSize(800, 400)
        self.resize(800, 400)
        # self.setWindowOpacity(0.9)
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
        self.home_page = CreateHomePage(self) # accessed by config page
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(CreateConfigPage(self))
        self.stacked_widget.addWidget(CreateSettingsPage())

        # pages for config details 3+
        self.config_details = ConfigDetails(self)
        self.stacked_widget.addWidget(self.config_details)

        self.layout.addLayout(self.nav_buttons)
        self.layout.addWidget(self.stacked_widget)
        
        self.change_page(3) #preview temporary

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, button in enumerate(self.buttons):
            if i == index:
                button.setStyleSheet('border-color: #00A4CD;')
            else:
                button.setStyleSheet('')
        if index >= 3:
            self.buttons[0].setStyleSheet('border-color: #00A4CD;')


is_running = False
space = '‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎'
app = QApplication(sys.argv)
font, fira_code = load_fonts()
screen_x = app.primaryScreen().size().width()
screen_y = app.primaryScreen().size().height()

# load client data
os.makedirs('multi_instance_client_data', exist_ok=True)
if not os.path.exists('multi_instance_client_data/config_list.json'):
    with open('multi_instance_client_data/config_list.json', 'w') as file:
        file.write(json.dumps({}))
if not os.path.exists('multi_instance_client_data/settings.json'):
    with open('multi_instance_client_data/settings.json', 'w') as file:
        file.write(json.dumps({}))

with open('multi_instance_client_data/config_list.json', 'r') as file:
    config_list = json.loads(file.read())
with open('multi_instance_client_data/settings.json', 'r') as file:
    settings = json.loads(file.read())

# initialize app
window = MainWindow()
window.show()
sys.exit(app.exec_())