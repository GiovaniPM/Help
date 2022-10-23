REM docker rm --force esearch
REM docker rmi esearchbasic
REM docker build -t esearchbasic .
REM docker run -d --name esearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" esearchbasic
REM docker network connect myNetwork esearch
@echo off

set NetworkName="myNetwork"
set ContainerName="esearch"
set ImageName="esearchbasic"
set PortList=-p 9200:9200 -p 9300:9300
set Volumes=
set Variaveis=-e "discovery.type=single-node"

..\runbuild