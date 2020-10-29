#!/bin/bash

declare -a MEU_ARRAY

i=0
for t in $(docker images --format "{{.Repository}}"); do
    MEU_ARRAY[$i]=$t
    let i=i+1
done

i=1
for t in ${MEU_ARRAY[*]}; do
    echo $i' '$t
    let i=i+1
done

spaces='1'$(printf '%0.1s' '.'{1..10})
echo $spaces