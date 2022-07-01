docker rm --force rabbitmq
docker rmi rabbitmqbasic
docker build -t rabbitmqbasic .
docker run -d --name rabbitmq -p 15671:15671 rabbitmqbasic
docker network connect myNetwork rabbitmq
REM docker network create myNetwork
REM docker network inspect myNetwork