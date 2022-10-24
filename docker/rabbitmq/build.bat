@echo off

set NetworkName="myNetwork"
set ContainerName="rabbitmq"
set ImageName="rabbitmqimg"
set PortList=-p 15671:15671
set Volumes=
set Variaveis=

..\runbuild