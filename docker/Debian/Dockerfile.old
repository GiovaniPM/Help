FROM debian
LABEL version="1.0.0" description="Linux with RDP console" maintainer="Giovani Mesquita<giovanipm@gmail.com>"
#Debian Update
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y apt-utils
RUN apt-get install -y sudo
#RDP Graphical Interface on port 3391
RUN apt-get purge xrdp
RUN apt install -y xrdp
RUN apt install -y xfce4
RUN apt install -y xfce4-goodies
RUN cp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.bak
RUN sed -i 's/3389/3391/g' /etc/xrdp/xrdp.ini
RUN sed -i 's/max_bpp=32/#max_bpp=32\nmax_bpp=128/g' /etc/xrdp/xrdp.ini
RUN sed -i 's/xserverbpp=24/#xserverbpp=24\nxserverbpp=128/g' /etc/xrdp/xrdp.ini
RUN echo 'xfce4-session' > ~/.xsession
RUN sed -i 's/test -x/#test -x/g' /etc/xrdp/startwm.sh
RUN sed -i 's/exec/#exec/g' /etc/xrdp/startwm.sh
RUN echo '#xfce' >> /etc/xrdp/startwm.sh
RUN echo 'startxfce4' >> /etc/xrdp/startwm.sh
RUN echo '#!/bin/bash' > /root/startdgfx.sh
RUN echo '/etc/init.d/xrdp stop' >> /root/startdgfx.sh
RUN echo 'rm /var/run/xrdp/xrdp.pid' >> /root/startdgfx.sh
RUN echo '/etc/init.d/xrdp start' >> /root/startdgfx.sh
RUN echo 'bash' >> /root/startdgfx.sh
RUN chmod 777 /root/startdgfx.sh
#Install Others Packages
RUN apt-get install -y synaptic
RUN apt-get install -y gdebi
RUN apt-get install -y git
RUN apt-get install -y fpc
RUN apt-get install -y wget
RUN apt-get install -y vim
#Oracle Client 19.8.0.0
RUN mkdir /downloads
RUN curl --progress-bar 'https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip?xd_co_f=fae07a5a-ae5f-4c1a-8ce0-f41ed4a394c5' -o /downloads/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip
RUN curl --progress-bar 'https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip' -o /downloads/instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip
RUN mkdir /opt/oracle
RUN cd /downloads
RUN unzip /downloads/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip -d /opt/oracle
RUN unzip /downloads/instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip -d /opt/oracle/
RUN echo 'export PATH="$PATH:/opt/oracle/instantclient_19_8"' >> ~/.bashrc
RUN echo 'export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/oracle/instantclient_19_8"' >> ~/.bashrc
#Install scripts
COPY CodeTyphonIns.zip /downloads
RUN unzip /downloads/CodeTyphonIns.zip -d /downloads
EXPOSE 3391 3350
CMD ["/root/startdgfx.sh"]