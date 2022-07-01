@echo off

set NetworkName="myNetwork"
set ContainerName="rabbitmq"
set ImageName="rabbitmqimg"

docker network inspect %NetworkName%> nul
IF "%ERRORLEVEL%" == "0" (goto CreatedNET)
docker network create %NetworkName%
echo Network %NetworkName% created!
goto CreateIMG

:CreatedNET
echo Network %NetworkName% found!
goto CreateIMG

:CreateIMG
docker rm --force %ContainerName%
docker rmi %ImageName%
docker build -t %ImageName% .
docker run -d --name %ContainerName% -p 15671:15671 %ImageName%
docker network connect %NetworkName% %ContainerName%