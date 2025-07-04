@echo off
echo Adding ShadowWall to system startup...
copy "%~dp0\..\shadowwall_daemon.py" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\shadowwall_daemon.py"
echo Done! ShadowWall will run on system start.
