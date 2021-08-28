@echo off
cd /D D:/PythonProjects/MyKiwoom
python login/versionupdater.py
timeout 5
python login/autologin2.py
timeout 5
python tick/window.py
timeout 5
python day/updater_short.py
timeout 5
python day/updater_mid.py
timeout 5
python day/updater_long.py
timeout 5
python tick/backtester_tick.py
shutdown /s /t 60