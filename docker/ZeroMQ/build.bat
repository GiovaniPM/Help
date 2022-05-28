docker rm --force 0mq
docker rmi 0mqbasic
docker build -t 0mqbasic .
docker run -d --name 0mq -p 5000:5000 -p 4444:4444 0mqbasic
docker network connect myNetwork 0mq
REM docker network create myNetwork
REM docker network inspect myNetworkShow