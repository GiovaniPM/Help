@echo off
title PC Cleanup Utility

setlocal

:menu
cls
SET _string=0
echo Wscript.Echo Inputbox(                              _>%TEMP%\~input.vbs
echo "Select a tool:                        "+vbNewLine+ _>>%TEMP%\~input.vbs
echo "                                      "+vbNewLine+ _>>%TEMP%\~input.vbs
echo "   [1] Delete Internet Cookies        "+vbNewLine+ _>>%TEMP%\~input.vbs
echo "   [2] Delete Temporary Internet Files"+vbNewLine+ _>>%TEMP%\~input.vbs
echo "   [3] Disk Cleanup                   "+vbNewLine+ _>>%TEMP%\~input.vbs
echo "   [4] Disk Defragment                "+vbNewLine+ _>>%TEMP%\~input.vbs
echo "   [5] JDE Cleanup Log                "+vbNewLine+ _>>%TEMP%\~input.vbs
echo "                                      "+vbNewLine+ _>>%TEMP%\~input.vbs
echo "   [6] Exit                           ",           _>>%TEMP%\~input.vbs
echo "PC Cleanup Utility                    "            )>>%TEMP%\~input.vbs
for /f "delims=/" %%G IN ('cscript //nologo %TEMP%\~input.vbs') DO set _string=%%G
del %TEMP%\~input.vbs
if %_string%==1 goto 1
if %_string%==2 goto 2
if %_string%==3 goto 3
if %_string%==4 goto 4
if %_string%==5 goto 5
if %_string%==6 goto exit
goto error

:1
cls
echo --------------------------------------------------------------------------------
echo Delete Internet Cookies
echo --------------------------------------------------------------------------------
echo.
echo Deleting Cookies...
ping localhost -n 3 >nul
del /f /q "%userprofile%\Cookies\*.*"
cls
echo --------------------------------------------------------------------------------
echo Delete Internet Cookies
echo --------------------------------------------------------------------------------
echo.
echo Cookies deleted.
echo.
ping localhost -n 3 >nul
goto menu

:2
cls
echo --------------------------------------------------------------------------------
echo Delete Temporary Internet Files
echo --------------------------------------------------------------------------------
echo.
echo Deleting Temporary Files...
echo.
del /f /q "%userprofile%\AppData\Local\Microsoft\Windows\Temporary Internet Files\*.*"
cls
echo --------------------------------------------------------------------------------
echo Delete Temporary Internet Files
echo --------------------------------------------------------------------------------
echo.
echo Temporary Internet Files deleted.
echo.
ping localhost -n 3 >nul
goto menu

