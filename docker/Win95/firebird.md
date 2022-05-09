# Creating container
```DOS
docker run --name firebird -d -p 3050:3050 -p 3051:3051 controlsoft/firebird
```

# Generate user
```SQL
CREATE DATABASE '/databases/teste.FDB' page_size 8192 user 'SYSDBA' password 'masterkey';

CONNECT "/databases/teste.FDB" user 'SYSDBA' password 'masterkey';

CREATE TABLE NOMES (ID INTEGER NOT NULL PRIMARY KEY, DESCRICAO VARCHAR(100));
```

setting 'SYSDBA' password to '3b728c882d9f53722011'