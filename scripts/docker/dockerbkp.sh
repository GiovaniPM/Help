#!/bin/bash

export IYellow="\033[0;93m"
export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"
re='^[0-9]+$'
i=1

#docker ps -a --format "table{{.ID}} {{.Image}}" > ./temp.txt
#docker images --format "table{{.Repository}}" > ./temp.txt
docker images --format "{{.Repository}}" > ./temp.txt

clear
echo -e '============================================================================='
echo -e 'Option Image                          | Option Image                         '
echo -e '====== ============================== | ====== =============================='

linstr=''
srtpar=0
for t in $(cat ./temp.txt); do
    spaces=$(printf '%0.1s' '.'{1..10})
    numstr=$i$spaces
    numstr=${numstr:0:6}
    spaces=$(printf '%0.1s' '.'{1..30})
    optstr=$t$spaces
    optstr=${optstr:0:30}
    string=$(echo -e $IYellow$numstr$Color_Off' '$IGreen$optstr$Color_Off)
    if [[ $strpar -eq 0 ]]; then
        linstr=$string
        strpar=1
    else
        linstr=$linstr' | '$string
        echo $linstr
        linstr=''
        strpar=0
    fi
    let i=i+1
done
if [[ $strpar -eq 1 ]]; then
    echo $linstr
fi

echo -e '============================================================================='
echo -e 'Select the option to backup ('0' backup all images): \c'
read option

clear
i=1

for t in $(cat ./temp.txt); do
    if [[ $option =~ $re ]] ; then
        if [ $i -eq $option -o $option -eq 0 ]; then
            filename=$t
            imagename=$t
            textfrom="/"
            textto="_"
            filename="${filename//$textfrom/$textto}"
            textfrom="."
            textto="_"
            filename="${filename//$textfrom/$textto}"
            echo -e $imagename' --> '$filename.img'\c'
            docker save -o $filename.img $imagename
            echo -e '\a ('$On_Green'ok'$Color_Off')'
        fi
    fi
    let i=i+1
done

rm ./temp.txt