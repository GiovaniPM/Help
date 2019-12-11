@echo off
setlocal EnableDelayedExpansion
if "%~1" equ "AnimateBanner" goto AnimateBanner

rem Animated banner in Batch file
rem Antonio Perez Ayala aka Aacini

set "delay=25"
set "myself=%~F0"
call :ShowBanner 60 "Giovani"
goto :EOF


:ShowBanner columns "banner"

rem Assemble the banner lines
set /A cols=%1, colsM1=cols-1
for /L %%i in (1,1,%colsM1%) do set "spaces= !spaces!"
if not defined fontSize call :DefineFont
for /L %%i in (1,1,%fontSize%) do set "msg[%%i]="
set "lowcase=abcdefghijklmnopqrstuvwxyz"
set "msg=%~2"
:nextChar
   for /F "delims=" %%c in ("%msg:~0,1%") do (
      if "%%c" equ "," (
         for /L %%i in (1,1,%fontSize%) do set "msg[%%i]=!msg[%%i]!!fComma%%i!  "
      ) else if "!lowcase:%%c=%%c!" equ "%lowcase%" (
         for /L %%i in (1,1,%fontSize%) do set "msg[%%i]=!msg[%%i]!!f%%c%%i!  "
      ) else (
         for /L %%i in (1,1,%fontSize%) do set "msg[%%i]=!msg[%%i]!!f%%c%%c%%i!  "
      )
   )
   set "msg=%msg:~1%"
if defined msg goto nextChar
call :StrLen "%msg[1]%" msgLen=

rem Animate the banner
start "" /WAIT cmd /C "%myself%" AnimateBanner
exit /B


:AnimateBanner
title Press any key to continue
mode %cols%,%lines%

del keyPressed 2>nul
start /B cmd /C pause^>nul ^& echo X^>keyPressed

