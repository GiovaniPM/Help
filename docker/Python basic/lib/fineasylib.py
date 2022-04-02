'''
    Funções comuns
'''
from bson import ObjectId
from datetime import datetime, timedelta, date
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from pathlib import Path
from unicodedata import normalize

import ast
import base64
import configparser
import getpass
import json
import mongolib
import os
import re
import requests
import socket
import smtplib
import sys
import xlsxwriter
import uuid

ALLOPTIONS = 'TUDO'

UNICODE_ACCENTUATION = {
    '\u00a7': 'o',
    '\u00b7': 'U',
    '\u00de': 'C',
    '\u00c0': 'A',
    '\u00c1': 'A',
    '\u00c2': 'A',
    '\u00c3': 'A',
    '\u00c4': 'A',
    '\u00c7': 'C',
    '\u00c8': 'E',
    '\u00c9': 'E',
    '\u00ca': 'E',
    '\u00cb': 'E',
    '\u00cc': 'I',
    '\u00cd': 'I',
    '\u00ce': 'I',
    '\u00cf': 'I',
    '\u00d1': 'N',
    '\u00d2': 'O',
    '\u00d3': 'O',
    '\u00d4': 'O',
    '\u00d5': 'O',
    '\u00d6': 'O',
    '\u00d9': 'U',
    '\u00da': 'U',
    '\u00db': 'U',
    '\u00e0': 'a',
    '\u00e1': 'a',
    '\u00e2': 'a',
    '\u00e3': 'a',
    '\u00e4': 'a',
    '\u00e7': 'c',
    '\u00e8': 'e',
    '\u00e9': 'e',
    '\u00ea': 'e',
    '\u00ec': 'i',
    '\u00ed': 'i',
    '\u00ee': 'i',
    '\u00ef': 'i',
    '\u00f1': 'n',
    '\u00f2': 'o',
    '\u00f3': 'o',
    '\u00f4': 'o',
    '\u00f5': 'o',
    '\u00f6': 'o',
    '\u00f9': 'u',
    '\u00fa': 'u',
    '\u00fb': 'u',
    '\u00fc': 'u',
    '\u00fe': 'c',
    '\u0026': '&',
    '\u0027': "'",
}

class txtColors:
    FGBLK  = '\033[30m'
    FGRED  = '\033[31m'
    FGGRE  = '\033[32m'
    FGYEL  = '\033[33m'
    FGBLU  = '\033[34m'
    FGMAG  = '\033[35m'
    FGCYA  = '\033[36m'
    FGWHI  = '\033[37m'
    FGBLKB = '\033[90m'
    FGREDB = '\033[91m'
    FGGREB = '\033[92m'
    FGYELB = '\033[93m'
    FGBLUB = '\033[94m'
    FGMAGB = '\033[95m'
    FGCYAB = '\033[96m'
    FGWHIB = '\033[97m'
    BGBLK  = '\033[40m'
    BGRED  = '\033[41m'
    BGGRE  = '\033[42m'
    BGYEL  = '\033[43m'
    BGBLU  = '\033[44m'
    BGMAG  = '\033[45m'
    BGCYA  = '\033[46m'
    BGWHI  = '\033[47m'
    BGBLKB = '\033[100m'
    BGREDB = '\033[101m'
    BGGREB = '\033[102m'
    BGYELB = '\033[103m'
    BGBLUB = '\033[104m'
    BGMAGB = '\033[105m'
    BGCYAB = '\033[106m'
    BGWHIB = '\033[107m'
    RST    = '\033[0m'
    BLD    = '\033[1m'
    UND    = '\033[4m'
    BLK    = '\033[5m'
    REV    = '\033[7m'

def converteDeltaMinutos(timeDelta):
    '''
       Convert a timeDelta in minutes.
    
       Parameters:

           timeDelta       = Time delta

       Ex.: minutos = converteDeltaMinutos(time)
    '''
    array = divmod(timeDelta.total_seconds(), 60)
    return array[0]

def logConnection( Inicio, Fim, Texto ):
    '''
       Print a log console.
    
       Parameters:

           Inicio          = Start datetime

           Fim             = End datetime

           Texto           = Text

       Ex.: logConnection( Inicio, Fim, 'Texto' )
    '''
    linha = Inicio.strftime('%Y-%m-%d %H:%M:%S') + ' - ' + \
            Fim.strftime('%Y-%m-%d %H:%M:%S') + ' - ' + \
            Texto.ljust(20)[0:20] + ' - (' + \
            getpass.getuser() + '@' + \
            socket.gethostname() + ')'
    return linha

