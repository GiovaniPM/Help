@echo off

FOR /F "tokens=1,2,3,4 delims=/ " %%a IN ("%date%") DO set DateRun=%%c%%b%%a
FOR /F "tokens=1,2,3,4 delims=: " %%a IN ("%time%") DO set TimeRun=%%a%%b%%c%%d

echo Builded  %DateRun%%TimeRun%
echo Contaner %ContainerName%
echo Image    %ImageName%
echo Network  %NetworkName%
echo Ports    %PortList%
echo Volumes  %Volumes%

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