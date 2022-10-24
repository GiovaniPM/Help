REM docker rm --force windows95
REM docker rmi toolboc/windows95
REM docker build -t toolboc/windows95 .
REM docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd --name windows95 toolboc/windows95
REM docker network connect myNetwork windows95
@echo off

set NetworkName="myNetwork"
set ContainerName="windows95"
set ImageName="toolboc/windows95"
set PortList=
set Volumes=-v /tmp/.X11-unix:/tmp/.X11-unix
set Variaveis=-e DISPLAY=unix$DISPLAY --device /dev/snd

..\runbuild