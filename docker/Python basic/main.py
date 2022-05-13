#!/usr/bin/env python
from __future__ import print_function
from flask import Flask, jsonify
from flask_cors import CORS

import json
import os
import fineasylib
import oraclelib
import mongolib

app = Flask(__name__)
app.debug = True
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*","methods":"POST,DELETE,PUT,GET,OPTIONS"}})

def showConfig():
    return None

@app.route('/f4101', methods=['GET'])
def view_f4101():
    """
    Description:

    Parameter:

    Return:

    Usage:

    Example:
    """

    files = [
        'settings.ini',
    ]

    labels = [
        {'label': 'Test', 'key': 'message', 'default': 'None'}
    ]

    config = fineasylib.INIValues(files,labels)

    param1 = 'PRD'
    param2 = [ 'Codigo',
               'Descricao' ]
    param3 = "SELECT imlitm Codigo, \
                     imdsc1 Descricao \
                FROM C##GIOVANIPM.f4101 \
               ORDER BY imlitm"
    param4 = ''

    cursor = oraclelib.loadOracleResult(param1,
                                        param2,
                                        param3,
                                        param4)

    return jsonify( { 'tabela': 'f4101', 'dados': cursor } )

@app.route('/f4102', methods=['GET'])
def view_f4102():
    """
    Description:

    Parameter:

    Return:

    Usage:

    Example:
    """

    files = [
        'settings.ini',
    ]

    labels = [
        {'label': 'Test', 'key': 'message', 'default': 'None'}
    ]

    config = fineasylib.INIValues(files,labels)

    param1 = 'PRD'
    param2 = [ 'Codigo',
               'Filial' ]
    param3 = "SELECT iblitm Codigo, \
                     ibmcu Filial \
                FROM C##GIOVANIPM.f4102 \
               ORDER BY ibmcu, \
                        iblitm"
    param4 = ''

    cursor = oraclelib.loadOracleResult(param1,
                                        param2,
                                        param3,
                                        param4)

    return jsonify( { 'tabela': 'f4102', 'dados': cursor } )

@app.route('/f0006', methods=['GET'])
def view_f0006():
    """
    Description:

    Parameter:

    Return:

    Usage:

    Example:
    """

    files = [
        'settings.ini',
    ]

    labels = [
        {'label': 'Test', 'key': 'message', 'default': 'None'}
    ]

    config = fineasylib.INIValues(files,labels)

    param1 = 'PRD'
    param2 = [ 'Filial',
               'Descricao' ]
    param3 = "SELECT mcmcu Filial, \
                     mcdc Descricao \
                FROM C##GIOVANIPM.f0006 \
               ORDER BY mcmcu"
    param4 = ''

    cursor = oraclelib.loadOracleResult(param1,
                                        param2,
                                        param3,
                                        param4)

    return jsonify( { 'tabela': 'f0006', 'dados': cursor } )

@app.route('/pessoas', methods=['GET'])
def view_pessoa():
    """
    Description:

    Parameter:

    Return:

    Usage:

    Example:
    """

    files = [
        'settings.ini',
    ]

    labels = [
        {'label': 'Test', 'key': 'message', 'default': 'None'}
    ]

    config = fineasylib.INIValues(files,labels)

    param1 = 'PRD'
    param2 = 'Teste'
    param3 = 'Pessoa'
    param4 = {}
    param5 = []
    param6 = {}

    try:
        cursor = mongolib.loadMongoResult(param1,
                                          param2,
                                          param3,
                                          param4,
                                          param5,
                                          param6)
        
        dados = list(cursor)
        dados = json.dumps(dados, default=fineasylib.convertJSON, sort_keys=True)
        dados = json.loads(dados)
        
        return jsonify( { 'dados': dados, 'collection': param3 } )
    except:
        return jsonify( { 'param1': param1, 'param2': param2, 'param3': param3 } )

@app.route('/dados', methods=['GET'])
def view_dados():
    """
    Description:

    Parameter:

    Return:

    Usage:

    Example:
    """

    files = [
        'settings.ini',
    ]

    labels = [
        {'label': 'Test', 'key': 'message', 'default': 'None'}
    ]

    config = fineasylib.INIValues(files,labels)

    param1 = 'PRD'
    param2 = 'Teste'
    param3 = 'dados'
    param4 = {}
    param5 = []
    param6 = {}

    try:
        cursor = mongolib.loadMongoResult(param1,
                                          param2,
                                          param3,
                                          param4,
                                          param5,
                                          param6)
        
        dados = list(cursor)
        dados = json.dumps(dados, default=fineasylib.convertJSON, sort_keys=True)
        dados = json.loads(dados)
        
        return jsonify( { 'dados': dados, 'collection': param3 } )
    except:
        return jsonify( { 'param1': param1, 'param2': param2, 'param3': param3 } )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=os.environ.get('PORT', '8080'))