def readINIKey(iniFile, label, key):
    '''
       Read a INI config keys
    
       Parameters:

           iniFile       = Name of ini file

           label         = Label of section in ini file

           key           - Key to be acessed

       Ex.: value = readINIKey('setup.ini', 'PRD', 'DB_HOST')
    '''
    config = configparser.ConfigParser()
    config.read(iniFile)

    result = config.get(label,key)

    return result

def removeAccentuation(txt):
    '''
        Accentuation remotion

        Parameters:

            txt          = text do be replace

        Ex.: new = removeAccentuation(old)
    '''
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def removePunctuation(txt):
    '''
        Punctuation remotion

        Parameters:

            txt          = text do be replace

        Ex.: new = removePunctuation(old)
    '''
    return re.sub(r'[^\w\s]', '', txt)

def convertJSON(o):
    '''
       Lamba function to convert JSON data
    
       Parameters:

           o             = something

       Ex.: json_data = json.dumps(list_cur, default=fineasylib.convertJSON, indent = 4, sort_keys=True)
    '''
    if type(o) == 'str':
        return removeAccentuation(o)
    elif isinstance(o, ObjectId):
        return o.__str__()
    elif isinstance(o, str):
        return removeAccentuation(o)
    elif isinstance(o, datetime):
        try:
            data =  o - timedelta(hours=3)
            return data.__str__()
        except:
            return o.__str__()

def accentuationUnicode(txt):
    '''
       Remove unicode chars
    
       Parameters:

           txt           = text

       Ex.: accentuationUnicode(txt)
    '''
    txt = txt.replace('\\u0026', '&')
    txt = txt.replace('\\u0027', "'")
    txt = txt.replace('\\u00a7', 'o')
    txt = txt.replace('\\u00aa', "a")
    txt = txt.replace('\\u00b7', 'U')
    txt = txt.replace('\\u00c0', 'A')
    txt = txt.replace('\\u00c1', 'A')
    txt = txt.replace('\\u00c2', 'A')
    txt = txt.replace('\\u00c3', 'A')
    txt = txt.replace('\\u00c4', 'A')
    txt = txt.replace('\\u00c7', 'C')
    txt = txt.replace('\\u00c8', 'E')
    txt = txt.replace('\\u00c9', 'E')
    txt = txt.replace('\\u00ca', 'E')
    txt = txt.replace('\\u00cb', 'E')
    txt = txt.replace('\\u00cc', 'I')
    txt = txt.replace('\\u00cd', 'I')
    txt = txt.replace('\\u00ce', 'I')
    txt = txt.replace('\\u00cf', 'I')
    txt = txt.replace('\\u00d1', 'N')
    txt = txt.replace('\\u00d2', 'O')
    txt = txt.replace('\\u00d3', 'O')
    txt = txt.replace('\\u00d4', 'O')
    txt = txt.replace('\\u00d5', 'O')
    txt = txt.replace('\\u00d6', 'O')
    txt = txt.replace('\\u00d9', 'U')
    txt = txt.replace('\\u00da', 'U')
    txt = txt.replace('\\u00db', 'U')
    txt = txt.replace('\\u00de', 'C')
    txt = txt.replace('\\u00e0', 'a')
    txt = txt.replace('\\u00e1', 'a')
    txt = txt.replace('\\u00e2', 'a')
    txt = txt.replace('\\u00e3', 'a')
    txt = txt.replace('\\u00e4', 'a')
    txt = txt.replace('\\u00e7', 'c')
    txt = txt.replace('\\u00e8', 'e')
    txt = txt.replace('\\u00e9', 'e')
    txt = txt.replace('\\u00ea', 'e')
    txt = txt.replace('\\u00ec', 'i')
    txt = txt.replace('\\u00ed', 'i')
    txt = txt.replace('\\u00ee', 'i')
    txt = txt.replace('\\u00ef', 'i')
    txt = txt.replace('\\u00f1', 'n')
    txt = txt.replace('\\u00f2', 'o')
    txt = txt.replace('\\u00f3', 'o')
    txt = txt.replace('\\u00f4', 'o')
    txt = txt.replace('\\u00f5', 'o')
    txt = txt.replace('\\u00f6', 'o')
    txt = txt.replace('\\u00f9', 'u')
    txt = txt.replace('\\u00fa', 'u')
    txt = txt.replace('\\u00fb', 'u')
    txt = txt.replace('\\u00fc', 'u')
    txt = txt.replace('\\u00fe', 'c')

    return txt

