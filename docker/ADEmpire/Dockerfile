FROM openjdk:8-jdk-alpine
MAINTAINER Yamel Senih "ysenih@erpya.com"
COPY start-adempiere.sh /opt/

ENV LANG=es_ES.UTF-8
ENV LANGUAGE=es_ES.UTF-8

ENV ADEMPIERE_DB_HOST localhost
ENV ADEMPIERE_DB_PORT 5432
ENV ADEMPIERE_DB_NAME ADempiereSeed
ENV ADEMPIERE_DB_USER adempiere
ENV ADEMPIERE_DB_PASSWORD adempiere
ENV ADEMPIERE_DB_ADMIN_PASSWORD postgres
ENV ADEMPIERE_WEB_PORT 8888
ENV ADEMPIERE_SSL_PORT 4443
ENV OPT_DIR /opt
ENV ADEMPIERE_HOME /opt/Adempiere
ENV ADEMPIERE_RELEASE_URL https://github.com/erpcya/adempiere/releases/download
ENV ADEMPIERE_RELEASE_NAME 3.9.3-rs-3.8
ENV ADEMPIERE_BINARY_NAME Adempiere_393LTS.tar.gz
ENV ADEMPIERE_SERVICE_TYPE jboss
ENV ADEMPIERE_JAVA_OPTIONS -Xms256M -Xmx1000M

#Expose Ports
EXPOSE $ADEMPIERE_WEB_PORT
EXPOSE $ADEMPIERE_SSL_PORT

#Set Workdir
WORKDIR $ADEMPIERE_HOME

RUN echo "Install needed packages..." && \
	apk --no-cache add sed && \
	apk --no-cache add wget && \
	apk --no-cache add ttf-dejavu && \
	echo "Get ADempiere Binary..."  && \
	cd $OPT_DIR && \
	wget -c $ADEMPIERE_RELEASE_URL/$ADEMPIERE_RELEASE_NAME/$ADEMPIERE_BINARY_NAME && \
	echo "De-compress ADempiere Binary..." && \ 
	tar -C $OPT_DIR -zxvf $ADEMPIERE_BINARY_NAME && \
	echo "Setting Directories and access..." && \
	cd $ADEMPIERE_HOME && \ 
	chmod -Rf 755 *.sh && \
	chmod -Rf 755 utils/*.sh && \
	chmod +x $OPT_DIR/start-adempiere.sh && \
	cp AdempiereEnvTemplate.properties AdempiereEnv.properties && \
	sed -i "s@ADEMPIERE_HOME=C.*@ADEMPIERE_HOME=$ADEMPIERE_HOME@" AdempiereEnv.properties && \
	sed -i "s@JAVA_HOME=C.*@JAVA_HOME=$JAVA_HOME@" AdempiereEnv.properties && \
	sed -i "s/ADEMPIERE_KEYSTORE=C*/ADEMPIERE_KEYSTORE=\/data\/app\/Adempiere\/keystore\/myKeystore/g" AdempiereEnv.properties && \
	echo "Remove Compress Binary..." && \
	rm $OPT_DIR/$ADEMPIERE_BINARY_NAME  && \
	echo "Remove Data Files..." && \
	rm -R $ADEMPIERE_HOME/data/*

#Setting Environment
RUN cd $OPT_DIR && \
	echo "ADEMPIERE_HOME=$ADEMPIERE_HOME" >> /root/.bashrc  && \
	echo "JAVA_HOME=$JAVA_HOME" >> /root/.bashrc  && \
	echo "export JAVA_HOME" >> /root/.bashrc  && \
	echo "export ADEMPIERE_HOME" >> /root/.bashrc

#Start Adempiere
CMD $OPT_DIR/start-adempiere.sh