docker rm --force devbasic
docker rmi debiangfx
docker build -t debiangfx .
docker run -itd --name devbasic -p 3350:3350 -p 3391:3391 debiangfx
docker network connect myNetwork devbasic
REM docker network create myNetwork
REM docker network inspect myNetworkShow

rem docker build --tag=debiangfx .
rem docker run -it --name="dgfx" -p 3350:3350 -p 3391:3391 debiangfx