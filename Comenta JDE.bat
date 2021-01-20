@echo off
set SPACES=...............................................................................
set HEADER_COM=%USERNAME%/%COMPUTERNAME% - %DATE% %TIME% - Start %SPACES%
set TAIL_COM=%USERNAME%/%COMPUTERNAME% - %DATE% %TIME% - End %SPACES%
cls
echo %HEADER_COM:~0,66% > temporario.txt
echo ------------------------------------------------------------------- >> temporario.txt
echo Notes: >> temporario.txt
notepad temporario.txt
echo . >> temporario.txt
type temporario.txt | boxes -d jde
echo %TAIL_COM:~0,66% | boxes -d jde
del temporario.txt