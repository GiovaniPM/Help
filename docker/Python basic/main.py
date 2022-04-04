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
        {'label': 'Test', 'key': 'message'       , 'default': 'None'        },
        {'label': 'PRD' , 'key': 'db_host'       , 'default': 'localhost'   },
        {'label': 'PRD' , 'key': 'db_port'       , 'default': '1521'        },
        {'label': 'PRD' , 'key': 'db_servicename', 'default': 'xe'          },
        {'label': 'PRD' , 'key': 'db_user'       , 'default': 'C##GIOVANIPM'},
        {'label': 'PRD' , 'key': 'db_pass'       , 'default': 'Pm11092j'    }
    ]

    config = fineasylib.INIValues(files,labels)

    param1 = 'PRD'
    param2 = [ 'Descricao' ]
    param3 = "SELECT imlitm Descricao\
                FROM C##GIOVANIPM.f4101"
    param4 = ''

    cursor = oraclelib.loadOracleResult(param1,
                                        param2,
                                        param3,
                                        param4)

    print(cursor)

    return jsonify( { 'message': config['message'] } )
    #return jsonify( { 'message': 'None' } )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '8080'))