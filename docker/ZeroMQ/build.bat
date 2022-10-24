@echo off

set NetworkName="myNetwork"
set ContainerName="0mq"
set ImageName="0mqbasic"
set PortList=-p 5000:5000 -p 4444:4444
set Volumes=
set Variaveis=

..\runbuild