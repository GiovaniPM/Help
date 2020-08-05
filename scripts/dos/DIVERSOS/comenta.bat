@echo off

for /f "tokens=1-4 delims=/ " %%i in ("%date%") do (
     set month=%%i
     set day=%%j
     set year=%%k
)

set datestr=%month%/%day%/%year%

echo %username% > 1.txt
echo %1 - %datestr% - Inicio >> 1.txt
type 1.txt | boxes -d jde -a l -s 53 > 2.txt
echo %username% > 1.txt
echo %1 - %datestr% - Fim >> 1.txt
type 1.txt | boxes -d jde -a l -s 53 >> 2.txt

codium 2.txt

del 1.txt
del 2.txt