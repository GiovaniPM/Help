#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export IYellow="\033[0;93m"
export On_Green="\033[42m"
export backdir=$(pwd)
export fileU=./upload.per
export fileD=./download.per

if [ "X$1" != "XD" ] && [ "X$1" != "Xd" ] && [ "X$1" != "XU" ] && [ "X$1" != "Xu" ]; then 
  echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
  echo -e $IGreen"  Usage: $directory"$Color_Off
  echo -e $IGreen"    $IYellow gitsync D - $On_Green Download directories $directory"$Color_Off
  echo -e $IGreen"    $IYellow gitsync U - $On_Green Upload directories   $directory"$Color_Off
  echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
  echo -e $IGreen"  Tokens:"$Color_Off
  echo -e $IGreen"    $IYellow $fileU   - $On_Green Put this file inside the directory to denie upload"$Color_Off
  echo -e $IGreen"    $IYellow $fileD - $On_Green Put this file inside the directory to denie download"$Color_Off
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
      if test -f "$fileD"; then
        ~/download.sh
      else
        echo "Bypassed by flag -> download.per"
      fi
      cd $backdir
    fi
    if [ "X$1" == "XU" ] ||  [ "X$1" == "Xu" ]; then
      cd $directory
      if test -f "$fileU"; then
        ~/upload.sh
      else
        echo "Bypassed by flag -> upload.per"
      fi
      cd $backdir
    fi
  fi
done