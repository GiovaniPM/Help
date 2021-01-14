#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"
export backdir=$(pwd)
export file=./upload.per

if [ "X$1" != "XD" ] && [ "X$1" != "Xd" ] && [ "X$1" != "XU" ] && [ "X$1" != "Xu" ]; then 
  echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
  echo -e $IGreen"  Usage: $directory"$Color_Off
  echo -e $IGreen"    D - Download directories $directory"$Color_Off
  echo -e $IGreen"    U - Upload directories $directory"$Color_Off
  echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
  exit
fi

for directory in $(ls -d */)
do
  if [ "$directory" != "." ] &&  [ "$directory" != ".." ]; then
    echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
    echo -e $IGreen"  Directory: $directory"$Color_Off
    echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
    if [ "X$1" == "XD" ] ||  [ "X$1" == "Xd" ]; then
      cd $directory
      ~/download.sh
      cd $backdir
    fi
    if [ "X$1" == "XU" ] ||  [ "X$1" == "Xu" ]; then
      cd $directory
      if test -f "$file"; then
        ~/upload.sh
      fi
      cd $backdir
    fi
  fi
done