import argparse
import cx_Oracle

parser = argparse.ArgumentParser(description = 'Consulta UDC')
parser.add_argument('--sy', action = 'store', dest = 'sy', required = True, help = 'System code ex.: 57')
parser.add_argument('--rt', action = 'store', dest = 'rt', required = True, help = 'RT code ex.: US')
args = parser.parse_args()

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

sql_string = "SELECT\
                  DRSY,\
                  DRRT,\
                  DRKY,\
                  DRDL01,\
                  DRDL02,\
                  DRSPHD,\
                  DRHRDC\
              FROM\
                  PRODCTLXE.F0005\
              WHERE\
                  RTRIM(LTRIM(DRSY,' '),' ') = :sy\
                  AND DRRT = :rt\
              ORDER BY\
                  DRSY,\
                  DRRT"

cur = con.cursor()
cur.execute(sql_string, sy=args.sy, rt=args.rt)
data_set = cur.fetchall()

print('+------+----+------------+--------------------------------+--------------------------------+------------+------+')
print('| SY   | RT | KY         | DL01                           | DL02                           | SPHD       | HRDC |')
print('+------+----+------------+--------------------------------+--------------------------------+------------+------+')

for linha in data_set:

    print('  %s   %s   %s   %s   %s   %s   %s' % (linha[0],\
                                                  linha[1],\
                                                  linha[2],\
                                                  linha[3],\
                                                  linha[4],\
                                                  linha[5],\
                                                  linha[6]))

print('+------+----+------------+--------------------------------+--------------------------------+-------------+------+')

con.close()