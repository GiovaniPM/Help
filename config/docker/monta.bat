@echo off

docker pull pvargacl/oracle-xe-18.4.0
docker run --name oracle18 -d -p 1521:1521 pvargacl/oracle-xe-18.4.0
docker stop oracle18

docker pull mediawiki
docker run --name some-mediawiki -p 8080:80 -d mediawiki
docker stop some-mediawiki

docker pull mariadb
docker run --name some-mariadb -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mariadb
docker stop some-mariadb

cd ..
cd ..
cd docker
cd dv

build_dv.bat
run_dv.bat
stop_dv.bat

cd ..
cd ..
cd config
cd docker