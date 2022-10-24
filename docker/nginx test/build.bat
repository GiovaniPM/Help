REM docker rm --force home
REM docker rmi homebasic
REM docker build -t homebasic .
REM docker run -d --name home -p 8081:80 homebasic
REM docker network connect myNetwork home
@echo off

set NetworkName="myNetwork"
set ContainerName="home"
set ImageName="homebasic"
set PortList=-p 8081:80
set Volumes=
set Variaveis=

..\runbuild