@echo off
rem =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
rem Created by Giovani Perotto Mesquita
rem =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

if "%1"=="" goto error

type %1 | findstr /C:"SELECT " /C:"UPDATE " /C:"DELETE " /C:"INSERT " > temp.txt
type temp.txt
del temp.txt
goto fim

:error
echo Procura comandos SQL em log do JDE.
echo Ex:
echo    findsql file

:fim