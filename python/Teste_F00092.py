import cx_Oracle
import sys

# Reset
Color_Off="\033[0m"       # Text Reset
Reset="\033[0;0m"         # Text Reset
Bold="\033[;1m"           # Bold
Reverse="\033[;7m"        # Reverse

# Regular Colors
Black="\033[0;30m"        # Black
Red="\033[0;31m"          # Red
Green="\033[0;32m"        # Green
Yellow="\033[0;33m"       # Yellow
Blue="\033[0;34m"         # Blue
Purple="\033[0;35m"       # Purple
Cyan="\033[0;36m"         # Cyan
White="\033[0;37m"        # White

# Bold
BBlack="\033[1;30m"       # Black
BRed="\033[1;31m"         # Red
BGreen="\033[1;32m"       # Green
BYellow="\033[1;33m"      # Yellow
BBlue="\033[1;34m"        # Blue
BPurple="\033[1;35m"      # Purple
BCyan="\033[1;36m"        # Cyan
BWhite="\033[1;37m"       # White

# Underline
UBlack="\033[4;30m"       # Black
URed="\033[4;31m"         # Red
UGreen="\033[4;32m"       # Green
UYellow="\033[4;33m"      # Yellow
UBlue="\033[4;34m"        # Blue
UPurple="\033[4;35m"      # Purple
UCyan="\033[4;36m"        # Cyan
UWhite="\033[4;37m"       # White

# Background
On_Black="\033[40m"       # Black
On_Red="\033[41m"         # Red
On_Green="\033[42m"       # Green
On_Yellow="\033[43m"      # Yellow
On_Blue="\033[44m"        # Blue
On_Purple="\033[45m"      # Purple
On_Cyan="\033[46m"        # Cyan
On_White="\033[47m"       # White

# High Intensty
IBlack="\033[0;90m"       # Black
IRed="\033[0;91m"         # Red
IGreen="\033[0;92m"       # Green
IYellow="\033[0;93m"      # Yellow
IBlue="\033[0;94m"        # Blue
IPurple="\033[0;95m"      # Purple
ICyan="\033[0;96m"        # Cyan
IWhite="\033[0;97m"       # White

# Bold High Intensty
BIBlack="\033[1;90m"      # Black
BIRed="\033[1;91m"        # Red
BIGreen="\033[1;92m"      # Green
BIYellow="\033[1;93m"     # Yellow
BIBlue="\033[1;94m"       # Blue
BIPurple="\033[1;95m"     # Purple
BICyan="\033[1;96m"       # Cyan
BIWhite="\033[1;97m"      # White

# High Intensty backgrounds
On_IBlack="\033[0;100m"   # Black
On_IRed="\033[0;101m"     # Red
On_IGreen="\033[0;102m"   # Green
On_IYellow="\033[0;103m"  # Yellow
On_IBlue="\033[0;104m"    # Blue
On_IPurple="\033[10;95m"  # Purple
On_ICyan="\033[0;106m"    # Cyan
On_IWhite="\033[0;107m"   # White

db_host = 'prd-jdepnsc.nsccorp.net'
db_port = 1544
db_servicename = 'jdepnsc'
db_user = 'giovani_mesquita'
db_pass = 'wJBP475N'

conn_string = "\
               (DESCRIPTION =\
                    (ADDRESS_LIST =\
                        (ADDRESS = (PROTOCOL = TCP)\
                            (HOST = %s)\
                            (PORT = %s))\
                        )\
                    (CONNECT_DATA =\
                        (SERVICE_NAME = %s)\
                    )\
                )" % (db_host, str(db_port), db_servicename)

con = cx_Oracle.connect(user=db_user, password=db_pass, dsn=conn_string, encoding='UTF-8')

posicao = 0
par = 1

sql_string = "SELECT\
                  T3SDB,\
                  T3TYDT,\
                  to_char(to_date(T3EFT+1900000,'YYYYDDD'),'DD/MM/YY'),\
                  to_char(to_date(T3EFTE+1900000,'YYYYDDD'),'DD/MM/YY'),\
                  to_char(T3RMK3,'9999'),\
                  T3RMK,\
                  T3KY,\
                  T3RMK2,\
                  T3UKID\
              FROM\
                  PRODDTAXE.F00092\
              WHERE\
                  T3SDB = 'REQ '\
                  AND T3TYDT = 'OM'"
sql_cond = sql_string + ' AND T3RMK3 >= ''%s''' % (str(posicao))
cur = con.cursor()
cur.execute(sql_cond)
data_set = cur.fetchall()
linhas = cur.rowcount
cur.close()
print('+------+------+--------+--------+------+--------------------------------+------------+--------------------------------+------+')
print('| SDB  | TYDT | EFT    | EFTE   | RMK3 | RMK                            | KY         | RMK2                           | UKID |')
print('+------+------+--------+--------+------+--------------------------------+------------+--------------------------------+------+')

while (linhas > 0):
    sql_cond = sql_string + ' AND T3RMK3 = ''%s''' % (str(posicao))
    cur = con.cursor()
    cur.execute(sql_cond)
    data_set = cur.fetchall()
    if cur.rowcount > 0:
        for linha in data_set:
            if (par == 1):
                sys.stdout.write(IBlue)
                par = 0
            else:
                sys.stdout.write(IGreen)
                par = 1
            print('  %s   %s    %s %s %s   %s   %s   %s   %s   ' % (linha[0],\
                                                                    linha[1],\
                                                                    linha[2],\
                                                                    linha[3],\
                                                                    linha[4],\
                                                                    linha[5],\
                                                                    linha[6],\
                                                                    linha[7],\
                                                                    linha[8]))
    cur.close()

    posicao = posicao + 1
    sql_cond = sql_string + ' AND T3RMK3 >= ''%s''' % (str(posicao))
    cur = con.cursor()
    cur.execute(sql_cond)
    data_set = cur.fetchall()
    linhas = cur.rowcount
    cur.close()

sys.stdout.write(Color_Off)

print('+------+------+--------+--------+------+--------------------------------+------------+--------------------------------+------+')
con.close()