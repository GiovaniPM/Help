@echo off

:Menu
cls
::docker image ls
docker ps -a --format "table{{.Names}}\t{{.ID}}\t{{.Image}}\t{{.RunningFor}}\t{{.Status}}"
echo Entre com a IMAGE NAME (deixe branco para sair)
set /p Nome=

if [%Nome%]==[] goto Sair

title Docker - Logs %Nome%
docker logs %Nome%
pause
set Nome=
goto Menu

:Sair
exit /b