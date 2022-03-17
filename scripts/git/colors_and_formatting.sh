#!/bin/bash

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.


rotulos=('Black          ' 'Red            ' 'Green          ' 'Yellow         ' 'Blue           ' 'Magenta        ' 'Cyan           ' 'White          ' 'Default        ' 'Bright Black   ' 'Bright Red     ' 'Bright Green   ' 'Bright Yellow  ' 'Bright Blue    ' 'Bright Magenta ' 'Bright Cyan    ' 'Bright White   ')
indice=0
titulo="                  Normal      Intense     Weak        Italic      Underline   Blink       Inverse     Invisible   Strike"
#titulo="                  Normal      Intenso     Fraco       Italico     Sublinhado  Piscando    Inverso     Invisivel   Tachado"

#Background
for clbg in {40..47} 49 {100..107}; do
	#Foreground
    echo -e "$titulo"
	for clfg in {30..37} 39 {90..97}; do
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
		echo #Newline
	done
	echo #Newline
done

exit 0