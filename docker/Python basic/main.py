#!/usr/bin/env python
from __future__ import print_function
from flask import Flask, jsonify, abort, request
from flask_cors import CORS, cross_origin
from json import dumps
from requests import post

import datetime
import time
import json
import logging
import math
import os
import re
import fineasylib
import oraclelib

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '8080'))