docker rm --force db2
docker rmi db2basic
docker build -t db2basic .
docker run -d --name db2 -p 22:22 -p 50000:50000 -p 55000:55000 -p 60006:60006 -p 60007:60007 -e LICENSE=accept -e DB2INST1_PASSWORD=pm11092j -e DBNAME=testdb db2basic
docker network connect myNetwork db2
REM docker network create myNetwork
REM docker network inspect myNetworkShow