def encodeBase64(str):
    '''
       Encode text to base64
    
       Parameters:

           str           = text

       Ex.: encodeBase64(str)
    '''
    key_bytes   = str.encode("ascii")
    key_base64  = base64.b64encode(key_bytes)
    key_message = key_base64.decode('ascii')
    return key_message

def decodeBase64(str):
    '''
       Decode text to base64
    
       Parameters:

           str           = text

       Ex.: decodeBase64(str)
    '''
    base64_bytes = str.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message

def getHourStr(hora):
    '''
       Turn hour to HH:MM:SS
    
       Parameters:

           hora          = hour

       Ex.: getHourStr(hora)
    '''
    hour    = str(hora.hour)
    minute  = str(hora.minute)
    second  = str(hora.second)
    return hour.rjust(2,'0') + ":" + minute.rjust(2,'0') + ":" + second.rjust(2,'0')

def getAcessToken(client_id, secret_id):
    '''
       Get the access token
    
       Parameters:

           client_id

           secret_id 

       Ex.: access_token, authorizationBase64 = getAcessToken(client_id, secret_id)
    '''
    key_id      = "Basic " + encodeBase64(client_id + ":" + secret_id)
    
    # Get host code
    url     = "http://api-topazio.sensedia.com/oauth/grant-code"
    
    header  = {}
    header["content-type"]  = "application/json"
    
    payload = {}
    payload["client_id"]    = client_id
    payload["redirect_uri"] = "http://localhost"
    
    response = requests.post(url, headers=header, json=payload)
    
    if response.status_code >= 200 and response.status_code <= 299:
        message  = response.content.decode("utf-8")
        response = ast.literal_eval(message)
        response = response['redirect_uri']
        codeurl  = response.replace("http://localhost/?code=","")
    
        # Get acess token
        url     = "http://api-topazio.sensedia.com/oauth/access-token"
        
        header  = {}
        header["authorization"] = key_id
        header["content-type"]  = "application/x-www-form-urlencoded"
        
        payload = {}
        payload["grant_type"]   = "authorization_code"
        payload["code"]         = codeurl
        
        response = requests.post(url, headers=header, data=payload)
        
        if response.status_code >= 200 and response.status_code <= 299:
            message      = response.content.decode("utf-8")
            response     = ast.literal_eval(message)
            response     = response['access_token']
            access_token = response

            return access_token, key_id
        else:
            return None, None
    else:
        return None, None

def strToDate(dateString='', tmz=-3):
    '''
       Turn str to date, with timezone convertion
    
       Parameters:

           dateString   = String in format "yyyy-MM-dd"

           tmz          = Time zone hour (Brazil = -3)

       Ex.: date = strToDate('2021-08-20', -3)
    '''
    if dateString != '':
        now = date(*map(int, dateString.split('-')))
        return datetime(now.year, now.month, now.day, 00, 00, 00, 000000) - timedelta(hours=tmz)
    else:
        return None

def addDays(date, days=0, tmz=-3):
    '''
       Add days to a date
    
       Parameters:

           date         = Date in datetime format

           days         = Days to be added

       Ex.: date = addDays(date, 1)
    '''
    days = days * (-1)
    return datetime(date.year, date.month, date.day, 00, 00, 00, 000000) - timedelta(days=days, hours=tmz)

def emptyField(field):
    '''
       Field is empty?
    
       Parameters:

           field   

       Ex.: emptyField(field)
    '''
    if type(field) is list:
        return field == [] or ALLOPTIONS in field or '--' in field
    else:
        return field == '' or field == None or field == ALLOPTIONS

