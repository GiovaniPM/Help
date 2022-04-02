# -*- coding: utf-8 -*-

import fineasylib
import json
import mongolib

lista  = []
lista.append(mongolib.addMatch({}, 'transactionId', 'equal', '', '10f29e36-2679-4e64-a497-50ad3c22c35a', None))
lista.append(mongolib.addMatch({}, 'transactionId', 'equal', '', '10f29e36-2679-4e64-a497-50ad3c22c35b', None))

param1 = 'PRD'
param2 = 'transfer'
param3 = 'accountopenings'
param4 = {}
param4 = mongolib.addMatch(param4, '', 'or', '', lista, None)
param5 = ['status', 'documentType', 'document', 'externalStatus']

output = mongolib.loadMongoResult(param1,
                                  param2,
                                  param3,
                                  param4,
                                  param5)

list_cur = list(output)
json_data = json.dumps(list_cur, default=fineasylib.convertJSON, indent=4, sort_keys=True)

print(json_data)