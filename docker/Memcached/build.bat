REM docker rm --force memcached
REM docker rmi memcachedbasic
REM docker build -t memcachedbasic .
REM docker run -d --name memcached -p 11211:11211 memcachedbasic
REM docker network connect myNetwork memcached
@echo off

set NetworkName="myNetwork"
set ContainerName="memcached"
set ImageName="memcachedbasic"
set PortList=-p 11211:11211
set Volumes=
set Variaveis=

..\runbuild