docker rm --force mariadb
docker rmi mariadbbasic
docker build -t mariadbbasic .
docker run -d --name mariadb -p 3306:3306 --env MARIADB_USER=giovanipm --env MARIADB_PASSWORD=pm11092j --env MARIADB_ROOT_PASSWORD=pm11092j mariadbbasic
docker network connect myNetwork mariadb
REM docker network create myNetwork
REM docker network inspect myNetworkShow