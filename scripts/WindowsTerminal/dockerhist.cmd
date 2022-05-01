@echo off

:Menu
cls
::docker image ls
docker ps -a --format "table{{.Image}}\t{{.RunningFor}}\t{{.Status}}"
echo Entre com a IMAGE NAME (deixe branco para sair)
set /p Nome=

if [%Nome%]==[] goto Sair

title Docker - Logs %Nome%
docker history %Nome% --format "{{.CreatedBy}}" --no-trunc
pause
set Nome=
goto Menu

:Sair
exit /b