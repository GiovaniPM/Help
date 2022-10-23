REM docker rm --force db2
REM docker rmi db2basic
REM docker build -t db2basic .
REM docker run -itd --name db2 --privileged=true -p 22:22 -p 50000:50000 -p 55000:55000 -p 60006:60006 -p 60007:60007 -e LICENSE=accept -e DB2INST1_PASSWORD=pm11092j -e DBNAME=testdb -v dadosdb2:/database db2basic
REM docker network connect myNetwork db2
@echo off

set NetworkName="myNetwork"
set ContainerName="db2"
set ImageName="db2basic"
set PortList=-p 22:22 -p 50000:50000 -p 55000:55000 -p 60006:60006 -p 60007:60007
set Volumes=-v dadosdb2:/database
set Variaveis=-itd --privileged=true -e LICENSE=accept -e DB2INST1_PASSWORD=pm11092j -e DBNAME=testdb

..\runbuild