FROM debian:8
RUN apt-get update && apt-get install -y python3 python3-pip curl
RUN curl -sSL https://raw.githubusercontent.com/GiovaniPM/flaskAPI/master/dv.py > dv.py
RUN mkdir /dv
COPY requirements.txt /dv/requirements.txt
RUN cp dv.py /dv/dv.py
RUN rm dv.py
RUN cd dv && /usr/bin/pip3 install -r requirements.txt
EXPOSE 8080
CMD ["/usr/bin/python3", "dv/dv.py"]