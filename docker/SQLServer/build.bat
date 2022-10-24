REM docker rm --force sqlserver
REM docker rmi mssqlbasic
REM docker build -t mssqlbasic .
REM docker run -d --name sqlserver -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=Pm11092j#" -e "MSSQL_PID=Express" -p 1433:1433 -d mssqlbasic
REM docker network connect myNetwork sqlserver
@echo off

set NetworkName="myNetwork"
set ContainerName="sqlserver"
set ImageName="mssqlbasic"
set PortList=-p 1433:1433
set Volumes=
set Variaveis=-e "ACCEPT_EULA=Y" -e "SA_PASSWORD=Pm11092j#" -e "MSSQL_PID=Express"

..\runbuild