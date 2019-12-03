#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"

export backdir=$(pwd)
export bkpnm=`date +%y%m%d%H%M%S`

DIR="BKP"
if [ ! -d "$DIR" ]; then
  mkdir "$DIR"
fi

echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
echo -e $IGreen"Directories:"$Color_Off
echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
for directory in $(ls -a)
do
  if [ "$directory" != "." ] &&  [ "$directory" != ".." ] &&  [ "$directory" != "BKP" ]; then
    echo -e "  "$IGreen$directory$Color_Off
    echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off >> ./$DIR/$bkpnm.log
    echo -e $IGreen"  Directory: $directory"$Color_Off >> ./$DIR/$bkpnm.log
    echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off >> ./$DIR/$bkpnm.log
    tar --exclude=".git" -czvf ./$DIR/$bkpnm-$directory.gz ./$directory/** >> ./$DIR/$bkpnm.log
  fi
done