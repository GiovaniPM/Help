docker rm --force firebird
docker rmi firebirdbasic
docker build -t firebirdbasic .
docker run -d --name firebird -p 3050:3050 -p 3051:3051 firebirdbasic
docker network connect myNetwork firebird
REM docker network create myNetwork
REM docker network inspect myNetworkShow