REM docker rm --force devbasic
REM docker rmi debiangfx
REM docker build -t debiangfx .
REM docker run -itd --name devbasic -p 3350:3350 -p 3391:3391 debiangfx
REM docker network connect myNetwork devbasic
@echo off

set NetworkName="myNetwork"
set ContainerName="debiangfx"
set ImageName="devbasic"
set PortList=-p 3350:3350 -p 3391:3391
set Volumes=
set Variaveis=-itd

..\runbuild