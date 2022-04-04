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
        db_host        = os.environ.get('ORACLE_DB_HOST'     )
        db_port        = os.environ.get('ORACLE_DB_PORT'     )
        db_servicename = os.environ.get('ORACLE_SERVICE_NAME')
        db_user        = os.environ.get('ORACLE_DB_USER'     )
        db_pass        = os.environ.get('ORACLE_DB_PASS'     )
        if db_host == None:
            raise Exception('The variable ORACLE_DB_HOST does not return anything!')
    except:
        config = configparser.ConfigParser()
        config.read('connection.ini')
        if environment == 'PRD':
            try:
                db_host = config['Oracle_PRD']['db_host']
                db_port = config['Oracle_PRD']['db_port']
                db_servicename = config['Oracle_PRD']['db_servicename']
                db_user = config['Oracle_PRD']['db_user']
                db_pass = config['Oracle_PRD']['db_pass']
            except:
                db_host = '10.100.97.196'
                db_port = 1521
                db_servicename = 'CRITICO'
                db_user = 'mariomatos'
                db_pass = 'Topazio21'
        elif environment == 'HLG':
            try:
                db_host = config['Oracle_HLG']['db_host']
                db_port = config['Oracle_HLG']['db_port']
                db_servicename = config['Oracle_HLG']['db_servicename']
                db_user = config['Oracle_HLG']['db_user']
                db_pass = config['Oracle_HLG']['db_pass']
            except:
                db_host = '10.100.98.74'
                db_port = 1521
                db_servicename = 'CCRITICO'
                db_user = 'baas'
                db_pass = 'baas'
        elif environment == 'HLG_79':
            try:
                db_host = config['Oracle_HLG_79']['db_host']
                db_port = config['Oracle_HLG_79']['db_port']
                db_servicename = config['Oracle_HLG_79']['db_servicename']
                db_user = config['Oracle_HLG_79']['db_user']
                db_pass = config['Oracle_HLG_79']['db_pass']
            except:
                db_host = '10.100.98.74'
                db_port = 1521
                db_servicename = 'CCRITICO'
                db_user = 'baas'
                db_pass = 'baas'
        else:
            try:
                db_host = config['Oracle_HLG_53']['db_host']
                db_port = config['Oracle_HLG_53']['db_port']
                db_servicename = config['Oracle_HLG_53']['db_servicename']
                db_user = config['Oracle_HLG_53']['db_user']
                db_pass = config['Oracle_HLG_53']['db_pass']
            except:
                db_host = '10.100.98.90'
                db_port = 1521
                db_servicename = 'LBANKING'
                db_user = 'TOPAZIO'
                db_pass = '3UR0P435'

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
    
    print(conn_string)

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