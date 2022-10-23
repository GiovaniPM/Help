@echo off

set NetworkName="myNetwork"
set ContainerName="camunda"
set ImageName="camundabasic"
set PortList=-p 8000:8000 -p 8080:8080 -p 9404:9404
set Volumes=
set Variaveis=

..\runbuild