docker build -t pythonbasic .
docker run -d --name pythonserver -p 5000:8080 pythonbasic
REM docker run -it --rm --name my-running-app my-python-app