def listParceiros():
    '''
       Create a partners list to fieldchoice.
    '''
    tupla = []
    
    client = mongolib.db_connection('PRD')
    album = mongolib.get_collection(client, 'transfer', 'partners')
    
    pipeline = []
    
    sort = {}

    sort = { "socialName": 1 }

    pipeline.append({'$sort': sort})
    
    cursor = album.aggregate(pipeline)

    tupla += [( ALLOPTIONS, '--' )]

    for doc in cursor:
        tupla += [( "%s" % (doc['clientId']), "%s - %s" % (doc['clientId'], doc['socialName']))]
    
    client.close()

    return tuple(tupla)

def noChoiceField(field):
    '''
       Choice all is informed?
    
       Parameters:

           field   

       Ex.: noChoiceField(field)
    '''
    return field == ALLOPTIONS or field == '--' or field == 'ALL'

def tableUnicode(char):
    '''
       Table unicode chars
    
       Parameters:

           char           = char

       Ex.: tableUnicode(char)
    '''
    try:
        return UNICODE_ACCENTUATION[char]
    except:
        return char

def addNode(reg, label):
    entrace = {}
    #When add the node, must be with the same type in original.
    if type(reg) == int:
        entrace[label] = int(reg)
    elif type(reg) == float:
        entrace[label] = float(reg)
    elif isinstance(reg, datetime):
        try:
            data = reg - timedelta(hours=3)
        except:
            data = reg
        entrace[label] = str(data)
    else:
        entrace[label] = str(reg)
    return entrace

def getNode(lst, obj, label):
    col = 1

    #Decompose struct in terms of itens
    for item in obj:
        try:
            #Get the key and her value
            key   = item
            value = obj[item]
        except:
            #The item are atomic (composed only by itens)
            key   = '_reg[' + str(col).rjust(3,'0') + ']'
            value = item
            col   += 1
        
        #Get the first character in the item value, to determine if value are: value, dict or list.
        #In order, must understand if the item value is a string, to prevent python misunderstanding.
        if type(value) != str:
            bgValue = str(value)[0:1]
        else:
            bgValue = ' '

        #Assembly the key path.
        if label == '':
            newLabel = key
        else:
            newLabel = label + '.' + key

        #The first character of item value is '[', seens like a array.
        if bgValue == '[':
        ########if bgValue == '[' and type(value) != str:
            count = 1
            #Decompose the array
            for reg in value:
                lstLabel = newLabel + '[' + str(count).rjust(3,'0') + ']'
                #If the item in the array is a list or dict, use a recursive call. Otherwise put in the result list
                if type(reg) ==  list or type(reg) == dict:
                    getNode(lst, reg, lstLabel)
                else:
                    lst.append(addNode(reg, lstLabel))
                count += 1
        #The first character of item value is '{', seens like a dict, use a recursive call.
        elif bgValue == '{':
        ########elif bgValue == '{' and type(value) != str:
            getNode(lst, value, newLabel)
        #Other way smells like a true value, put in the result list
        else:
            lst.append(addNode(value, newLabel))

def getTitle(title, lst):
    #Read the result list, to create a unique list of titles.
    #This logic must be used to correct docs with different keys.
    for reg in lst:
        for field in reg:
            try:
                pos = title.index(field)
            except:
                pos = -1

            if pos < 0:
                title.append(field)
    
    title.sort()

def getValues(lstOutput, lst):
    #Turn array-of-array into array-of-dict.
    outputReg = {}
    for tupla in lst:
        for field in tupla:
            outputReg[field] = tupla[field]
    lstOutput.append(outputReg)

def getSheet(lstTitles, lstValues):
    lstSheet = []

    #Read each dict on the array-of-dict.
    #Get all titles in try find the correspond in the dict and put in the result list, otherwise put a empty key.
    for reg in lstValues:
        outputReg = {}

        for field in lstTitles:
            try:
                outputReg[field] = reg[field]
            except:
                outputReg[field] = None
        
        lstSheet.append(outputReg)

    return lstSheet

def getDataExport(reg, lstTitle, lstValues):
    '''
       Prepare data in two lists.
    
       Parameters:

           reg            = each individual

           lstTitle       = list with the titles

           lstValues      = list with the values

       Ex.: tableUnicode(char)
    '''
    lista = []
    lstOutput = []
    getNode(lista, reg, '')
    getValues(lstOutput, lista)
    getTitle(lstTitle, lista)
    lstValues += lstOutput

