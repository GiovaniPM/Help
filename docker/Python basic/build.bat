@echo off

set NetworkName="myNetwork"
set ContainerName="pythonserver"
set ImageName="pythonbasic"
set PortList=-p 5000:8080
set Volumes=

..\runbuild