docker rm --force redis
docker rmi redisbasic
docker build -t redisbasic .
docker run -d --name redis -p 6379:6379 redisbasic
docker network connect myNetwork redis
REM docker network create myNetwork
REM docker network inspect myNetworkShow