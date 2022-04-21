docker rm --force memcached
docker rmi memcachedbasic
docker build -t memcachedbasic .
docker run -d --name memcached -p 11211:11211 memcachedbasic
docker network connect myNetwork memcached
REM docker network create myNetwork
REM docker network inspect myNetworkShow