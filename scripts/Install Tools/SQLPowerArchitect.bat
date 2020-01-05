@echo off

wget --quiet --show-progress -O download.jar http://www.bestofbi.com/downloads/architect/1.0.8/SQL-Power-Architect-Setup-Windows-jdbc-1.0.8.jar
download.jar
del download.jar /Q