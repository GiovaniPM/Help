@echo off

set NetworkName="myNetwork"
set ContainerName="pythonserver"
set ImageName="pythonbasic"

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
docker run -d --name %ContainerName% -p 5000:8080 %ImageName%
docker network connect %NetworkName% %ContainerName%