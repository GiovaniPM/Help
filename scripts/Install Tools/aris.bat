@echo off

wget --quiet --show-progress -O download.exe http://download.ariscommunity.com/aris-express-setup.exe
download.exe
del download.exe /Q