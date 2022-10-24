REM docker rm --force MongoDB
REM docker rmi mongobasic
REM docker build -t mongobasic .
REM docker run -d --name MongoDB -p 27017:27017 mongobasic
REM docker network connect myNetwork MongoDB
@echo off

set NetworkName="myNetwork"
set ContainerName="MongoDB"
set ImageName="mongobasic"
set PortList=-p 27017:27017
set Volumes=
set Variaveis=

..\runbuild