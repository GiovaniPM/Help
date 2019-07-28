#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================
echo -e '+-\033[41;30;4m Setup: \033[m----------------------------------------------------------------+'
echo -e '|                                                                         |'
echo -e '|    Setup directory                                                      |'
echo -e '|                                                                         |'
echo -e '+-------------------------------------------------------------------------+'

export gitdir="Help"
export gitlink="https://github.com/GiovaniPM/$gitdir.git"
export IYellow="\033[0;93m"
export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"

echo -e "->$IYellow $gitlink $Color_Off"

if [ -d "../$gitdir" ]; then
  echo -e "->$IYellow Getting code actual directory $Color_Off"
  git pull
  cd ..
else
  if [ -d "./$gitdir" ]; then
    echo -e "->$IYellow Getting code $Color_Off"
    cd $gitdir
    git pull
    cd ..
  else
    echo -e "$IYellow Cloning $Color_Off"
    git clone $gitlink Help
    echo -e "->$IYellow Getting code $Color_Off"
    cd $gitdir
    git pull
    cd ..
  fi
fi

echo -e "->$On_Green Finished $Color_Off"