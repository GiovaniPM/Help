#!/usr/bin/env python
from __future__ import print_function
from flask import Flask, jsonify, abort, request
from flask_cors import CORS, cross_origin
from json import dumps
from requests import post
#from lib.fineasylib import INIValues

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

@app.route('/config', methods=['GET'])
def view_config():
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
    param2 = [ 'Codigo', 'Descricao' ]
    param3 = "SELECT imlitm Codigo, \
                     imdsc1 Descricao \
                FROM C##GIOVANIPM.f4101"
    param4 = ''
    
    print(param3)

    cursor = oraclelib.loadOracleResult(param1,
                                        param2,
                                        param3,
                                        param4)

    return jsonify( cursor )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '8080'))