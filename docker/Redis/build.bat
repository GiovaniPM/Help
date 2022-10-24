REM docker rm --force redis
REM docker rmi redisbasic
REM docker build -t redisbasic .
REM docker run -d --name redis -p 6379:6379 redisbasic
REM docker network connect myNetwork redis
@echo off

set NetworkName="myNetwork"
set ContainerName="redis"
set ImageName="redisbasic"
set PortList=-p 6379:6379
set Volumes=
set Variaveis=

..\runbuild