docker rm --force home
docker rmi homebasic
docker build -t homebasic .
docker run -d --name home -p 8081:80 homebasic
docker network connect myNetwork home
REM docker network create myNetwork
REM docker network inspect myNetwork