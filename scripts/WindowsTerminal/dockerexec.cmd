@echo off

:Menu
cls
::docker image ls
docker ps
echo Entre com a IMAGE (deixe branco para sair)
set /p Nome=

if [%Nome%]==[] goto Sair

title Docker - %Nome%
docker exec -it %Nome% bash
set Nome=
goto Menu

:Sair
exit /b