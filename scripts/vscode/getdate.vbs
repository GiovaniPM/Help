' Syntax:
'  CSCRIPT /nologo getdate.vbs
 
Dim dt
dt=now
'output format: yyyymmddHHnn
wscript.echo ((year(dt)*100 + month(dt))*100 + day(dt))*10000 + hour(dt)*100 + minute(dt)