:3
cls
echo --------------------------------------------------------------------------------
echo Disk Cleanup
echo --------------------------------------------------------------------------------
echo.
echo Running Disk Cleanup...
if exist "C:\WINDOWS\temp" del /f /q "C:WINDOWS\temp\*.*"
if exist "C:\WINDOWS\tmp" del /f /q "C:\WINDOWS\tmp\*.*"
if exist "C:\tmp" del /f /q "C:\tmp\*.*"
if exist "C:\temp" del /f /q "C:\temp\*.*"
if exist "%temp%" del /f /q "%temp%\*.*"
if exist "%tmp%" del /f /q "%tmp%\*.*"
if not exist "C:\WINDOWS\Users\*.*" goto skip
if exist "C:\WINDOWS\Users\*.zip" del "C:\WINDOWS\Users\*.zip" /f /q
if exist "C:\WINDOWS\Users\*.exe" del "C:\WINDOWS\Users\*.exe" /f /q
if exist "C:\WINDOWS\Users\*.gif" del "C:\WINDOWS\Users\*.gif" /f /q
if exist "C:\WINDOWS\Users\*.jpg" del "C:\WINDOWS\Users\*.jpg" /f /q
if exist "C:\WINDOWS\Users\*.png" del "C:\WINDOWS\Users\*.png" /f /q
if exist "C:\WINDOWS\Users\*.bmp" del "C:\WINDOWS\Users\*.bmp" /f /q
if exist "C:\WINDOWS\Users\*.avi" del "C:\WINDOWS\Users\*.avi" /f /q
if exist "C:\WINDOWS\Users\*.mpg" del "C:\WINDOWS\Users\*.mpg" /f /q
if exist "C:\WINDOWS\Users\*.mpeg" del "C:\WINDOWS\Users\*.mpeg" /f /q
if exist "C:\WINDOWS\Users\*.ra" del "C:\WINDOWS\Users\*.ra" /f /q
if exist "C:\WINDOWS\Users\*.ram" del "C:\WINDOWS\Users\*.ram"/f /q
if exist "C:\WINDOWS\Users\*.mp3" del "C:\WINDOWS\Users\*.mp3" /f /q
if exist "C:\WINDOWS\Users\*.mov" del "C:\WINDOWS\Users\*.mov" /f /q
if exist "C:\WINDOWS\Users\*.qt" del "C:\WINDOWS\Users\*.qt" /f /q
if exist "C:\WINDOWS\Users\*.asf" del "C:\WINDOWS\Users\*.asf" /f /q
:skip
if not exist C:\WINDOWS\Users\Users\*.* goto skippy /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.zip del C:\WINDOWS\Users\Users\*.zip /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.exe del C:\WINDOWS\Users\Users\*.exe /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.gif del C:\WINDOWS\Users\Users\*.gif /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.jpg del C:\WINDOWS\Users\Users\*.jpg /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.png del C:\WINDOWS\Users\Users\*.png /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.bmp del C:\WINDOWS\Users\Users\*.bmp /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.avi del C:\WINDOWS\Users\Users\*.avi /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.mpg del C:\WINDOWS\Users\Users\*.mpg /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.mpeg del C:\WINDOWS\Users\Users\*.mpeg /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.ra del C:\WINDOWS\Users\Users\*.ra /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.ram del C:\WINDOWS\Users\Users\*.ram /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.mp3 del C:\WINDOWS\Users\Users\*.mp3 /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.asf del C:\WINDOWS\Users\Users\*.asf /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.qt del C:\WINDOWS\Users\Users\*.qt /f /q
if exist C:\WINDOWS\Users\AppData\Temp\*.mov del C:\WINDOWS\Users\Users\*.mov /f /q
:skippy
if exist "C:\WINDOWS\ff*.tmp" del C:\WINDOWS\ff*.tmp /f /q
if exist C:\WINDOWS\ShellIconCache del /f /q "C:\WINDOWS\ShellI~1\*.*"
cls
echo --------------------------------------------------------------------------------
echo Disk Cleanup
echo --------------------------------------------------------------------------------
echo.
echo Disk Cleanup successful!
echo.
ping localhost -n 3 >nul
goto menu

:4
cls
echo --------------------------------------------------------------------------------
echo Disk Defragment
echo --------------------------------------------------------------------------------
echo.
echo Defragmenting hard disks...
defrag -c -v
cls
echo --------------------------------------------------------------------------------
echo Disk Defragment
echo --------------------------------------------------------------------------------
echo.
echo Disk Defrag successful!
echo.
ping localhost -n 3 >nul
goto menu

:5
cls
echo --------------------------------------------------------------------------------
echo Delete JDE log files
echo --------------------------------------------------------------------------------
echo.
echo Delete JDE log files...
del /f /q "c:\jde*.log"
cls
echo --------------------------------------------------------------------------------
echo Delete JDE log files
echo --------------------------------------------------------------------------------
echo.
echo JDE Log deleted.
echo.
ping localhost -n 3 >nul
goto menu

:error
cls
echo Command not recognized.
ping localhost -n 4 >nul
goto menu

:exit
echo Thanks for using PC Cleanup Utility by GPM
endlocal & set _input=%_string%