'''
   Oracle auxiliar library
'''
import configparser
import cx_Oracle
import fineasylib
import os

def createConnection(environment):
    '''
       Get a connection with the Oracle.
    
       Parameters:

           environment = Kind of environment ('PRD', 'HLG_79', 'HLG_53')

       Ex.: client = createConnection('PRD')
    '''

    try:
        ora_host        = os.environ.get('ORACLE_DB_HOST'     )
        ora_port        = os.environ.get('ORACLE_DB_PORT'     )
        ora_servicename = os.environ.get('ORACLE_SERVICE_NAME')
        ora_user        = os.environ.get('ORACLE_DB_USER'     )
        ora_pass        = os.environ.get('ORACLE_DB_PASS'     )
    except:
        ora_host        = None
        ora_port        = None
        ora_servicename = None
        ora_user        = None
        ora_pass        = None

    try:
        files = [
            'oracle.ini'
        ]
        labels = [
            {'label': environment, 'key': 'db_host'        , 'default': ora_host       },
            {'label': environment, 'key': 'db_port'        , 'default': ora_port       },
            {'label': environment, 'key': 'db_servicename' , 'default': ora_servicename},
            {'label': environment, 'key': 'db_user'        , 'default': ora_user       },
            {'label': environment, 'key': 'db_pass'        , 'default': ora_pass       }
        ]

        config = fineasylib.INIValues(files,labels)

        db_host        = config['db_host'        ]
        db_port        = config['db_port'        ]
        db_servicename = config['db_servicename' ]
        db_user        = config['db_user'        ]
        db_pass        = config['db_pass'        ]
    except:
        db_host        = ora_host       
        db_port        = ora_port       
        db_servicename = ora_servicename
        db_user        = ora_user       
        db_pass        = ora_pass       

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

    return cx_Oracle.connect(user=db_user, password=db_pass, dsn=conn_string, encoding='UTF-8')


def loadOracleResult(env, titles, query, parametros=[]):
    """Return a JSON over a request

    Args:
        env (string): environment
        titles (string): as keys titulos
        query (string): SQL query
        parametros (dict): binders

    Returns:
        dict: Result
    """
    conn = createConnection(env)
    cur  = conn.cursor()

    sql_string = query

    if parametros != []:
        cur.prepare(sql_string)
        cur.execute(None, parametros)
    else:
        cur.execute(sql_string)

    cursor = []

    for lin in cur.fetchall():
        reg = {}
        col = 0
        for name in titles:
            reg[name] = lin[col]
            col += 1
        cursor.append(reg)

    conn.close()

    return cursor

def addWhere(where, link, condition, field):
    if fineasylib.emptyField(field) == False:
        if where != '':
            where += ' ' + link + ' ' + condition
        else:
            where += ' ' + condition

    return where

def addBind(bind, field, name):
    if fineasylib.emptyField(field) == False:
        bind[name] = field

    return bind