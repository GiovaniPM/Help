# Minhas images

## Oracle XE 18.4.0

### Link
https://hub.docker.com/r/pvargacl/oracle-xe-18.4.0

### Pull Command
```dockerfile
docker pull pvargacl/oracle-xe-18.4.0
```

### Dockerfile
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

### popula.sh
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

### Build
```dockerfile
docker build --tag=oracle18.4.0 .
```

### Run
```dockerfile
docker run --name="oraclexe" -d -p 1541:1541 -p 1521:1521 -p 5500:5500 oracle18.4.0
```

![OracleConnection](https://raw.githubusercontent.com/GiovaniPM/Help/master/docker/OracleConnection.png)

## Home

### Link
https://hub.docker.com/_/nginx

### Pull Command
```dockerfile
docker pull nginx
```

### Pacote
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

### Dockerfile
```dockerfile
FROM nginx
RUN apt-get update && apt-get install -y curl
COPY home.000 /usr/share/nginx/html
RUN cd /usr/share/nginx/html && tar xzvf home.000
EXPOSE 80
```

### Build
```dockerfile
docker build --tag=homeimg .
```

### Run
```dockerfile
docker run -d --name="homeimg" -p 8081:80 home
```

## Service DV

### Link
https://hub.docker.com/_/debian

### Pull Command
```dockerfile
docker pull debian:8
```

### Dockerfile
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

### requirements.txt
```dos
flask
json5
flask_cors
requests
```

### Build
```dockerfile
docker build --tag=dvimg .
```

### Run
```dockerfile
docker run -d --name="dv" -p 8080:8080 dvimg
```

## Firebase

### Link
https://hub.docker.com/r/controlsoft/firebird

### Pull Command
```dockerfile
docker pull controlsoft/firebird
```

### Run
```dockerfile
docker run -d --name "firebird" -p 3050:3050 controlsoft/firebird
```

## MariaDB

### Pull Command
```dockerfile
docker pull mariadb
```

### Run
```dockerfile
docker run -d --name "MariaTest" -p 3306:3306 -e MYSQL_ROOT_PASSWORD=pm11092j mariadb
```