@echo off

FOR /F "tokens=1,2,3,4 delims=/ " %%a IN ("%date%") DO set DateRun=%%c%%b%%a
FOR /F "tokens=1,2,3,4 delims=: " %%a IN ("%time%") DO set TimeRun=%%a%%b%%c%%d

set NetworkName="myNetwork"
set ContainerName="0mq"
set ImageName="0mqbasic"
set PortList=-p 5000:5000 -p 4444:4444

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
docker run -d --name %ContainerName% %PortList% -e BUILDED=%DateRun%%TimeRun% %ImageName%
docker network connect %NetworkName% %ContainerName%