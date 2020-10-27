```SQL
CREATE DATABASE '/databases/teste.FDB' page_size 8192 user 'SYSDBA' password 'masterkey';

CONNECT "/databases/teste.FDB" user 'SYSDBA' password 'masterkey';

CREATE TABLE NOMES (ID INTEGER NOT NULL PRIMARY KEY, DESCRICAO VARCHAR(100));
```