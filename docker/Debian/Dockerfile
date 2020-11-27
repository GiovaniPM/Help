####################################################################################################
# Dockerfile to create a environment to developent
# -------------------------------------------------------------------------------------------------
# Author: Giovani Perotto Mesquuita<giovanipm@gmail.com>
# Date: 27/11/2020
# -------------------------------------------------------------------------------------------------
# Know Issues:
# - Synaptic does not work, show message no such file (to be evaluate)
# Next steps:
# - Automate user creation (to be evaluate);
# - Add VSCode;
# - Add Eclipse
####################################################################################################

FROM debian

# Labels
# ------
LABEL version="1.0.0" \
      description="Linux with RDP console for development" \
      maintainer="Giovani Mesquita<giovanipm@gmail.com>"                 

# Environment variables required for this build (do NOT change)
# -------------------------------------------------------------
ENV ORACLE_BASE=/opt/oracle \
    ORACLE_HOME=/opt/oracle/product/19c/dbhome_1 \ 
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/oracle/instantclient_19_8" \
    PATH="$PATH:/opt/oracle/instantclient_19_8" \
    ORA_SITE_CLIENT="https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip?xd_co_f=fae07a5a-ae5f-4c1a-8ce0-f41ed4a394c5'" \
    ORA_SITE_BASIC="https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip" \
    DOWNLOAD_TEMP=/downloads

# Update
# ------
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y apt-utils && \
    apt-get install -y sudo

# RDP Graphical Interface on port 3391
# ------------------------------------
RUN apt-get purge   -y xrdp && \
    apt-get install -y xrdp && \
    apt-get install -y xfce4 && \
    apt-get install -y xfce4-goodies && \
    cp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.bak && \
    sed -i 's/3389/3391/g' /etc/xrdp/xrdp.ini && \
    sed -i 's/max_bpp=32/#max_bpp=32\nmax_bpp=128/g' /etc/xrdp/xrdp.ini && \
    sed -i 's/xserverbpp=24/#xserverbpp=24\nxserverbpp=128/g' /etc/xrdp/xrdp.ini && \
    echo 'xfce4-session' > ~/.xsession && \
    sed -i 's/test -x/#test -x/g' /etc/xrdp/startwm.sh && \
    sed -i 's/exec/#exec/g' /etc/xrdp/startwm.sh && \
    echo '#xfce' >> /etc/xrdp/startwm.sh && \
    echo 'startxfce4' >> /etc/xrdp/startwm.sh && \
    echo '#!/bin/bash' > /root/startdgfx.sh && \
    echo '/etc/init.d/xrdp stop' >> /root/startdgfx.sh && \
    echo 'rm /var/run/xrdp/xrdp.pid' >> /root/startdgfx.sh && \
    echo '/etc/init.d/xrdp start' >> /root/startdgfx.sh && \
    echo 'bash' >> /root/startdgfx.sh && \
    chmod 777 /root/startdgfx.sh

# Install Packages
# ----------------
#RUN apt-get install -y synaptic # FIXME: Synpatic does not work, why???
RUN apt-get install -y gdebi && \
    apt-get install -y git && \
    apt-get install -y fpc && \
    apt-get install -y wget && \
    apt-get install -y vim && \
    apt-get install -y aptitude

# Oracle Client 19.8.0.0
# ----------------------
RUN mkdir $DOWNLOAD_TEMP && \
    curl --progress-bar $ORA_SITE_CLIENT -o $DOWNLOAD_TEMP/instantclient-basic-linux.zip && \
    curl --progress-bar $ORA_SITE_BASIC -o $DOWNLOAD_TEMP/instantclient-sqlplus-linux.zip && \
    mkdir $ORACLE_BASE && \
    cd $DOWNLOAD_TEMP && \
    unzip $DOWNLOAD_TEMP/instantclient-basic-linux.zip -d $ORACLE_BASE && \
    unzip $DOWNLOAD_TEMP/instantclient-sqlplus-linux.zip -d $ORACLE_BASE

# Prepare CodeTyphon 7.2
# ----------------------
COPY CodeTyphonIns.zip $DOWNLOAD_TEMP
RUN chmod 777 $DOWNLOAD_TEMP/CodeTyphonIns.zip

# Ports
# -----
EXPOSE 3391 3350

# Startup Script
# --------------
CMD ["/root/startdgfx.sh"]