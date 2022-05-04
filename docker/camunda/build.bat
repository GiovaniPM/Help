docker rm --force camunda
docker rmi camundabasic
docker build -t camundabasic .
docker run -d --name camunda -p 8000:8000 -p 8080:8080 -p 9404:9404 camundabasic
docker network connect myNetwork camunda
REM docker network create myNetwork
REM docker network inspect myNetwork