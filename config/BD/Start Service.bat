@ECHO OFF

net stop OracleJobSchedulerXE
net stop OracleOraDB18Home1MTSRecoveryService
net stop OracleOraDB18Home1TNSListener
net stop OracleVssWriterXE
net stop OracleServiceXE

sc config OracleJobSchedulerXE start= auto
sc config OracleOraDB18Home1MTSRecoveryService start= auto
sc config OracleOraDB18Home1TNSListener start= demand
sc config OracleServiceXE start= auto
sc config OracleVssWriterXE start= auto

net start OracleServiceXE
net start OracleJobSchedulerXE
net start OracleOraDB18Home1MTSRecoveryService
net start OracleOraDB18Home1TNSListener
net start OracleVssWriterXE