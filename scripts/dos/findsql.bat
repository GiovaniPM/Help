@ echo off
type %1 | findstr /C:"SELECT " /C:"UPDATE " /C:"DELETE " /C:"INSERT " > temp.txt
more temp.txt
del temp.txt