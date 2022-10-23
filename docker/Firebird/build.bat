REM docker rm --force firebird
REM docker rmi firebirdbasic
REM docker build -t firebirdbasic .
REM docker run -d --name firebird -p 3050:3050 -p 3051:3051 firebirdbasic
REM docker network connect myNetwork firebird
@echo off

set NetworkName="myNetwork"
set ContainerName="firebird"
set ImageName="firebirdbasic"
set PortList=-p 3050:3050 -p 3051:3051
set Volumes=
set Variaveis=

..\runbuild