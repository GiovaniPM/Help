# Creating container
```DOS
docker run -itd --name mydb2 --privileged=true -p 50000:50000 -e LICENSE=accept -e DB2INST1_PASSWORD=pm11092j -e DBNAME=testdb ibmcom/db2
```

# Generate user
```SQL

```