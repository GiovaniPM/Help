#!/bin/bash
#
#
# Author :
#	Suraj Singh Bisht
#	surajsinghbisht054@gmail.com
#	www.bitforestinfo.com
#	github.com/surajsinghbisht054
#
#
# ====================================================
#         Please Don't Remove Author name
# ====================================================
#
#
#	Description:
#		ASCII Table Print Bash Script

# Welcome Banner For Script
printf "#############################################################\n" > /tmp/$0
printf "                       ASCII TABLE \n" >> /tmp/$0
printf "#############################################################\n" >> /tmp/$0
printf "                         |      Suraj Singh Bisht            \n" >> /tmp/$0
printf "                         |      surajsinghbisht054@gmail.com \n" >> /tmp/$0
printf "                         |      www.bitforestinfo.com        \n" >> /tmp/$0
printf "[------------------------------------------------------------]\n" >> /tmp/$0
printf "[       Use q To Exit, And Arrow UP and Down To Scroll       ]\n" >> /tmp/$0
printf "[------------------------------------------------------------]\n" >> /tmp/$0
# table row format to print
format="%-10d | %-10x | %-10o | %s"

# table column heading format
printf "%-10s | %-10s | %-10s | %-10s\n" Digit Hexadecimal octadecimal Char >> /tmp/$0

# table divider line
printf '==============================================\n' >> /tmp/$0

# loop 1 to 175
for num in $(seq 1 175) 
do 
	printf "$format\n" $num $num $num $(printf '\x'$num) >> /tmp/$0 
done
# show complete output and pipe it into less command tool
cat /tmp/$0 | less