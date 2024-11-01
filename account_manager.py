from threading import Thread
from PyQt5.QtCore import *
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

    def launch_instance(self, vip, retries, offset, place_id):
        self.offset = offset
        self.retries = retries
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
        Thread(target=self.launch).start()

    def launch(self):
        self.logger.push_message(f'Launched {self.username}')
        self.pid = os.system(f'{self.launcher_path} "{self.launch_url}"')
        
    def kill(self):
        os.kill(self.pid, signal.SIGTERM)

class AccountManager(QThread):
    message_signal = pyqtSignal(str)

    def __init__(self, data, logger, launcher_path):
        super().__init__()

        if not os.path.exists(f'{launcher_path}/Roblox/Player/RobloxPlayerBeta.exe'):
            self.logger.push_message(f'Unable to locate RobloxPlayerBeta.exe', error=True)
        else:
            self.launcher_path = f'{launcher_path}/Roblox/Player/RobloxPlayerBeta.exe'

        self.name = data['name']
        self.place_id = data['place_id']
        self.vip = data['vip']
        self.potato = data['potato']
        self.ui = data['ui']
        self.fps = data['fps']
        self.delay = data['delay']
        self.retries = data['retries']
        self.offset = (data['x_offset'], data['y_offset'])
        self.target = (data['target_x'], data['target_y'])
        self.accounts = [Account(account, logger, self.launcher_path) for account in data['accounts']]

    def create_singleton_mutex(self):
        self.message_signal.emit('Created Roblox_singletonMutex')
        # logic to break singleton mutex later :P
        while True:
            mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "ROBLOX_singletonMutex")
            time.sleep(1)

    def run(self):
        Thread(target=self.create_singleton_mutex).start()
        self.launch_all_accounts()

    def launch_all_accounts(self):
        for account in self.accounts:
            self.message_signal.emit(f'Launching {account.username}')
            account.launch_instance(self.vip, self.retries, self.offset, self.place_id)
            time.sleep(self.delay)