@echo off

set NetworkName="myNetwork"
set ContainerName="oraclexe"
set ImageName="oraclebasic"
set PortList=-p 1541:1541 -p 1521:1521 -p 5500:5500
set Volumes=-v dadosxe:/opt/oracle/oradata
set Variaveis=

..\runbuild