set "i=0"
:loop1
(cls
echo/
for %%i in (!i!) do for /L %%j in (1,1,%fontSize%) do (
   echo(!spaces:~%%i!!msg[%%j]:~0,%%i!
))
if exist keyPressed exit
pathping 127.0.0.1 -n -q 1 -p %delay% >nul
set /A i+=1
if %i% lss %colsM1% goto loop1
set "i=0"
:loop2
(cls
echo/
for %%i in (!i!) do for /L %%j in (1,1,%fontSize%) do (
   echo(!msg[%%j]:~%%i,%colsM1%!
))
if exist keyPressed exit
pathping 127.0.0.1 -n -q 1 -p %delay% >nul
set /A i+=1
if %i% lss %msgLen% goto loop2
set "i=0"
goto loop1


:DefineFont

set "next[Û]= "
set "next[ ]=Û"
set "letter="
for %%a in (
   AA = "5 1+3+1 1+3+1 5 1+3+1 1+3+1 1+3+1 0+5"
    a = "0+5 0+5 0+1+3+1 0+4+1 0+1+4 1+3+1 0+1+4 0+5"
   BB = "4+1 1+3+1 1+3+1 4+1 1+3+1 1+3+1 4+1 0+5"
    b = "1+4 1+4 1+4 4+1 1+3+1 1+3+1 4+1 0+5"
   CC = "5 1+4 1+4  1+4  1+4 1+4 5 0+5"
    c = "0+5 0+5 5 1+4 1+4 1+4 5 0+5"
   DD = "4+1 1+3+1 1+3+1  1+3+1  1+3+1 1+3+1 4+1 0+5"
    d = "0+4+1 0+4+1 0+4+1 0+1+4 1+3+1 1+3+1 0+1+4 0+5"
   EE = "5 1+4 1+4 5 1+4 1+4 5 0+5"
    e = "0+5 0+5 0+1+3+1 1+3+1 5 1+4 0+1+4 0+5"
   FF = "5 1+4 1+4 5 1+4 1+4 1+4 0+5"
    f = "0+1+2 0+1+1+1 0+1+1+1 3 0+1+1+1 0+1+1+1 0+1+1+1 0+3"
   GG = "5 1+4 1+4 1+1+3 1+3+1 1+3+1 5 0+5"
    g = "0+5 0+5 0+1+4 1+3+1 1+3+1 0+1+4 0+4+1 4+1"
   HH = "1+3+1 1+3+1 1+3+1 5 1+3+1 1+3+1 1+3+1 0+5"
    h = "1+4 1+4 1+4 4+1 1+3+1 1+3+1 1+3+1 0+5"
   II = "3 0+1+1+1 0+1+1+1 0+1+1+1 0+1+1+1 0+1+1+1 3 0+3"
    i = "1 0+1 1 1 1 1 1 0+1"
   JJ = "0+4+1 0+4+1 0+4+1 0+4+1 1+3+1 1+3+1 5 0+5"
    j = "0+2+1 0+3 0+2+1 0+2+1 0+2+1 0+2+1 1+1+1 3"
   KK = "1+3+1 1+2+1+1 1+1+1+2 2+3 1+1+1+2 1+2+1+1 1+3+1 0+5"
    k = "1+3 1+3 1+2+1 1+1+1+1 2+2 1+1+1+1 1+2+1 0+4"
   LL = "1+4 1+4 1+4 1+4 1+4 1+4 5 0+5"
    l = "2+1 0+1+1+1 0+1+1+1 0+1+1+1 0+1+1+1 0+1+1+1 3 0+3"
   MM = "1+5+1 2+3+2 1+1+1+1+1+1+1 1+2+1+2+1 1+5+1 1+5+1 1+5+1 0+7"
    m = "0+6 0+6 1+1+1+1+1+1 0+1+1+1+1+1+1 0+1+1+1+1+1+1 0+1+1+1+1+1+1 0+1+1+1+1+1+1 0+6"
   NN = "1+5+1 2+4+1 1+1+1+3+1 1+2+1+2+1 1+3+1+1+1 1+4+2 1+5+1 0+7"
    n = "0+4 0+4 1+1+1+1 0+1+1+1+1 0+1+1+1+1 0+1+1+1+1 0+1+1+1+1 0+4"
   OO = "5 1+3+1 1+3+1  1+3+1  1+3+1 1+3+1 5 0+5"
    o = "0+5 0+5 0+1+3+1 1+3+1 1+3+1 1+3+1 0+1+3+1 0+5"
   PP = "5 1+3+1 1+3+1  5  1+4 1+4 1+4 0+5"
    p = "0+5 0+5 4+1 1+3+1 1+3+1 4+1 1+4 1+4"
   QQ = "5 1+3+1 1+3+1  1+3+1  1+1+1+1+1 1+2+1+1 3+1+1 0+5"
    q = "0+5 0+5 0+1+4 1+3+1 1+3+1 0+1+4 0+4+1 0+4+1"
   RR = "5 1+3+1 1+3+1  5  1+1+1+2 1+2+1+1 1+3+1 0+5"
    r = "0+4 0+4 1+1+2 2+2 1+3 1+3 1+3 0+4"
   SS = "5 1+4 1+4 5 0+4+1 0+4+1 5 0+5"
    s = "0+5 0+5 0+1+4 1+4 0+1+3+1 0+4+1 4+1 0+5"
   TT = "5 0+2+1+2 0+2+1+2 0+2+1+2 0+2+1+2 0+2+1+2 0+2+1+2 0+5"
    t = "0+1+1+1 0+1+1+1 3 0+1+1+1 0+1+1+1 0+1+1+1 0+1+2 0+3"
   UU = "1+3+1 1+3+1 1+3+1 1+3+1 1+3+1 1+3+1 5 0+5"
    u = "0+5 0+5 1+3+1 1+3+1 1+3+1 1+3+1 0+1+3+1 0+5"
   VV = "1+5+1 1+5+1 0+1+1+3+1+1 0+1+1+3+1+1 0+2+1+1+1+2 0+2+1+1+1+2 0+3+1+3 0+7"
    v = "0+5 0+5 1+3+1 1+3+1 0+1+1+1+1+1 0+1+1+1+1+1 0+2+1+2 0+5"
   WW = "1+5+1 1+5+1 1+5+1 1+2+1+2+1 1+1+1+1+1+1+1 2+3+2 1+5+1 0+7"
    w = "0+7 0+7 1+5+1 1+5+1 0+1+1+3+1+1 0+1+1+1+1+1+1+1 0+2+1+1+1+2 0+7"
   XX = "1+5+1 0+1+1+3+1+1 0+2+1+1+1+2 0+3+1+3 0+2+1+1+1+2 0+1+1+3+1+1 1+5+1 0+7"
    x = "0+5 0+5 1+3+1 0+1+1+1+1+1 0+2+1+2 0+1+1+1+1+1 1+3+1 0+5"
   YY = "1+5+1 0+1+1+3+1+1 0+2+1+1+1+2 0+3+1+3 0+3+1+3 0+3+1+3 0+3+1+3 0+7"
    y = "0+5 0+5 1+3+1 0+1+1+1+1+1 0+2+1+2 0+1+1+3 1+4 0+5"
   ZZ = "7 0+5+1+1 0+4+1+2 0+3+1+3 0+2+1+4 0+1+1+5 7 0+7"
    z = "0+5 0+5 5 0+3+1+1 0+2+1+2 0+1+1+3 5 0+5"
    - = "0+3 0+3 0+3 3 0+3 0+3 0+3 0+3"
    . = "0+3 0+3 0+3 0+3 0+3 3 3 0+3"
Comma = "0+3 0+3 0+3 0+3 0+3 3 3 0+2+1"
) do (
   if not defined letter (
      set "letter=%%a"
   ) else (
      set "i=0"
      for %%b in (%%~a) do (
         set /A i+=1
         set "line="
         set "char=Û"
         set "num=%%b"
         set "num=!num:+= !"
         for %%j in (!num!) do (
            for /L %%k in (1,1,%%j) do set "line=!line!!char!"
            for /F "delims=" %%k in ("!char!") do set "char=!next[%%k]!"
         )
         set "f!letter!!i!=!line!"
      )
      set "letter="
   )
)
set /A fontSize=8, lines=fontSize+2
for /L %%i in (1,1,%fontSize%) do set "f %%i=   "
exit /B


:StrLen "str" len=
set "str=0%~1"
set "%2=0"
for /L %%a in (8,-1,0) do (
   set /A "newLen=%2+(1<<%%a)"
   for %%b in (!newLen!) do if "!str:~%%b,1!" neq "" set "%2=%%b"
)
exit /B