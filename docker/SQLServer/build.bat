docker rm --force sqlserver
docker rmi mssqlbasic
docker build -t mssqlbasic .
docker run -d --name sqlserver -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=Pm11092j#" -e "MSSQL_PID=Express" -p 1433:1433 -d mssqlbasic
docker network connect myNetwork sqlserver
REM docker network create myNetwork
REM docker network inspect myNetworkShow