FROM debian
LABEL version="1.0.0" description="Linux with RDP console" maintainer="Giovani Mesquita<giovanipm@gmail.com>"
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y apt-utils
RUN apt-get install -y sudo
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
RUN apt-get install -y synaptic
RUN apt-get install -y gdebi
RUN apt-get install -y git
EXPOSE 3391 3350
CMD ["/root/startdgfx.sh"]