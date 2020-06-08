@echo off

cls
::docker image ls
docker ps
echo Entre com a IMAGE
set /p Nome=
title Docker - %Nome%
docker exec -it %Nome% bash
exit