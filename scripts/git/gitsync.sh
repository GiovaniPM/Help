#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

backdir=$(pwd)

for directory in $(ls -lias | cut -c75-)
do
  if [ "$directory" != "." ]; then
    if [ "$directory" != ".." ]; then
      echo "--------------------------------------------------------------------------------------"
      echo "  Directory: $directory"
      echo "--------------------------------------------------------------------------------------"
      if [ "X$1" == "XD" ]; then
        cd $directory
        ~/download.sh $directory
        cd $backdir
      fi
      if [ "X$1" == "XU" ]; then
        cd $directory
        ~/upload.sh $directory
        cd $backdir
      fi
    fi
  fi
done