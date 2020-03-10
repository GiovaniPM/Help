@echo off
title Alerta

echo result=Msgbox("Coma uma barrinha de cereal!",vbOk,"Lembrete") > %TEMP%\~input.vbs
echo WScript.Echo result >> %TEMP%\~input.vbs

cscript //nologo %TEMP%\~input.vbs

del %TEMP%\~input.vbs