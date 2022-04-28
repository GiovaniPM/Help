docker rm --force pythonwin
docker rmi pythonbasic2
docker build -t pythonbasic2 .
docker run -d --name pythonwin -p 5000:8080 pythonbasic2
docker network connect myNetwork pythonwin
REM docker network create myNetwork
REM docker network inspect myNetwork