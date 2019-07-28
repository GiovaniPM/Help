#!/bin/sh
#=====================================================================================================
#= Created by Giovani Perotto Mesquita                                                               =
#=====================================================================================================
if [ "X$1" == "X--help" ]
then
  echo -e '+-\033[41;30;4m Proposal: \033[m--------------------------------------------------------------------------------------------------------+'
  echo -e '|                                                                                                                    |'
  echo -e '|    To help push archives into Git repository in simple way.                                                        |'
  echo -e '|                                                                                                                    |'
  echo -e '+-\033[41;30;4m Usage: \033[m-----------------------------------------------------------------------------------------------------------+'
  echo -e '|                                                                                                                    |'
  echo -e '|    ./upload.sh <file> <comment for commit>                                                                         |'
  echo -e '|                                                                                                                    |'
  echo -e '+-\033[41;30;4m Examples: \033[m--------------------------------------------------------------------------------------------------------+'
  echo -e '|                                                                                                                    |'
  echo -e '|    ./upload.sh . "My_first_commit" \033[40;30;1m-- Upload all local files to server with the comment "My_first_commit"\033[m          |'
  echo -e '|    ./upload.sh                     \033[40;30;1m-- Upload all local files to server with default comment\033[m                        |'
  echo -e '|    ./upload.sh upload.sh           \033[40;30;1m-- Upload file upload.sh to server with default comment\033[m                         |'
  echo -e '+--------------------------------------------------------------------------------------------------------------------+'
else
  if [ "X$1" == "X" ]
  then
    git add .
  else
    git add $1
  fi
  if [ "X$2" == "X" ]
  then
    git commit -m $USERNAME'('$HOSTNAME') '`date +%y%m%d%H%M%S`
  else
    git commit -m $2
  fi
  git push
fi