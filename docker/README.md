# Minhas images

## 1 Home

### 1.1 Link
https://hub.docker.com/_/nginx

### 1.2 Pull Command
```dockerfile
docker pull nginx
```

### 1.3 Pacote
```DOS
@echo off

set ant=%cd%

echo (1/7) Gerando pacote
echo (1/7) Gerando pacote > %ant%\log.txt
tar --exclude="./*.old" --exclude="./*.xlsx" --exclude="./*.zip" --exclude="./.git" --exclude="./*.ktz" --exclude="./*.000" --exclude="./log.txt" -czvf home.000 . >> %ant%\log.txt

echo (2/7) Aplicando pacote
echo (2/7) Aplicando pacote >> %ant%\log.txt
xcopy home.000 ..\help\docker\home\. /y >> %ant%\log.txt
del home.000

echo (3/7) Parando container
echo (3/7) Parando container >> %ant%\log.txt
docker stop home >> %ant%\log.txt

echo (4/7) Removendo container
echo (4/7) Removendo container >> %ant%\log.txt
docker image rm home >> %ant%\log.txt

echo (5/7) Removendo imagem
echo (5/7) Removendo imagem >> %ant%\log.txt
docker rm home >> %ant%\log.txt
cd ..\help\docker\home

echo (6/7) Criando imagem
echo (6/7) Criando imagem >> %ant%\log.txt
docker build --tag=homeimg . >> %ant%\log.txt

echo (7/7) Criando container
echo (7/7) Criando container >> %ant%\log.txt
docker run -d --name="home" -p 8081:80 homeimg >> %ant%\log.txt
del home.000

cd %ant%
```

### 1.4 Dockerfile
```dockerfile
FROM nginx
RUN apt-get update && apt-get install -y curl
COPY home.000 /usr/share/nginx/html
RUN cd /usr/share/nginx/html && tar xzvf home.000
EXPOSE 80
```

### 1.5 Build
```dockerfile
docker build --tag=homeimg .
```

### 1.6 Run
```dockerfile
docker run -d --name="homeimg" -p 8081:80 home
```

## 2 Service DV

### 2.1 Link
https://hub.docker.com/_/debian

### 2.2 Pull Command
```dockerfile
docker pull debian:8
```

### 2.3 Dockerfile
```dockerfile
FROM debian:8
RUN mkdir /dv
RUN apt-get update && apt-get install -y python3 python3-pip curl
RUN curl -sSL https://raw.githubusercontent.com/GiovaniPM/flaskAPI/master/dv.py > /dv/dv.py
COPY requirements.txt /dv/requirements.txt
RUN cd dv && /usr/bin/pip3 install -r requirements.txt
EXPOSE 8080
CMD ["/usr/bin/python3", "dv/dv.py"]
```

### 2.4 Requirements.txt
```dos
flask
json5
flask_cors
requests
```

### 2.5 Build
```dockerfile
docker build --tag=dvimg .
```

### 2.6 Run
```dockerfile
docker run -d --name="dv" -p 8080:8080 dvimg
```

## 3 DB2

### 3.1 Link
https://hub.docker.com/r/ibmcom/db2

### 3.2 Pull Command
```dockerfile
docker pull ibmcom/db2
```

### 3.3 Run
```dockerfile
docker run -itd --name mydb2 --privileged=true -p 50000:50000 -e LICENSE=accept -e DB2INST1_PASSWORD=pm11092j -e DBNAME=testdb ibmcom/db2
```

### 3.4 DBeaver
![OracleConnection](https://raw.githubusercontent.com/GiovaniPM/Help/master/docker/DB2Connection.png)

## 4 Firebird

### 4.1 Link
https://hub.docker.com/r/controlsoft/firebird

### 4.2 Pull Command
```dockerfile
docker pull controlsoft/firebird
```

### 4.3 Run
```dockerfile
docker run -d --name "myfirebird" -p 3050:3050 controlsoft/firebird
```

### 4.4 Exemplos
[Montagem DB](https://github.com/GiovaniPM/Help/blob/master/docker/Firebird/firebird.md)

### 4.5 DBeaver
![OracleConnection](https://raw.githubusercontent.com/GiovaniPM/Help/master/docker/FirebirdConnection.png)

## 5 MariaDB

### 5.1 Pull Command
```dockerfile
docker pull mariadb
```

### 5.2 Run
```dockerfile
docker run -d --name "myMariaDB" -p 3306:3306 -e MYSQL_ROOT_PASSWORD=pm11092j mariadb
```

### 5.3 Exemplos
[Montagem DB](https://github.com/GiovaniPM/Help/blob/master/docker/MARIADB/mariadb.md)

### 5.4 DBeaver
![OracleConnection](https://raw.githubusercontent.com/GiovaniPM/Help/master/docker/MariaDBConnection.png)

## 6 Oracle XE 18.4.0

### 6.1 Link
https://hub.docker.com/r/pvargacl/oracle-xe-18.4.0

### 6.2 Pull Command
```dockerfile
docker pull pvargacl/oracle-xe-18.4.0
```

### 6.3 Dockerfile
```dockerfile
# Autor: Giovani Perotto Mesquita
FROM pvargacl/oracle-xe-18.4.0
RUN mkdir /scripts
COPY *.sql /scripts/
COPY *.sh /scripts/
RUN chmod 777 /scripts/popula.sh
EXPOSE 1521
EXPOSE 1541
EXPOSE 5500
```

### 6.4 popula.sh
```bash
#!/bin/bash
sqlplus SYS/oracle@XE AS SYSDBA @/scripts/setupXE.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f0006.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f4101.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f4102.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f4105.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f4111.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f41002.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f41003.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f41021.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f41112.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f76411.sql
sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/f76412.sql
#sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/jde_converte_um.sql
#sqlplus C##GIOVANIPM/Pm11092j@XE @/scripts/IndicesEstoque.sql
```

### 6.5 Build
```dockerfile
docker build --tag=oracle18.4.0 .
```

### 6.6 Run
```dockerfile
docker run --name="myoraclexe" -d -p 1541:1541 -p 1521:1521 -p 5500:5500 oracle18.4.0
```

### 6.7 Exemplos
[Montagem DB](https://github.com/GiovaniPM/Help/blob/master/docker/Oracle/setupXE.md)

### 6.8 DBeaver
![OracleConnection](https://raw.githubusercontent.com/GiovaniPM/Help/master/docker/OracleConnection.png)

## 7 SQL Server

### 7.1 Link
https://hub.docker.com/_/microsoft-mssql-server

### 7.2 Pull Command
```dockerfile
docker pull mcr.microsoft.com/mssql/server:2017-latest-ubuntu
```

### 7.3 Run
```dockerfile
docker run --name="mySQLServer" -e ACCEPT_EULA=Y -e SA_PASSWORD=pm11092j -e MSSQL_PID=Express -p 1433:1433 -d mcr.microsoft.com/mssql/server:2017-latest-ubuntu
```

### 7.4 DBeaver
![OracleConnection](https://raw.githubusercontent.com/GiovaniPM/Help/master/docker/SQLServerConnection.png)

## 8 Teamspeak

### 8.1 Link
https://hub.docker.com/_/teamspeak

### 8.2 Pull Command
```dockerfile
docker pull teamspeak
```

### 8.3 Run
```dockerfile
docker run --name="GameSvrOne" -p 9987:9987/udp -p 10011:10011 -p 30033:30033 -e TS3SERVER_LICENSE=accept -d teamspeak
```

### 8.4 Teamspeak client
![TeamspeakConnection](https://raw.githubusercontent.com/GiovaniPM/Help/master/docker/TeamspeakConnection.png)