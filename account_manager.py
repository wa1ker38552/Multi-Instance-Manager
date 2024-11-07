from threading import Thread
from PyQt5.QtCore import *
from ahk import AHK
import subprocess
import requests
import urllib
import ctypes
import random
import signal
import time
import os

endpoints = ['https://roblox.com/catalog']

class Account:
    def __init__(self, data, logger, launcher_path):
        self.logger = logger
        self.launcher_path = launcher_path
        self.username = data['username']
        self.vip = data['vip']
        self.cookie = data['cookie']
        self.session = requests.Session()
        self.session.headers['Referer'] = 'https://www.roblox.com/'
        self.session.headers['Content-Type'] = 'application/json'
        self.session.cookies.set('.ROBLOSECURITY', data['cookie'])
        self.get_xcsrf_token()
        self.get_auth_ticket()
        self.launched = False

    def get_xcsrf_token(self):
        obtained_token = False
        while not obtained_token:
            try:
                self.session.headers['X-CSRF-TOKEN'] = self.session.post(random.choice(endpoints)).headers['x-csrf-token']
                obtained_token = True
            except Exception as e:
                self.logger.push_message(f'Failed to obtain x-csrf token for {self.username}, {e}, retrying in 5s...', error=True)
                time.sleep(5)
        self.logger.push_message(f'Obtained x-csrf-token-for {self.username}')

    def get_auth_ticket(self):
        obtained_ticket = False
        while not obtained_ticket:
            try:
                self.auth_ticket = self.session.post('https://auth.roblox.com/v1/authentication-ticket').headers['rbx-authentication-ticket']
                obtained_ticket = True
            except Exception as e:
                self.logger.push_message(f'Failed to obtain auth ticket for {self.username}, {e}, retrying in 5s...', error=True)
                time.sleep(5)
        self.logger.push_message(f'Obtained auth ticket for {self.username}')

    def launch_instance(self, vip, place_id):
        self.place_id = place_id

        # vip server set, pioritize self.vip
        if self.vip or vip:
            if self.vip:
                access_code = self.vip.split('privateServerLinkCode=')[1]
            else:
                access_code = vip.split('privateServerLinkCode=')[1]
            self.launch_url = f"roblox-player:1+launchmode:play+gameinfo:{self.auth_ticket}+launchtime:{int(time.time() * 1000)}+placelauncherurl:{urllib.parse.quote(f'https://www.roblox.com/Game/PlaceLauncher.ashx?request=RequestPrivateGame&browserTrackerId={random.randint(100000000, 9999999999999)}&placeId={self.place_id}')}&linkCode={access_code}"
        else:
            self.launch_url = f"roblox-player:1+launchmode:play+gameinfo:{self.auth_ticket}+launchtime:{int(time.time() * 1000)}+placelauncherurl:{urllib.parse.quote(f'https://www.roblox.com/Game/PlaceLauncher.ashx?request=RequestGame&browserTrackerId={random.randint(100000000, 9999999999999)}&placeId={self.place_id}')}"
            
        # launch url created
        window_count = len(AccountManager.get_roblox_windows())
        Thread(target=self.launch).start()
        timeout_count = 0

        while len(AccountManager.get_roblox_windows()) == window_count:
            time.sleep(0.1)
            timeout_count += 0.1
            if timeout_count > 10:
                self.logger.push_message(f'Launching {self.username} timed out. Retrying...', error=True)
                try:
                    Thread(target=self.launch).start()
                except:
                    self.logger.push_message(f'Failed to re-launch {self.username}. Retrying...', error=True)
                    time.sleep(AccountManager.relaunch_delay)
                timeout_count = 0

        # logic to delay opening if vip server (assume there's nobody in the vip server)
        if (vip or self.vip) and len(AccountManager.window_ids) == 0:
            time.sleep(10)
        else:
            time.sleep(AccountManager.delay) # delay for roblox to open secondary frame
        
        for win in AccountManager.get_roblox_windows():
            if not win.id in AccountManager.window_ids:
                win.title = f'MultiInstance - {self.username}'
                win.move(x=AccountManager.window_x, y=AccountManager.window_y, width=500, height=500)
                if not AccountManager.stacking:
                    if AccountManager.window_x > AccountManager.screen[0]:
                        AccountManager.window_x = 0
                        AccountManager.window_y += AccountManager.offset[1]
                    else:
                        AccountManager.window_x += AccountManager.offset[0]
                else:
                    AccountManager.window_x += 25
                    AccountManager.window_y += 25
                AccountManager.window_ids.append(win.id)
                self.launched = True

    def launch(self):
        self.logger.push_message(f'Launched {self.username}')
        process = subprocess.Popen([self.launcher_path, self.launch_url])
        self.pid = process.pid
        
    def kill(self):
        try:
            os.kill(self.pid, signal.SIGTERM)
        except OSError:
            self.logger.push_message(f'Failed to kill {self.pid}', error=True)

class AccountManager(QThread):
    message_signal = pyqtSignal(str)
    ahk = AHK(executable_path=r'C:\Program Files\AutoHotkey\AutoHotkey.exe')
    window_ids: list[int] = []
    window_x: int = 0
    window_y: int = 0
    screen = (0, 0)

    # global settings
    potato = None
    ui = None
    delay = None
    relaunch_delay = None
    offset = None
    stacking = None
    

    def __init__(self, data, logger, launcher_path, scx, scy):
        super().__init__()

        if not os.path.exists(f'{launcher_path}/Roblox/Player/RobloxPlayerBeta.exe'):
            self.logger.push_message(f'Unable to locate RobloxPlayerBeta.exe', error=True)
        else:
            self.launcher_path = f'{launcher_path}/Roblox/Player/RobloxPlayerBeta.exe'

        self.name = data['name']
        self.place_id = data['place_id']
        self.vip = data['vip']
        AccountManager.potato = data['potato']
        AccountManager.ui = data['ui']
        AccountManager.delay = data['delay']
        AccountManager.relaunch_delay = data['relaunch_delay']
        AccountManager.offset = (data['x_offset'], data['y_offset'])
        AccountManager.stacking = data['stacking']

        self.target = (data['target_x'], data['target_y'])
        self.accounts = [Account(account, logger, self.launcher_path) for account in data['accounts']]
        self.running = True
        AccountManager.screen = (scx, scy)

    def create_singleton_mutex(self):
        self.message_signal.emit('Created Roblox_singletonMutex')
        while self.running:
            mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "ROBLOX_singletonMutex")
            time.sleep(1)

    def run(self):
        Thread(target=self.create_singleton_mutex).start()
        self.launch_all_accounts()

    def launch_all_accounts(self):
        for account in self.accounts: # TRMEP CHNGE
            self.message_signal.emit(f'Launching {account.username}')
            account.launch_instance(self.vip, self.place_id)
            # time.sleep(self.delay)

    def kill_all_accounts(self):
        for account in self.accounts:
            account.kill()
        self.running = False
        self.message_signal.emit('Killed all accounts successfully')

    @staticmethod
    def get_roblox_windows():
        active_windows = []
        for window in AccountManager.ahk.list_windows():
            if window.title == 'Roblox' or 'MultiInstance' in window.title:
                active_windows.append(window)
        return active_windows 