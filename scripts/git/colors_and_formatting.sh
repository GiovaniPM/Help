#!/bin/bash

rotulos=('Black          ' 'Red            ' 'Green          ' 'Yellow         ' 'Blue           ' 'Magenta        ' 'Cyan           ' 'White          ' 'Default        ' 'Bright Black   ' 'Bright Red     ' 'Bright Green   ' 'Bright Yellow  ' 'Bright Blue    ' 'Bright Magenta ' 'Bright Cyan    ' 'Bright White   ')
indice=0
titulo="                  Normal      Intense     Weak        Italic      Underline   Blink       Inverse     Invisible   Strike"
#titulo="                  Normal      Intenso     Fraco       Italico     Sublinhado  Piscando    Inverso     Invisivel   Tachado"

#Background
for clbg in {40..47} 49 {100..107}; do
    #Foreground
    echo -e "$titulo"
    for clfg in {30..37} 39 {90..97}; do
        #headline
        echo -en "${rotulos[indice]} \e[0m "
        if test $indice -ge 16; then
            let indice=0
        else
            let indice++
        fi
        #Formatting
        for attr in 0 1 2 3 4 5 7 8 9; do
            if test $clbg -le 99; then
                echo -en "\e[${attr};${clbg};${clfg}m ${attr};${clbg};${clfg}m  \e[0m "
            else
                echo -en "\e[${attr};${clbg};${clfg}m ${attr};${clbg};${clfg}m \e[0m "
            fi
        done
        #Newline
        echo 
    done
    #Newline
    echo 
done

echo -en "\e[2;40;30m xx2;40;30mxxx \e[2;40;90m xx2;40;90mxx \e[0;40;30m xx0;40;30mxx \e[1;40;30m xx1;40;30mxx ";echo -en "\e[0m";echo
echo -en "\e[2;40;31m xx2;40;31mxxx \e[2;40;91m xx2;40;91mxx \e[0;40;31m xx0;40;31mxx \e[1;40;31m xx1;40;31mxx ";echo -en "\e[0m";echo
echo -en "\e[2;40;32m xx2;40;32mxxx \e[2;40;92m xx2;40;92mxx \e[0;40;32m xx0;40;32mxx \e[1;40;32m xx1;40;32mxx ";echo -en "\e[0m";echo
echo -en "\e[2;40;33m xx2;40;33mxxx \e[2;40;93m xx2;40;93mxx \e[0;40;33m xx0;40;33mxx \e[1;40;33m xx1;40;33mxx ";echo -en "\e[0m";echo
echo -en "\e[2;40;34m xx2;40;34mxxx \e[2;40;94m xx2;40;94mxx \e[0;40;34m xx0;40;34mxx \e[1;40;34m xx1;40;34mxx ";echo -en "\e[0m";echo
echo -en "\e[2;40;35m xx2;40;35mxxx \e[2;40;95m xx2;40;95mxx \e[0;40;35m xx0;40;35mxx \e[1;40;35m xx1;40;35mxx ";echo -en "\e[0m";echo
echo -en "\e[2;40;36m xx2;40;36mxxx \e[2;40;96m xx2;40;96mxx \e[0;40;36m xx0;40;36mxx \e[1;40;36m xx1;40;36mxx ";echo -en "\e[0m";echo
echo -en "\e[2;40;37m xx2;40;37mxxx \e[2;40;97m xx2;40;97mxx \e[0;40;37m xx0;40;37mxx \e[1;40;37m xx1;40;37mxx ";echo -en "\e[0m";echo

echo

echo -en "\e[0;40m                \e[0;100m                ";echo -en "\e[0m";echo
echo -en "\e[0;41m                \e[0;101m                ";echo -en "\e[0m";echo
echo -en "\e[0;42m                \e[0;102m                ";echo -en "\e[0m";echo
echo -en "\e[0;43m                \e[0;103m                ";echo -en "\e[0m";echo
echo -en "\e[0;44m                \e[0;104m                ";echo -en "\e[0m";echo
echo -en "\e[0;45m                \e[0;105m                ";echo -en "\e[0m";echo
echo -en "\e[0;46m                \e[0;106m                ";echo -en "\e[0m";echo
echo -en "\e[0;47m                \e[0;107m                ";echo -en "\e[0m";echo

exit 0