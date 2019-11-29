#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"
export backdir=$(pwd)

for directory in $(ls -lias | cut -c75-)
do
  if [ "$directory" != "." ]; then
    if [ "$directory" != ".." ]; then
      echo "$IGreen--------------------------------------------------------------------------------------"
      echo "  Directory: $directory"
      echo "--------------------------------------------------------------------------------------$Color_Off"
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