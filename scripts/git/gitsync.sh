#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"
export backdir=$(pwd)

for directory in $(ls -a)
do
  if [ "$directory" != "." ]; then
    if [ "$directory" != ".." ]; then
      echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
      echo -e $IGreen"  Directory: $directory"$Color_Off
      echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
      if [ "X$1" == "XD" ]; then
        cd $directory
        ~/download.sh
        cd $backdir
      fi
      if [ "X$1" == "XU" ]; then
        cd $directory
        ~/upload.sh
        cd $backdir
      fi
    fi
  fi
done