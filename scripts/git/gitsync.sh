#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

export backdir=$(pwd)

for directory in $(ls -lias | cut -c75-)
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