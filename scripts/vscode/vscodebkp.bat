@ECHO OFF

FOR /f %%G in ('cscript /nologo getdate.vbs') DO SET _dtm=%%G
SET _yyyy=%_dtm:~0,4%
SET _mm=%_dtm:~4,2%
SET _dd=%_dtm:~6,2%
SET _hh=%_dtm:~8,2%
SET _nn=%_dtm:~10,2%

SET timetoday=%_yyyy%%_mm%%_dd%
SET filenamebkp=%COMPUTERNAME%_%timetoday%
SET filename=%COMPUTERNAME%.txt

IF [%2] NEQ [] SET filename=%2
IF [%1] == [b] GOTO backup
IF [%1] == [B] GOTO backup
IF [%1] == [r] GOTO restore
IF [%1] == [R] GOTO restore
ECHO Invalid parameters, try:
ECHO   vscodebkp b -- to backup
ECHO   vscodebkp r -- to restore
GOTO end

:backup
DEL .\bkp\%filenamebkp% /q
XCOPY .\%filename% .\bkp\ /y
REN .\bkp\%filename% %filenamebkp%
code --list-extensions > %filename%
GOTO end

:restore
::cat extensions.txt | xargs -L 1 code --install-extension
@ECHO Installed extensions:
@ECHO --------------------
FOR /F "tokens=1,2,3 DELims= " %%G IN (%filename%) DO @code --install-extension %%G | @ECHO %%G
GOTO end

:end