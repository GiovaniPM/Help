FROM debian:8
RUN apt-get update && apt-get install -y python python-pip curl
RUN curl -sSL https://github.com/shekhargulati/python-flask-docker-hello-world/archive/master.tar.gz | tar -xzv
RUN cd python-flask-docker-hello-world-master && /usr/bin/pip install -r requirements.txt
EXPOSE 5000
CMD ["/usr/bin/python", "python-flask-docker-hello-world-master/app.py"]