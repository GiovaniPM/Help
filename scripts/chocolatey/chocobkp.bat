@echo off

For /f %%G in ('cscript /nologo getdate.vbs') do set _dtm=%%G
set _yyyy=%_dtm:~0,4%
set _mm=%_dtm:~4,2%
set _dd=%_dtm:~6,2%
set _hh=%_dtm:~8,2%
set _nn=%_dtm:~10,2%

set timetoday=%_yyyy%%_mm%%_dd%
set filename=%COMPUTERNAME%.bat
set filenamebkp=%COMPUTERNAME%_%timetoday%

del .\bkp\%filenamebkp% /q
xcopy .\%filename% .\bkp\ /y
ren .\bkp\%filename% %filenamebkp%
<<<<<<< HEAD
choco list > temp.txt
=======
REM choco list -l > temp.txt
choco list | busybox tail -n +9 | busybox head -n -1 > temp.txt
>>>>>>> 589501df68a013e5c6456f63271db427197eb49d
echo @echo off > %filename%
echo REM =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= >> %filename%
echo REM %COMPUTERNAME% >> %filename%
echo REM Capturado em: %_dd%/%_mm%/%_yyyy% %_hh%:%_nn% >> %filename%
echo REM =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= >> %filename%

for /F "tokens=1,2,3 delims= " %%G in (temp.txt) DO if [%%I] NEQ [installed.] echo choco install %%G -y >> %filename%

del temp.txt