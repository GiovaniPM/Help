docker rm --force esearch
docker rmi esearchbasic
docker build -t esearchbasic .
docker run -d --name esearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" esearchbasic
docker network connect myNetwork esearch
REM docker network create myNetwork
REM docker network inspect myNetworkShow