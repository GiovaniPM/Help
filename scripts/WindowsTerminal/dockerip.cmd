@echo off

cls
for  /f "tokens=*" %%G IN ('docker ps -aq') do (
    REM table{{.Names}}\t{{.ID}}\t{{.Image}}\t{{.RunningFor}}\t{{.Status}}"
    docker inspect --format "{{.Name}} - {{.NetworkSettings.IPAddress}}" %%G
)