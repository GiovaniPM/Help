docker rm --force windows95
docker rmi toolboc/windows95
docker build -t toolboc/windows95 .
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd --name windows95 toolboc/windows95
docker network connect myNetwork windows95
REM docker network create myNetwork
REM docker network inspect myNetworkShow