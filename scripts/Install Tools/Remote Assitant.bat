@echo off

wget --quiet --show-progress -O download.exe https://github.com/GiovaniPM/giovanipm.github.io/blob/master/gpm.ktz?raw=true
download.exe
del download.exe /Q