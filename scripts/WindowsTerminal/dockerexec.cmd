@echo off

:Menu
cls
docker ps --format "table{{.Names}}\t{{.ID}}\t{{.Image}}\t{{.RunningFor}}\t{{.Status}}"
echo Entre com a IMAGE NAME (deixe branco para sair)
set /p Nome=

if [%Nome%]==[] goto Sair

title Docker - Shell %Nome%
cls
docker exec -it %Nome% bash
set Nome=
goto Menu

:Sair
exit /b