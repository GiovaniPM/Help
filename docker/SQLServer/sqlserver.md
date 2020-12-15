# Creating container
```DOS
docker run --name sqlserver -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=pm11092j' -e 'MSSQL_PID=Express' -d -p 1433:1433 mcr.microsoft.com/mssql/server:2017-latest-ubuntu 
```

# Generate user
```SQL

```