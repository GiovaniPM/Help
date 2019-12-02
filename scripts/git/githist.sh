#
# Creates an alias called "git hist" that outputs a nicely formatted git log.
# Usage is just like "git log"
# Examples:
#   git hist
#   git hist -5
#   git hist <branch_name>
#   git hist <tag_name> -10
##
git config --global alias.hist "log --pretty=format:'%C(yellow)[%ad]%C(reset) %C(green)[%h]%C(reset) | %C(red)%s %C(bold red){{%an}}%C(reset) %C(blue)%d%C(reset)' --graph --date=short"