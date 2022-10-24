REM docker rm --force mariadb
REM docker rmi mariadbbasic
REM docker build -t mariadbbasic .
REM docker run -d --name mariadb -p 3306:3306 --env MARIADB_USER=giovanipm --env MARIADB_PASSWORD=pm11092j --env MARIADB_ROOT_PASSWORD=pm11092j mariadbbasic
REM docker network connect myNetwork mariadb
@echo off

set NetworkName="myNetwork"
set ContainerName="mariadb"
set ImageName="mariadbbasic"
set PortList=-p 3306:3306
set Volumes=
set Variaveis=--env MARIADB_USER=giovanipm --env MARIADB_PASSWORD=pm11092j --env MARIADB_ROOT_PASSWORD=pm11092j

..\runbuild