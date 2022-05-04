@echo off

:Menu
cls
docker ps -a --format "table{{.Image}}\t{{.RunningFor}}\t{{.Status}}"
echo Entre com a IMAGE NAME (deixe branco para sair)
set /p Nome=

if [%Nome%]==[] goto Sair

title Docker - History %Nome%
cls
docker history %Nome% --format "{{.CreatedBy}}" --no-trunc
pause
set Nome=
goto Menu

:Sair
exit /b