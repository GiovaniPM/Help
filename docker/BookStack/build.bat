@echo off

set NetworkName="myNetwork"
set ContainerName="bookstackerver"
set ImageName="bookstacbasic"
set PortList=-p 6875:80
rem set Volumes=-v /var/run/docker.sock:/var/run/docker.sock
set Volumes=
rem set Variaveis=-e PUID=1000 -e PGID=1000 -e APP_URL= -e DB_HOST=<yourdbhost> -e DB_USER=<yourdbuser> -e DB_PASS=<yourdbpass> -e DB_DATABASE=bookstackapp --restart unless-stopped
rem set Variaveis=-e PUID=1000 -e PGID=1000 --restart unless-stopped
set Variaveis=

..\runbuild