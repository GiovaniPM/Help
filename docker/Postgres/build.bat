docker rm --force PostgresDB
docker rmi postgresbasic
docker build -t postgresbasic .
docker run -d --name PostgresDB  -e POSTGRES_PASSWORD=pm11092j -p 5432:5432 postgresbasic
docker network connect myNetwork PostgresDB
REM docker network create myNetwork
REM docker network inspect myNetwork