# Creating container
```DOS
docker run --name some-mariadb -e MYSQL_ROOT_PASSWORD=pm11092j -d -p 3306:3306 mariadb:tag
```

# Generate user
```SQL
mysql -u root -p -h localhost
CREATE DATABASE bookstore;
```