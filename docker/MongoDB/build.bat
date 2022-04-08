docker rm --force MongoDB
docker rmi mongobasic
docker build -t mongobasic .
docker run -d --name MongoDB -p 27017:27017 mongobasic
docker network connect myNetwork MongoDB
REM docker network create myNetwork
REM docker network inspect myNetwork