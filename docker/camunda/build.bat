docker rm --force camunda
docker rmi camundabasic
docker build -t camundabasic .
docker run -d --name camunda -p 8080:8080 camundabasic
docker network connect myNetwork camunda
REM docker network create myNetwork
REM docker network inspect myNetwork