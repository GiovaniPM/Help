'''
   Mongo auxiliar library
'''
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date

import configparser
import fineasylib
import json
import os
import pymongo

def goKey(key, label):
    '''
       Get a object.
    
       Parameters:

           key   = Actual object

           label = Object to be accessed

       Ex.: key = goKey(reg, 'products')
    '''
    try:
        return key[label]
    except:
        return None

def showKey(key, label):
    '''
       Get a key value.
    
       Parameters:

           key   = Actual object

           label = Key to be accessed

       Ex.: value = showKey(ted, 'codeIdentifier')
    '''
    try:
        return str(key[label])
    except:
        return " *** UNKNOW ***"

def db_connection(environment):
    '''
       Get a connection with the MongoDB.
    
       Parameters:

           environment = Kind of environment ('PRD', 'HLG')

       Ex.: client = db_connection('PRD')
    '''

    try:
        string = eval(os.environ.get('DB_MONGO_HOST'))
    except:
        config = configparser.ConfigParser()
        config.read('connection.ini')
        if environment == 'PRD':
            try:
                string = config['MongoDB_PRD']['str_conn']
                string = string.replace("%20", "%20")
            except:
                string = 'mongodb://db_app_view:LkG72iB2W0@10.100.97.81:27017/baas?authSource=admin&replicaSet=rs0&readPreference=primary&appname=MongoDB%20Compass&ssl=false'
        else:
            try:
                string = config['MongoDB_HLG']['str_conn']
                string = string.replace("%20", "%20")
            except:
                string = 'mongodb://db_app_admin:XTZqTjv1rF@10.100.98.130:27017/admin?authSource=admin&replicaSet=rs0&readPreference=primaryPreferred&appname=MongoDB%20Compass&ssl=false'

    client = pymongo.MongoClient(string)
    
    return client

def get_collection(client, db_name, collection_name, debug=False):
    '''
       Get a collection to be used by the application, and return the collection cursor.
    
       Parameters:

           client          = MongoDB client connection

           db_name         =  The database name

           collection_name = The collection to be used

       Ex.: album = get_collection(client, 'transfer', 'externalbankslips')
    '''
    db = client[db_name]
    collection = db[collection_name]
    if debug == True:
        print(client)
        print(collection)
    return collection

def nomeCliente(client, clientId):
    '''
       Get a partner name from your clientId.
    
       Parameters:

           client          = MongoDB client connection

           clientId        =  The database name

       Ex.: Name = nomeCliente(client, '0c825c68-5b3d-3cad-bac7-0a3abd90d98f')
    '''
    filter={
        'clientId': clientId
    }
    project={
        'socialName': 1,
        'tradingName': 1
    }
    sort=list({
        'socialName': 1
    }.items())
    
    result = client['transfer']['partners'].find(
      filter=filter,
      projection=project,
      sort=sort
    )

    retorno = 'N/A'

    for i in result:
        try:
            retorno = i['socialName']
        except:
            try:
                retorno = i['tradingName']
            except:
                retorno = clientId

    return retorno

def loadMongoResult(env, database, collection, match, projection, addfield={}):
    """Return a JSON over a request

    Args:
        env (string): environment
        database (string): database
        collection (string): name of collection
        match (dict): match criteria
        projection (dict): projection
        addfield (dict): fields criteria

    Returns:
        dict: Result
    """
    client = db_connection(env)
    album  = get_collection(client, database, collection)

    pipeline = []

    if addfield != {}:
        pipeline.append({'$addFields': addfield})

    pipeline.append({'$match': match})

    if projection != []:
        project = {}
        for i in projection:
            project[i] = '$' + i

        pipeline.append({'$project': project})

    cursor = album.aggregate(pipeline, collation={ "locale": "en", "strength": 1 })

    client.close()

    return cursor

