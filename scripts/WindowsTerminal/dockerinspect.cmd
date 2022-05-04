@echo off

:Menu
cls
docker ps -a --format "table{{.Image}}\t{{.RunningFor}}\t{{.Status}}"
echo Entre com a IMAGE NAME (deixe branco para sair)
set /p Nome=

if [%Nome%]==[] goto Sair

title Docker - Inspect %Nome%
cls
docker image inspect %Nome%
pause
set Nome=
goto Menu

:Sair
exit /b