#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================
echo -e '+-\033[41;30;4m Setup: \033[m-----------------------------------------------------------------------------------------------------------+'
echo -e '|                                                                                                                    |'
echo -e '|    Setup directory                                                                                                 |'
echo -e '|                                                                                                                    |'
echo -e '+--------------------------------------------------------------------------------------------------------------------+'

set gitdir=Help
echo -e "$IYellow $gitdir $Color_Off"

if [ -d "../"$gitdir]; then
  echo -e "$IYellow Getting code $Color_Off"
  git pull
  cd ..
else
  if [ -d "./$gitdir" ]; then
    echo -e "$IYellow Getting code $Color_Off"
    cd $gitdir
    git pull
    cd ..
  else
    echo -e "$IYellow Cloning $Color_Off"
    git clone https://github.com/GiovaniPM/$gitdir.git Help
    echo -e "$IYellow Getting code $Color_Off"
    cd $gitdir
    git pull
    cd ..
  fi
fi

echo -e "$IGreen Finished $Color_Off"