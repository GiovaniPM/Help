REM docker rm --force PostgresDB
REM docker rmi postgresbasic
REM docker build -t postgresbasic .
REM docker run -d --name PostgresDB  -e POSTGRES_PASSWORD=pm11092j -p 5432:5432 postgresbasic
REM docker network connect myNetwork PostgresDB
@echo off

set NetworkName="myNetwork"
set ContainerName="PostgresDB"
set ImageName="postgresbasic"
set PortList=-p 5432:5432
set Volumes=
set Variaveis=-e POSTGRES_PASSWORD=pm11092j

..\runbuild