def expDataExcel(workbook, lstTitle, lstValues, sheetName=''):
    '''
       Generate a excel two lists.
    
       Parameters:

           workbook       = excel workbook

           lstTitle       = list with the titles

           lstValues      = list with the values

       Ex.: expDataExcel(workbook, lstTitle, lstValues)
    '''
    header    = workbook.add_format({'bold': True, 'bg_color': 'gray'})
    if sheetName == '':
        worksheet = workbook.add_worksheet()
    else:
        worksheet = workbook.add_worksheet(sheetName)

    lstValues = getSheet(lstTitle, lstValues)

    linha = 0
    coluna = 0
    
    for reg in lstTitle:
        worksheet.write(linha,  coluna, reg, header)
        coluna += 1
    
    linha += 1

    for reg in lstValues:
        coluna = 0
        for field in reg:
            worksheet.write(linha,  coluna, reg[field])
            coluna += 1
        linha += 1

def posCursor(row, column):
    '''
       Put thr cursor on the position.
    
       Parameters:

           row            = 

           column         = 

       Ex.: posCursor(10, 50)
    '''
    return '\033[%d;%dH' % (row, column)

def setFgColor(color):
    '''
       Set text background color.
    
       Parameters:

           color          = 112

       Ex.: setFgColor(112)
    '''
    return '\033[38;5;%dm' % (color)

def setBgColor(color):
    '''
       Set text foreground color.
    
       Parameters:

           color          = 112

       Ex.: setBgColor(112)
    '''
    return '\033[48;5;%dm' % (color)

def postMessageTelegram(token, chat_id, msg):
    '''
       Envia mensage pelo Telegram.
    
       Parameters:

           token          = string with the token

           chat_id        = string with room id

           msg            = string message
       
       Ex.: postMessageTelegram('2027100082:AAELBy-Vw00jg9iUpxM0ENbn9USP_kL5vfQ','1971368110','Oba')
    '''
    url = 'https://api.telegram.org/bot' + token + '/sendMessage'

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "chat_id": chat_id,
        "text": "[" + str(datetime.now()) + "] - " + msg,
        "disable_notification": False
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    return response

def postMessageTeams(webhook, msg):
    '''
       Envia mensage pelo Teams.
    
       Parameters:

           webhook        = string webhook link

           msg            = string message
    '''
    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "text": "[" + str(datetime.now()) + "] - " + msg
    }
    
    response = requests.post(webhook, headers=headers, data=json.dumps(payload))

    return response

def posEmail(send_from, send_to, subject, message, files=[],
             server="localhost", port=587, username='', password='',
             use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ",".join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(path).name))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

def sendMessageSpoon(code, level=[1], clientId=None):
    """Capture eletronicMessage catalog

    Args:
        code     (string):  Message group code
        level    (list)  :  List with levels of this message
        clientId (string):  The clientId code
    """
    Emails          = {''}
    Teams           = {''}
    TelegramTokens  = {''}
    TelegramChatIds = {''}

    client = mongolib.db_connection('HLG')
    album = mongolib.get_collection(client, 'baas', 'eletronicMessage')

    pipeline = []
    matches = {}
    matches['code'] = code
    matches['clientId'] = None
    pipeline.append({'$match': matches})
    sort = {}
    sort['clientId'] = 1
    pipeline.append({'$sort': sort})

    cursor = album.aggregate(pipeline, collation={ "locale": "en", "strength": 1 })

    for doc in cursor:
        for postInfo in doc['postInfo']:
            if postInfo['level'] in level:
                for endPoint in postInfo['endPoint']:
                    if endPoint['active'] == True:
                        if endPoint['type'] == 'Email':
                            Emails.add(endPoint['value']['address'])
                        elif endPoint['type'] == 'Telegram':
                            TelegramTokens.add(endPoint['value']['token'])
                            TelegramChatIds.add(endPoint['value']['chatId'])
                        elif endPoint['type'] == 'Teams':
                            Teams.add(endPoint['value']['webhook'])

    if clientId != None:
        pipeline = []
        matches = {}
        matches['code'] = code
        matches['clientId'] = clientId
        pipeline.append({'$match': matches})
        sort = {}
        sort['clientId'] = 1
        pipeline.append({'$sort': sort})
    
        cursor = album.aggregate(pipeline, collation={ "locale": "en", "strength": 1 })
    
        for doc in cursor:
            for postInfo in doc['postInfo']:
                if postInfo['level'] in level:
                    for endPoint in postInfo['endPoint']:
                        if endPoint['active'] == True:
                            if endPoint['type'] == 'Email':
                                Emails.add(endPoint['value']['address'])
                            elif endPoint['type'] == 'Telegram':
                                TelegramTokens.add(endPoint['value']['token'])
                                TelegramChatIds.add(endPoint['value']['chatId'])
                            elif endPoint['type'] == 'Teams':
                                Teams.add(endPoint['value']['webhook'])
    
    client.close()

    return Emails, Teams, TelegramTokens, TelegramChatIds