def addMatch(match, key=None, operator=None, type=None, field1=None, field2=None):
    """Add match criteria

    Args:
        match (dict): Previous criteria
        key (string): The key name
        operator (string): Type of operator 'equal', 'regex', 'in', 'between', 'exist'
        type (string, optional): Type of value 'float', 'int', 'datestr', 'str', 'obj', 'date'. Defaults to None.
        field1 (value1, optional): Value to be evaluated. Defaults to None.
        field2 (Value2, optional): Value to be evaluated. Defaults to None.

    Returns:
        dict: Match criteria.
    """
    if   type == 'float':
        if fineasylib.emptyField(field1) == False:
            field1 = float(field1)
        if fineasylib.emptyField(field2) == False:
            field2 = float(field2)
    elif type == 'int':
        if fineasylib.emptyField(field1) == False:
            field1 = int(field1)
        if fineasylib.emptyField(field2) == False:
            field2 = int(field2)
    elif type == 'str':
        if fineasylib.emptyField(field1) == False:
            field1 = str(field1)
        if fineasylib.emptyField(field2) == False:
            field2 = str(field2)
    elif type == 'obj':
        if fineasylib.emptyField(field1) == False:
            field1 = ObjectId(field1)
        if fineasylib.emptyField(field2) == False:
            field2 = ObjectId(field2)
    elif type == 'date':
        if fineasylib.emptyField(field1) == False:
            field1 = datetime(field1.year, field1.month, field1.day, 00, 00, 00, 000000) - timedelta(hours=-3)
        if fineasylib.emptyField(field2) == False:
            field2 = datetime(field2.year, field2.month, field2.day, 23, 59, 59, 999999) - timedelta(hours=-3)
    elif type == 'datestr':
        if fineasylib.emptyField(field1) == False:
            field1 = field1.strftime('%Y-%m-%d')
        if fineasylib.emptyField(field2) == False:
            field2 = field2.strftime('%Y-%m-%d')

    if   operator == 'equal':
        if fineasylib.emptyField(field1) == False:
            match[key] = field1
        elif fineasylib.emptyField(field2) == False:
            match[key] = field2
    elif operator == 'not':
        if fineasylib.emptyField(field1) == False:
            match[key] = {"$ne": field1}
        elif fineasylib.emptyField(field2) == False:
            match[key] = {"$ne": field2}
    elif operator == 'or':
        if fineasylib.emptyField(field1) == False:
            match["$or"] = field1
        elif fineasylib.emptyField(field2) == False:
            match["$or"] = field2
    elif operator == 'type':
        if fineasylib.emptyField(field1) == False:
            match[key] = {"$type": field1}
        elif fineasylib.emptyField(field2) == False:
            match[key] = {"$type": field2}
    elif operator == 'size':
        if fineasylib.emptyField(field1) == False:
            match[key] = {"$size": field1}
        elif fineasylib.emptyField(field2) == False:
            match[key] = {"$size": field2}
    elif operator == 'regex':
        if fineasylib.emptyField(field1) == False:
            match[key] = { "$regex": field1, "$options": "i" }
        elif fineasylib.emptyField(field2) == False:
            match[key] = { "$regex": field2, "$options": "i" }
    elif operator == 'in':
        if fineasylib.emptyField(field1) == False:
            reg = {}
            reg['$in'] = field1
            match[key] = reg
        elif fineasylib.emptyField(field2) == False:
            reg = {}
            reg['$in'] = field2
            match[key] = reg
    elif operator == 'nin':
        if fineasylib.emptyField(field1) == False:
            reg = {}
            reg['$nin'] = field1
            match[key] = reg
        elif fineasylib.emptyField(field2) == False:
            reg = {}
            reg['$nin'] = field2
            match[key] = reg
    elif operator == 'exist':
        if fineasylib.emptyField(field1) == False:
            match[key] = { "$exists": field1 }
        elif fineasylib.emptyField(field2) == False:
            match[key] = { "$exists": field2 }
    elif operator == 'between':
        if fineasylib.emptyField(field1) == False and fineasylib.emptyField(field2) == False:
            match[key] = { "$gte": field1, "$lte": field2 }
        elif fineasylib.emptyField(field1) == False:
            match[key] = { "$gte": field1 }
        elif fineasylib.emptyField(field2) == False:
            match[key] = { "$lte": field2 }

    return match