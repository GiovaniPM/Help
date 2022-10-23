@echo off

FOR /F "tokens=1,2,3,4 delims=/ " %%a IN ("%date%") DO set DateRun=%%c%%b%%a
FOR /F "tokens=1,2,3,4 delims=: " %%a IN ("%time%") DO set TimeRun=%%a%%b%%c%%d

set NetworkName="myNetwork"
set ContainerName="oraclexe"
set ImageName="oraclebasic"
set PortList=-p 1541:1541 -p 1521:1521 -p 5500:5500
set Volumes=-v dadosxe:/opt/oracle/oradata

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
docker run -d --name %ContainerName% %PortList% -e BUILDED=%DateRun%%TimeRun% %Volumes% %ImageName%
docker network connect %NetworkName% %ContainerName%
docker network inspect %NetworkName%