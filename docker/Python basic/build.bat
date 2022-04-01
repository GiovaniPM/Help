docker build -t pythonbasic .
docker run -d --name pythonserver pythonbasic
REM docker run -it --rm --name my-running-app my-python-app