def sendMessages(code, level=[1], clientId=None, message=''):
    """Send eletronic message using the catalog of eletronicMessage

    Args:
        code     (string):  Message group code
        level    (list)  :  List with levels of this message
        clientId (string):  The clientId code
        message  (string):  Message to be send. Defaults to ''.
    """

    Emails, Teams, TelegramTokens, TelegramChatIds = sendMessageSpoon(code, level, clientId)

    email_to       = ''
    #email_from     = 'sistrapi@fineasytech.com'
    #email_server   = eval(os.environ.get('EMAIL_SERVER'))
    #email_port     = eval(os.environ.get('EMAIL_PORT'))
    #email_username = eval(os.environ.get('EMAIL_USERNAME'))
    #email_password = eval(os.environ.get('EMAIL_PASSWORD'))
    #email_subject  = code

    while (len(Emails) > 0):
        address  = Emails.pop()
        if address != '':
            if email_to == '':
                email_to += address
            else:
                email_to += ';' + address

    print(email_to)

    #while (len(TelegramTokens) > 0):
    #    token  = TelegramTokens.pop()
    #    chatId = TelegramChatIds.pop()
    #    if token != '':
    #        postMessageTelegram(token, chatId, message)

    #while (len(Teams) > 0):
    #    webhook  = Teams.pop()
    #    if webhook != '':
    #        postMessageTeams(webhook, message)

def INIValues(files, labels):
    """Return multiple labels in INI file

    Args:
        files (list): list of values with files with relative path
        labels (list): list of labels (see more in example)

    Returns:
        list: dictionary with keys and their respective value

    Example:
        Code:
            import fineasylib

            files = [
                'setup.ini',
                'dashboard/setup.ini',
                '/dashboard/setup.ini'
            ]

            labels = [
                {'label': 'Setup', 'key': 'PageTimeUpdate', 'default': '5'                                                                    },
                {'label': 'Setup', 'key': 'PageTimePix'   , 'default': '5'                                                                    },
                {'label': 'Setup', 'key': 'EnviromentName', 'default': 'HLG'                                                                  },
                {'label': 'Theme', 'key': 'Logo'          , 'default': 'https://www.bancotopazio.com.br/wp-content/uploads/2019/05/ico_6.png' },
                {'label': 'Theme', 'key': 'BackPicture'   , 'default': 'https://www.bancotopazio.com.br/wp-content/uploads/2019/05/ico_6.png' },
                {'label': 'Theme', 'key': 'ColorHead'     , 'default': '#f8c471'                                                              },
                {'label': 'Theme', 'key': 'ColorBody'     , 'default': '#fad7a0'                                                              }
            ]

            print(fineasylib.INIValues(files,labels))

        Result:
            {'PageTimeUpdate': '5', 'PageTimePix': '5', 'EnviromentName': 'PRD', 'Logo': 'https://v2assets.zopim.io/4UTdH6YgZTvTDKFnMs3aaaDqxMMlR5KE-banner?1557803643080', 'BackPicture': 'https://www.bancotopazio.com.br/wp-content/uploads/2019/05/ico_6.png', 'ColorHead': '#4993ec', 'ColorBody': '#dff7fd'}
    """
    output = {}

    for reg in labels:
        value = None

        for file in files:
            try:
                foundValue = readINIKey(file, reg['label'], reg['key'])
            except:
                foundValue = None
            
            if foundValue != None:
                value = foundValue

        if value != None:
            output[reg['key']] = value
        else:
            output[reg['key']] = reg['default']

    return output

