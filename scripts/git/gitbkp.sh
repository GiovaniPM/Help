#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================

export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"
export backdir=$(pwd)

DIR="BKP"
if [ ! -d "$DIR" ]; then
  mkdir "$DIR"
fi

for directory in $(ls -a)
do
  if [ "$directory" != "." ] &&  [ "$directory" != ".." ] &&  [ "$directory" != "BKP" ]; then
    echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
    echo -e $IGreen"  Directory: $directory"$Color_Off
    echo -e $IGreen"--------------------------------------------------------------------------------------"$Color_Off
    tar --exclude=".git" -czvf ./$DIR/$directory`date +%y%m%d%H%M%S`.gz ./$directory/**
  fi
done