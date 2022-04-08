docker rm --force oraclexe
docker rmi oraclebasic
docker build -t oraclebasic .
docker run -d --name oraclexe -p 1541:1541 -p 1521:1521 -p 5500:5500 oraclebasic
docker network connect myNetwork oraclexe
REM docker network create myNetwork
REM docker network inspect myNetwork