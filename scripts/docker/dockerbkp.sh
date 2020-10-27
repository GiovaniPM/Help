#!/bin/bash

export IYellow="\033[0;93m"
export Color_Off="\033[0m"
export IGreen="\033[0;92m"
export On_Green="\033[42m"

#docker ps -a --format "table{{.ID}} {{.Image}}" > ./temp.txt
#docker images --format "table{{.Repository}}" > ./temp.txt
docker images --format "{{.Repository}}" > ./temp.txt

i=1

clear
echo -e 'Option\tImage'
echo -e '======\t==========================================================='

for t in $(cat ./temp.txt); do
    echo -e $IYellow$i$Color_Off'\t'$IGreen$t$Color_Off
    let i=i+1
done

echo -e '==================================================================='
echo -e 'Select the option to backup (0 to all images):'
read option

clear
i=1

for t in $(cat ./temp.txt); do
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
    let i=i+1
done

rm ./temp.txt