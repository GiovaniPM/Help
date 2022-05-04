@echo off

cls
for  /f "tokens=*" %%G IN ('docker ps -aq') do (
    docker inspect --format "{{.Name}} - {{.NetworkSettings.IPAddress}}" %%G
)