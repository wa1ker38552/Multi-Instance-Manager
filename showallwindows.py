from ahk import AHK

ahk = AHK(executable_path=r'C:\Program Files\AutoHotkey\AutoHotkey.exe')

active_windows = []
for window in ahk.list_windows():
    if window.title == 'Roblox' or 'MultiManager' in window.title:
        active_windows.append(window)

for win in active_windows:
    win.show()