@echo off

cls
docker image ls
echo Entre com o REPOSITORY
set /p Nome=
title Docker - %Nome%
docker exec -it %Nome% bash
exit