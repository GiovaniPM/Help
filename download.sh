#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================
echo -e '\033[1;49;34m+- Setup: ----------------------------------------------------------------+\033[m'
echo -e '\033[1;49;34m|                                                                         |\033[m'
echo -e '\033[1;49;34m|\033[m    Download repository                                                  \033[1;49;34m|\033[m'
echo -e '\033[1;49;34m|                                                                         |\033[m'
echo -e '\033[1;49;34m+-------------------------------------------------------------------------+\033[m'

if [ "X$1" == "X" ]; then
  export gitdir=${PWD##*/}
else
  export gitdir="$1"
fi

export gitlink="https://github.com/GiovaniPM/$gitdir.git"

echo -e "->\033[0;93m $gitlink \033[0m"

if [ -d "../$gitdir" ]; then
  echo -e "->\033[0;93m Getting code actual directory \033[0m"
  git pull
  cd ..
else
  if [ -d "./$gitdir" ]; then
    echo -e "->\033[0;93m Getting code \033[0m"
    cd $gitdir
    git pull
    cd ..
  else
    echo -e "->\033[0;93m Cloning \033[0m"
    git clone $gitlink $gitdir
  fi
fi

echo -e "->\033[42m Finished \033[0m"