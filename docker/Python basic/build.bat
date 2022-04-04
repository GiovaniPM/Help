docker build -t pythonbasic .
docker run -d --name pythonserver -p 5000:8080 pythonbasic
docker network connect myNetwork pythonserver
REM docker network create myNetwork
REM docker network inspect myNetwork