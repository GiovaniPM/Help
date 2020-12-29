#!/bin/bash
PROJDIR="Projetos"
HELPDIR="Help"
GITDIR=$HELPDIR"/scripts/git"

if [ ! -d "${PROJDIR}" ]
then
    mkdir $PROJDIR
fi

cd ${PROJDIR}

if [ ! -d "${HELPDIR}" ]
then
    git clone https://github.com/GiovaniPM/Help.git
fi

cp $GITDIR/* ../.
chmod 777 ../*.sh