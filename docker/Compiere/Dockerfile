####################################################################################################
# Dockerfile to create Compiere ERP Server
# -------------------------------------------------------------------------------------------------
# Author: Giovani Perotto Mesquuita<giovanipm@gmail.com>
# Date: 15/12/2020
# -------------------------------------------------------------------------------------------------
# Know Issues:
# - 
# Next steps:
# - 
####################################################################################################

FROM openjdk:8-jdk-alpine

# ------
# Labels
# ------
LABEL version="1.02" \
      description="Compiere Community Edition 3.5" \
      maintainer="Giovani Mesquita<giovanipm@gmail.com>"                 

# -------------------------------------------------------------
# Environment variables required for this build (do NOT change)
# -------------------------------------------------------------
ENV	DOWNLOAD_TEMP="/downloads" \
    LANG="pt_BR.UTF-8" \
    LANGUAGE="pt.UTF-8" \
    OPT_DIR="/opt" 

ENV LD_LIBRARY_PATH="/lib" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/oracle/instantclient_19_8" \
    ORACLE_BASE="/opt/oracle" \
    ORACLE_HOME="/opt/oracle/product/19c/dbhome_1" \ 
#    ORACLE_SITE_BASIC="https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-sqlplus-linux.x64-19.8.0.0.0dbru.zip" \
    ORACLE_SITE_BASIC="https://download.oracle.com/otn_software/linux/instantclient/193000/instantclient-basic-linux.x64-19.3.0.0.0dbru.zip" \
    ORACLE_SITE_CLIENT="https://download.oracle.com/otn_software/linux/instantclient/19800/instantclient-basic-linux.x64-19.8.0.0.0dbru.zip?xd_co_f=fae07a5a-ae5f-4c1a-8ce0-f41ed4a394c5'" \
    PATH="$PATH:/opt/oracle/instantclient_19_8" 

ENV COMPIERE_BINARY_NAME="Compiere.zip" \
    COMPIERE_HOME="/opt/Compiere2" \
    COMPIERE_JAVA_OPTIONS="-Xms256M -Xmx1000M" \
    COMPIERE_RELEASE_NAME="3.5.0 STD" \
    COMPIERE_RELEASE_URL="http://www.compiere.com/products/download/Compiere_350_STD.zip" \
    COMPIERE_SERVICE_TYPE="jboss" \
    COMPIERE_SSL_PORT="4443" \
    COMPIERE_WEB_PORT="8888"

# ------------
# Expose Ports
# ------------
EXPOSE $COMPIERE_SSL_PORT \
       $COMPIERE_WEB_PORT

# -----------
# Set Workdir
# -----------
WORKDIR $COMPIERE_HOME

# -------------------
# Setting Environment
# -------------------
RUN echo "Setting environment" && \
    cd $OPT_DIR && \
	echo "COMPIERE_HOME=$ADEMPIERE_HOME" >> /root/.bashrc  && \
	echo "JAVA_HOME=$JAVA_HOME" >> /root/.bashrc  && \
	echo "export JAVA_HOME" >> /root/.bashrc  && \
	echo "export COMPIERE_HOME" >> /root/.bashrc

# -------
# Aliases
# -------
RUN echo "Aliases" && \
    echo "alias dir='ls -lias --color'" >> /root/.bashrc && \
    echo "alias cls='clear'" >> /root/.bashrc

# -----------------
# Auxiliar software
# -----------------
RUN echo "Auxiliar Software" && \
    apk update && \
    apk upgrade && \
    apk --no-cache add autoconf && \
    apk --no-cache add cpio && \
    apk --no-cache add curl && \
    apk --no-cache add gcc && \
    apk --no-cache add git && \
    apk --no-cache add musl-dev && \
    apk --no-cache add openssl-dev && \
	apk --no-cache add sed && \
    apk --no-cache add sudo && \
	apk --no-cache add ttf-dejavu && \
    apk --no-cache add unzip && \
    apk --no-cache add vim && \
    apk --no-cache add wget && \
    apk --no-cache add zip

# -------------
# Oracle Client
# -------------
RUN echo "Oracle Install" && \
    mkdir $DOWNLOAD_TEMP && \
    curl --progress-bar $ORACLE_SITE_CLIENT -o $DOWNLOAD_TEMP/instantclient-basic-linux.zip && \
    curl --progress-bar $ORACLE_SITE_BASIC -o $DOWNLOAD_TEMP/instantclient-sqlplus-linux.zip && \
    mkdir $ORACLE_BASE && \
    cd $DOWNLOAD_TEMP && \
    unzip $DOWNLOAD_TEMP/instantclient-basic-linux.zip -d $ORACLE_BASE && \
    unzip $DOWNLOAD_TEMP/instantclient-sqlplus-linux.zip -d $ORACLE_BASE && \
    apk --no-cache add libaio && \
    apk --no-cache add libaio && \
    apk --no-cache add libnsl && \
    apk --no-cache add libc6-compat && \
    cd /lib && \
    ln -s /lib64/* /lib && \
    ln -s libnsl.so.2 /usr/lib/libnsl.so.1 && \
    ln -s libc.so /usr/lib/libresolv.so.2
#    cd /lib && \
#    curl --progress-bar $ORACLE_SITE_CLIENT -o instantclient-basic-linux.zip && \
#    unzip instantclient-basic-linux.zip && \
#    rm -rf instantclient-basic-linux.zip && \
#    apk --no-cache add libaio && \
#    apk --no-cache add libaio && \
#    apk --no-cache add libnsl && \
#    apk --no-cache add libc6-compat && \
#    ln -s /lib64/* /lib && \
#    ln -s libnsl.so.2 /usr/lib/libnsl.so.1 && \
#    ln -s libc.so /usr/lib/libresolv.so.2

# ----------------
# Compiere Install
# ----------------
RUN echo "Compiere Install" && \
    curl --progress-bar $COMPIERE_RELEASE_URL -o $DOWNLOAD_TEMP/$COMPIERE_BINARY_NAME && \
    unzip $DOWNLOAD_TEMP/$COMPIERE_BINARY_NAME -d /opt && \
    cd $COMPIERE_HOME && \
    chmod -Rf 755 *.sh && \
	 chmod -Rf 755 utils/*.sh

# -------------------
# Removing temp files
# -------------------
RUN echo "Removing temp files" && \
    rm $DOWNLOAD_TEMP/$COMPIERE_BINARY_NAME  && \
    rm $DOWNLOAD_TEMP/instantclient-basic-linux.zip  && \
    rm $DOWNLOAD_TEMP/instantclient-sqlplus-linux.zip