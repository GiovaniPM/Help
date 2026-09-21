@echo off
rem Gera ORACLE.LIB e o programa de exemplo TESTE.EXE (Clipper 5.2 + RTLink/Blinker)
rem
rem   /n  nao cria a procedure inicial (necessario para bibliotecas)
rem   /w  avisa sobre variaveis nao declaradas
rem
rem Antes de compilar, o CLIPPER precisa achar ORACLE.CH: rode desta pasta ou
rem use "set include=<pasta>" (ou a opcao /i do compilador).
clipper oracle /n /w
if errorlevel 1 goto erro

rem recria a biblioteca do zero a cada execucao
if exist oracle.lib del oracle.lib
lib oracle +oracle
if errorlevel 1 goto erro

rem programa de exemplo (tem FUNCTION Main, entao sem /n)
clipper teste /w
if errorlevel 1 goto erro

rem liga TESTE.OBJ com ORACLE.LIB
rtlink fi teste lib oracle
if errorlevel 1 goto erro
echo OK
goto fim
:erro
echo Falha na compilacao
:fim