def expPipelineExcel(workbook, pipeLine, sheetName=''):
    '''
       Generate a excel two lists.
    
       Parameters:

           workbook       = excel workbook

           pipeLine       = JSON de consulta

           sheetName      = Sheet name

       Ex.: expPipelineExcel(workbook, lstTitle, lstValues)
    '''
    header    = workbook.add_format({'bold': True, 'bg_color': 'gray'})
    if sheetName == '':
        worksheet = workbook.add_worksheet()
    else:
        worksheet = workbook.add_worksheet(sheetName)

    linha = 0
    coluna = 0
    
    worksheet.write(linha,  coluna, 'JSON', header)
    
    linha += 1

    worksheet.write(linha,  coluna, str(pipeLine))

def mongoINPipeline(key, list):
    '''
       Generate IN options for mongodb query.
    
       Parameters:

           key            = field to be filtered

           list           = list of options

       Ex.: mongoINPipeline("type", lstValues)
    '''
    options = []
    for reg in list:
        value          = {}
        value["$eq"]   = reg
        element        = {}
        element[key]   = value
        options.append(element)

    return options

def copyDictToDict(reg, listValues):
    '''
       Copy some fields in a dict to other dict.
    '''
    output = {key: reg[key] for key in listValues}
    return output

def expDataCSV(filearq, lstTitle, lstValues):
    """Export to CSV layout

    Args:
        filearq (handle): handle of file
        lstTitle (list): list of all headers
        lstValues (dict): values
    """
    regout = ''
    for col in lstTitle:
        if regout != '':
             regout += ','
        regout += '"' + col + '"'
    filearq.write(regout + '\n')

    for lin in lstValues:
        regout = ''
        for col in lstTitle:
            if regout != '':
                regout += ','
            try:
                regout += '"' + str(lin[col]) + '"'
                regout = regout.replace('\n', ' ')
            except:
                regout += '""'
        filearq.write(regout + '\n')

def createFileExport(fileType):
    """Create a file to export by the type informed

    Args:
        fileType (string): the type ex.: 'Excel', 'Json', 'CSV'
    Returns:
        dict: file structure
    """
    fileoutput = {}

    if fileType == 'Excel':
        fileoutput['filename']   = str(uuid.uuid1()) + '.xlsx'
        fileoutput['filehandle'] = xlsxwriter.Workbook('Output/' + fileoutput['filename'])
        fileoutput['type']       = fileType
    elif fileType == 'Json':
        fileoutput['filename']   = str(uuid.uuid1()) + '.json'
        fileoutput['filehandle'] = open('Output/' + fileoutput['filename'], "w")
        fileoutput['type']       = fileType
    elif fileType == 'CSV':
        fileoutput['filename']   = str(uuid.uuid1()) + '.csv'
        fileoutput['filehandle'] = open('Output/' + fileoutput['filename'], "w")
        fileoutput['type']       = fileType

    return fileoutput

def writeFileExport(fileoutput, cursor, query, collection):
    """Write a cursor to a file

    Args:
        fileoutput (dict): file structure
        cursor (cursor): Value structure
        query (dict): Query pipeline
        collection (string): Collection name
    """
    lstTitle  = []
    lstValues = []

    handle = fileoutput['filehandle']

    if fileoutput['type'] == 'Excel':
        for reg in cursor:
            getDataExport(reg, lstTitle, lstValues)

        expDataExcel(handle, lstTitle, getSheet(lstTitle, lstValues), collection)

        expPipelineExcel(handle, query, collection + '_query')
    elif fileoutput['type'] == 'Json':
        list_cur = list(cursor)
        json_data = accentuationUnicode(json.dumps(list_cur, default=convertJSON, indent=4, sort_keys=True))

        for reg in json_data:
            handle.write(reg)
    elif fileoutput['type'] == 'CSV':
        for reg in cursor:
            getDataExport(reg, lstTitle, lstValues)

        expDataCSV(handle, lstTitle, lstValues)

def closeFileExport(fileoutput):
    """Close a export file

    Args:
        fileoutput (dict): file structure
    """
    handle = fileoutput['filehandle']

    if fileoutput['type'] == 'Excel':
        handle.close()
    elif fileoutput['type'] == 'Json':
        handle.close()
    elif fileoutput['type'] == 'CSV':
        handle.close()