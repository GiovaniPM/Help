#!/bin/bash
BASEDIR=`echo ~`
PROJDIR=$BASEDIR/"Projetos"
HELPDIR=$PROJDIR/"Help"
GITDIR=$HELPDIR"/scripts/git"

if ! [ -d "${PROJDIR}" ]
then
    mkdir $PROJDIR
fi

if ! [ -d "${HELPDIR}" ]
then
    cd ${PROJDIR}
    git clone https://github.com/GiovaniPM/Help.git
    cp $GITDIR/*.sh $PROJDIR/.
    chmod 777 $PROJDIR/*.sh
fi

if ! [ -x "$(command -v choco)" ]; then
  scriptchoco = "'https://chocolatey.org/install.ps1'"
  echo 'Error: choco is not installed.'
  echo '  Run the follow line:'
  #echo '  - "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"'
  echo '  - "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString("$scriptchoco"))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"'
  exit
fi

if ! [ -x "$(command -v code)" ]; then
  echo 'Error: vscode is not installed.'
  choco install vscode -y
fi

echo "BASEDIR="$BASEDIR
echo "PROJDIR="$PROJDIR
echo "HELPDIR="$HELPDIR
echo "GITDIR="$GITDIR