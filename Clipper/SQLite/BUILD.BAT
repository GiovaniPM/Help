@echo off
rem Gera SQLITE.LIB e o programa de exemplo TESTE.EXE (Clipper 5.2 + RTLink/Blinker)
rem
rem   /n  nao cria a procedure inicial (necessario para bibliotecas)
rem   /w  avisa sobre variaveis nao declaradas
rem
rem Antes de compilar, o CLIPPER precisa achar SQLITE.CH: rode desta pasta ou
rem use "set include=<pasta>" (ou a opcao /i do compilador).
clipper sqlite /n /w
if errorlevel 1 goto erro

rem recria a biblioteca do zero a cada execucao
if exist sqlite.lib del sqlite.lib
lib sqlite +sqlite
if errorlevel 1 goto erro

rem programa de exemplo (tem FUNCTION Main, entao sem /n)
clipper teste /w
if errorlevel 1 goto erro

rem liga TESTE.OBJ com SQLITE.LIB
rtlink fi teste lib sqlite
if errorlevel 1 goto erro
echo OK
goto fim
:erro
echo Falha na compilacao
:fim
