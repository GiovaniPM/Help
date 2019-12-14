@echo off

For /f %%G in ('cscript /nologo getdate.vbs') do set _dtm=%%G
set _yyyy=%_dtm:~0,4%
set _mm=%_dtm:~4,2%
set _dd=%_dtm:~6,2%
set _hh=%_dtm:~8,2%
set _nn=%_dtm:~10,2%

set timetoday=%_yyyy%%_mm%%_dd%
set filename=%COMPUTERNAME%.txt
set filenamebkp=%COMPUTERNAME%_%timetoday%

IF [%1] == [b] GOTO backup
IF [%1] == [B] GOTO backup
IF [%1] == [r] GOTO restore
IF [%1] == [R] GOTO restore
echo Invalid parameters, try:
echo   codiumbkp b -- to backup
echo   codiumbkp r -- to restore
goto end

:backup
del .\bkp\%filenamebkp% /q
xcopy .\%filename% .\bkp\ /y
ren .\bkp\%filename% %filenamebkp%
codium --list-extensions > %filename%
goto end

:restore
::cat extensions.txt | xargs -L 1 code --install-extension
for /F "tokens=1,2,3 delims= " %%G in (%filename%) DO codium --install-extension %%G
goto end

:end