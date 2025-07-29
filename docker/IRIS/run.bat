@echo off
rem docker run --name my-iris -d --publish 9091:1972 --publish 9092:52773 --volume /home/irisowner/:/durable intersystems/iris-community:latest-cd --password-file /durable/password/password.txt
docker run --name my-iris -d --publish 9091:1972 --publish 9092:52773 intersystems/iris-community:latest-cd