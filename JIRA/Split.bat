@echo off
rem Splits a file into pieces of a given size (see Split.ps1 for details).
rem Usage: Split.bat <file> <size> [outputDir]
rem Example: Split.bat bigfile.log 10MB

if "%~2"=="" (
    echo Usage: %~nx0 ^<file^> ^<size^> [outputDir]
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Split.ps1" "%~1" "%~2" "%~3"
