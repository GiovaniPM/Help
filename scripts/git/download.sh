#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================
if [ "X$1" == "X--help" ]
then
  echo -e '+-\033[41;30;4m Proposal: \033[m--------------------------------------------------------------------------------------------------------+'
  echo -e '|                                                                                                                    |'
  echo -e '|    To help pull archives from Git repository in simple way.                                                        |'
  echo -e '|                                                                                                                    |'
  echo -e '+-\033[41;30;4m Usage: \033[m-----------------------------------------------------------------------------------------------------------+'
  echo -e '|                                                                                                                    |'
  echo -e '|    ./download.sh <repository>                                                                                      |'
  echo -e '|                                                                                                                    |'
  echo -e '+-\033[41;30;4m Examples: \033[m--------------------------------------------------------------------------------------------------------+'
  echo -e '|                                                                                                                    |'
  echo -e '|    ./download.sh JDE-Query \033[40;30;1m-- Download all files from server\033[m                                                       |'
  echo -e '|    ./download.sh           \033[40;30;1m-- Download all files from server using current local repo\033[m                              |'
  echo -e '+--------------------------------------------------------------------------------------------------------------------+'
else
  echo -e '\033[1;49;34m+-\033[0;106;97m Setup: \033[1;49;34m----------------------------------------------------------------+\033[m'
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
  
  #echo -e "->\033[0;106;97m $gitlink \033[m"
  
  if [ -d "../$gitdir" ]; then
    echo -e "->\033[0;103;30m Getting code actual directory \033[m"
    echo -e "\033[0;49;92m"
    git pull
    echo -e "\033[m"
    cd ..
  else
    if [ -d "./$gitdir" ]; then
      echo -e "->\033[0;103;30m Getting code \033[m"
      cd $gitdir
      echo -e "\033[0;49;92m"
      git pull
      echo -e "\033[m"
      cd ..
    else
      echo -e "->\033[0;103;30m Cloning \033[m"
      echo -e "\033[0;49;92m"
      git clone $gitlink $gitdir
      echo -e "\033[m"
    fi
  fi
  
  echo -e "->\033[0;106;97m Finished \033[m"
fi
