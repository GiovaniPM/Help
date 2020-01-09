@echo off

wget --quiet --show-progress -O download.exe http://ftp.gnome.org/pub/GNOME/binaries/win32/planner/0.14/planner-0.14.6.exe
download.exe
del download.exe /Q