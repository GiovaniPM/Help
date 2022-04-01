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

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*","methods":"POST,DELETE,PUT,GET,OPTIONS"}})

def isCpfValid(cpf):
    """
        If cpf in the Brazilian format is valid, it returns True, otherwise, it returns False. 

        Format: 999.999.999-DD
    """
    # Check if type is str
    if not isinstance(cpf,str):
        return False
    # Remove some unwanted characters
    cpf = re.sub("[^0-9]",'',cpf)
    # Checks if string has 11 characters
    if len(cpf) != 11:
        return False
    sum = 0
    weight = 10
    """ Calculating the first cpf check digit. """
    for n in range(9):
        sum = sum + int(cpf[n]) * weight
        # Decrement weight
        weight = weight - 1
    verifyingDigit = 11 -  sum % 11
    if verifyingDigit > 9 :
        firstVerifyingDigit = 0
    else:
        firstVerifyingDigit = verifyingDigit
    """ Calculating the second check digit of cpf. """
    sum = 0
    weight = 11
    for n in range(10):
        sum = sum + int(cpf[n]) * weight
        # Decrement weight
        weight = weight - 1
    verifyingDigit = 11 -  sum % 11
    if verifyingDigit > 9 :
        secondVerifyingDigit = 0
    else:
        secondVerifyingDigit = verifyingDigit
    if cpf[-2:] == "%s%s" % (firstVerifyingDigit,secondVerifyingDigit):
        return True
    return False
def isEctValid(ect):
    """
        If ect in the Brazilian format is valid, it returns True, otherwise, it returns False.

        Format: AA99999999DAA
    """
    # Check if type is str
    if not isinstance(ect,str):
        return False
    # Remove some unwanted characters
    ect = re.sub("[^0-9]",'',ect)
    # Checks if string has 9 characters
    if len(ect) != 9:
        return False
    sum = 0
    weight = [8,6,4,2,3,5,9,7]
    """ Calculating the ect check digit. """
    for n in range(8):
        sum = sum + int(ect[n]) * weight[n]
    verifyingDigit = 11 -  sum % 11
    if verifyingDigit == 0:
        firstVerifyingDigit = 5
    elif verifyingDigit == 1:
        firstVerifyingDigit = 0
    else:
        firstVerifyingDigit = verifyingDigit
    if ect[-1:] == "%s" % (firstVerifyingDigit):
        return True
    return False
def isCnpjValid(cnpj):
    """
        If cnpf in the Brazilian format is valid, it returns True, otherwise, it returns False.

        Format: 99.999.999/999-DD
    """
    # Check if type is str
    if not isinstance(cnpj,str):
        return False
    # Remove some unwanted characters
    cpf = re.sub("[^0-9]",'',cnpj)
    # Checks if string has 11 characters
    if len(cpf) != 14:
        return False
    sum = 0
    weight = [5,4,3,2,9,8,7,6,5,4,3,2]
    """ Calculating the first cpf check digit. """
    for n in range(12):
        value =  int(cpf[n]) * weight[n]
        sum = sum + value
    verifyingDigit = sum % 11
    if verifyingDigit < 2 :
        firstVerifyingDigit = 0
    else:
        firstVerifyingDigit = 11 - verifyingDigit
    """ Calculating the second check digit of cpf. """
    sum = 0
    weight = [6,5,4,3,2,9,8,7,6,5,4,3,2]
    for n in range(13):
        sum = sum + int(cpf[n]) * weight[n]
    verifyingDigit = sum % 11
    if verifyingDigit < 2 :
        secondVerifyingDigit = 0
    else:
        secondVerifyingDigit = 11 - verifyingDigit
    if cpf[-2:] == "%s%s" % (firstVerifyingDigit,secondVerifyingDigit):
        return True
    return False
def isCertidaoValid(certidao):
    """
        If certidao in the Brazilian format is valid, it returns True, otherwise, it returns False.

        Format: aaaaaa.bb.cc.dddd.e.fffff.ggg.hhhhhhh-ii

        Onde:

        aaaaaa - indica o Código Nacional da Serventia (identificação única do cartório) ex.: 10453-9 (v. Nota final)

        bb - indica o Código do Acervo (01-Acervo Próprio e 02-Acervos incorporados)

        cc - indica o Tipo de Serviço Prestado (55 - Serviço de Registro Civil das Pessoas Naturais)

        dddd - indica o Ano do Registro - ex.: 2013

        e - indica o Tipo do livro - 1-Livro A (Nascimento), 2-Livro B (Casamento), 3-Livro B Auxiliar (Registro de casamentos religiosos para fins civis), 4-Livro C (Óbito), 5-Livro C Auxiliar (Registro de Natimortos), 6-Livro D (Registro de Proclamas), 7-Livro E (Demais atos relativos ao Registro Civil ou Livro E único), 8-Livro E (Desdobrado para registro específico das Emancipações) e 9-Livro E (Desdobrado para registro específico das Interdições)

        fffff - indica o Número do livro - ex.: 00012

        ggg - indica o Número da folha - ex.: 021

        hhhhhhh - indica o Número do Termo - ex.: 0000123

        ii - indica o Dígito Verificador DV
    """
    # Check if type is str
    if not isinstance(certidao,str):
        return False
    # Remove some unwanted characters
    certidao = re.sub("[^0-9]",'',certidao)
    # Checks if string has 11 characters
    if len(certidao) != 32:
        return False
    sum = 0
    weight = [2,3,4,5,6,7,8,9,10,0,1,2,3,4,5,6,7,8,9,10,0,1,2,3,4,5,6,7,8,9]
    """ Calculating the first certidao check digit. """
    for n in range(30):
        value =  int(certidao[n]) * weight[n]
        sum = sum + value
    firstVerifyingDigit = sum % 11
    if firstVerifyingDigit == 10:
        firstVerifyingDigit = 1
    """ Calculating the second check digit of certidao. """
    sum = 0
    weight = [1,2,3,4,5,6,7,8,9,10,0,1,2,3,4,5,6,7,8,9,10,0,1,2,3,4,5,6,7,8,9]
    for n in range(31):
        sum = sum + int(certidao[n]) * weight[n]
    secondVerifyingDigit = sum % 11
    if secondVerifyingDigit == 10:
        secondVerifyingDigit = 1
    if certidao[-2:] == "%s%s" % (firstVerifyingDigit,secondVerifyingDigit):
        return True
    return False
def isProcessoValid(processo):
    """
        If processo in the Brazilian format is valid, it returns True, otherwise, it returns False.

        Format: NNNNNNN-DD.AAAA.J.TR.OOOO

        Onde:

        NNNNNNN - Número seqüencial do Processo, por Unidade de Origem, a ser reiniciado a cada ano

        DD - Dígito Verificador

        AAAA - Ano do ajuizamento do Processo

        J - Órgão ou Segmento do Poder Judiciário

        TR - Tribunal do respectivo Segmento do Poder Judiciário

        OOOO - Unidade de origem do Processo
    """
    # Check if type is str
    if not isinstance(processo,str):
        return False
    # Remove some unwanted characters
    processo = re.sub("[^0-9]",'',processo)
    # Checks if string has 11 characters
    if len(processo) != 20:
        return False
    """ Calculating the processo check digit. """
    sum = int(processo[0:7]+processo[9:20])*100
    VerifyingDigit = 98 - (sum % 97)
    if int(processo[7:9]) == VerifyingDigit:
        return True
    return False
def isCreditoValid(credito):
    """
        If credito in the Brazilian format is valid, it returns True, otherwise, it returns False.

        Format: 9999 9999 9999 999D
    """
    # Check if type is str
    if not isinstance(credito,str):
        return False
    # Remove some unwanted characters
    credito = re.sub("[^0-9]",'',credito)
    # Checks if string has 11 characters
    if len(credito) != 16:
        return False
    """ Calculating the credito check digit. """
    sum = 0
    weight = [2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]
    """ Calculating the first certidao check digit. """
    for n in range(15):
        value =  int(credito[n]) * weight[n]
        if value > 9:
            value = value - 9
        sum = sum + value
    VerifyingDigit = (math.ceil(sum/10)*10)-sum
    if int(credito[-1:]) == VerifyingDigit:
        return True
    return False
def isNfeValid(nfe):
    """
        If nfe in the Brazilian format is valid, it returns True, otherwise, it returns False.

        Format: UUAAMMCCCCCCCCCCCCCCmmSSSNNNNNNNNNFccccccccD

        Onde:

        UU - Código da UF do emitente do Documento Fiscal;

        AAMM - Ano e Mês de emissão da NF-e;

        CCCCCCCCCCCCCC - CNPJ do emitente;

        mm - Modelo do Documento Fiscal;
        
        SSS - Série do Documento Fiscal;

        NNNNNNNNN - Número do Documento Fiscal;

        F – forma de emissão da NF-e;

        cccccccc - Código Numérico que compõe a Chave de Acesso;

        D - Dígito Verificador da Chave de Acesso.
    """
    # Check if type is str
    if not isinstance(nfe,str):
        return False
    # Remove some unwanted characters
    nfe = re.sub("[^0-9]",'',nfe)
    # Checks if string has 11 characters
    if len(nfe) != 44:
        return False
    """ Calculating the nfe check digit. """
    sum = 0
    weight = [4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2,9,8,7,6,5,4,3,2]
    """ Calculating the first certidao check digit. """
    for n in range(43):
        value =  int(nfe[n]) * weight[n]
        sum = sum + value
    VerifyingDigit = 11 - (sum % 11)
    if int(nfe[-1:]) == VerifyingDigit:
        return True
    return False
def isTituloValid(titulo):
    """
        If titulo in the Brazilian format is valid, it returns True, otherwise, it returns False.

        Format: 9999 9999 UUDD

        Onde:

        9999 9999 - Código

        UU - Unidade da federacao

        DD - Digito Verificador
    """
    # Check if type is str
    if not isinstance(titulo,str):
        return False
    # Remove some unwanted characters
    titulo = re.sub("[^0-9]",'',titulo)
    # State
    state = titulo[8:10]
    # Checks if string has 11 characters
    if len(titulo) != 12:
        return False
    sum = 0
    weight = [2,3,4,5,6,7,8,9]
    """ Calculating the first titulo check digit. """
    for n in range(8):
        sum = sum + int(titulo[n]) * weight[n]
    verifyingDigit = sum % 11
    if verifyingDigit > 10 :
        verifyingDigit = 0
    if state == '01' or state == '02' and verifyingDigit == 0:
        verifyingDigit = 1
    firstVerifyingDigit = verifyingDigit
    """ Calculating the second check digit of titulo. """
    sum = (int(titulo[8]) * 7) + (int(titulo[9]) * 8) + (firstVerifyingDigit * 9)
    verifyingDigit = sum % 11
    if verifyingDigit > 10 :
        verifyingDigit = 0
    if state == '01' or state == '02' and verifyingDigit == 0:
        verifyingDigit = 1
    secondVerifyingDigit = verifyingDigit
    if titulo[-2:] == "%s%s" % (firstVerifyingDigit,secondVerifyingDigit):
        return True
    return False

@app.route('/dv', methods=['GET'])
def view_dv():
    """
    Description:
        Service to validate Digit Verification.
    Parameter:
        JSON {"certidao":string,
              "cnpj":string,
              "cpf":string,
              "credito":string,
              "ect":string,
              "nfe":string,
              "processo":string,
              "titulo":string}
    Return:
        True/False per each parameter passed named
        JSON {"certidao":True/False,
              "cnpj":True/False,
              "cpf":True/False,
              "credito":True/False,
              "ect":True/False,
              "nfe":True/False,
              "processo":True/False,
              "titulo":True/False}
    Usage:
        curl -X GET -i -H "Content-Type: application/json" -d "{\"certidao\":\"10453901552013100012021000012321\"}" http://127.0.0.1:8080/dv
        curl -X GET -i -H "Content-Type: application/json" -d "{\"cnpj\":\"30917504000131\"}" http://127.0.0.1:8080/dv
        curl -X GET -i -H "Content-Type: application/json" -d "{\"cpf\":\"622.560.920-20\"}" http://127.0.0.1:8080/dv
        curl -X GET -i -H "Content-Type: application/json" -d "{\"credito\":\"5491670040304243\"}" http://127.0.0.1:8080/dv
        curl -X GET -i -H "Content-Type: application/json" -d "{\"ect\":\"473124829\"}" http://127.0.0.1:8080/dv
        curl -X GET -i -H "Content-Type: application/json" -d "{\"nfe\":\"43171207364617000135550000000120141000120146\"}" http://127.0.0.1:8080/dv
        curl -X GET -i -H "Content-Type: application/json" -d "{\"processo\":\"00020802520125150049\"}" http://127.0.0.1:8080/dv
        curl -X GET -i -H "Content-Type: application/json" -d "{\"titulo\":\"053538810418\"}" http://127.0.0.1:8080/dv

        curl -X GET -i -H "Content-Type: application/json" -d "{\"certidao\":\"10453901552013100012021000012321\",\"cnpj\":\"30917504000131\", \"cpf\":\"62256092020\",\"credito\":\"5491670040304243\",\"ect\":\"473124829\",\"nfe\":\"43171207364617000135550000000120141000120146\",\"processo\":\"00020802520125150049\",\"titulo\":\"053538810418\"}" http://127.0.0.1:8080/dv
    Example:
        $ curl -X GET -i -H "Content-Type: application/json" -d "{\"certidao\":\"10453901552013100012021000012321\",\"cnpj\":\"30917504000131\", \"cpf\":\"62256092020\",\"credito\":\"5491670040304243\",\"ect\":\"473124829\",\"nfe\":\"43171207364617000135550000000120141000120146\",\"processo\":\"00020802520125150049\"}" http://127.0.0.1:8080/dv
          % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                         Dload  Upload   Total   Spent    Left  Speed
        100   349  100   123  100   226  61500   110k --:--:-- --:--:-- --:--:--  340k
        HTTP/1.0 200 OK
        Content-Type: application/json
        Content-Length: 123
        Access-Control-Allow-Origin: *
        Server: Werkzeug/0.16.0 Python/3.8.1
        Date: Mon, 17 Feb 2020 18:48:18 GMT
        
        "{\"certidao\": true, \"cnpj\": true, \"cpf\": true, \"credito\": true, \"ect\": true, \"nfe\": true, \"processo\": true}"
    """
    # TODO: Make the validation routine
    # TODO: Make the accounting routine
    reg          = {}
    if request.json == None:
        return jsonify( { 'error': 'No parameters found.' } )
    elif 'titulo' in request.json or 'nfe' in request.json or 'credito' in request.json or 'processo' in request.json or 'certidao' in request.json or 'ect' in request.json or 'cnpj' in request.json or 'cpf' in request.json:
        start = time.time()
        if 'certidao' in request.json:
            if not isinstance(request.json['certidao'],str):
                return jsonify( { 'error': 'CERTIDAO must be a string type.' } )
            elif len(request.json['certidao']) == 32:
                reg['certidao' ] = isCertidaoValid(request.json['certidao'])
            else:
                return jsonify( { 'error': 'CERTIDAO must be 32 lenght without mask.' } )
        if 'cnpj' in request.json:
            if not isinstance(request.json['cnpj'],str):
                return jsonify( { 'error': 'CNPJ must be a string type.' } )
            elif len(request.json['cnpj']) == 14:
                reg['cnpj' ] = isCnpjValid(request.json['cnpj'])
            else:
                return jsonify( { 'error': 'CNPJ must be 14 lenght without mask.' } )
        if 'cpf' in request.json:
            if not isinstance(request.json['cpf'],str):
                return jsonify( { 'error': 'CPF must be a string type.' } )
            elif len(request.json['cpf']) == 11:
                reg['cpf' ] = isCpfValid(request.json['cpf'])
            else:
                return jsonify( { 'error': 'CPF must be 11 lenght without mask.' } )
        if 'credito' in request.json:
            if not isinstance(request.json['credito'],str):
                return jsonify( { 'error': 'CREDITO must be a string type.' } )
            elif len(request.json['credito']) == 16:
                reg['credito' ] = isCreditoValid(request.json['credito'])
            else:
                return jsonify( { 'error': 'CREDITO must be 16 lenght without mask.' } )
        if 'ect' in request.json:
            if not isinstance(request.json['ect'],str):
                return jsonify( { 'error': 'ECT must be a string type.' } )
            elif len(request.json['ect']) == 9 or len(request.json['ect']) == 13:
                reg['ect' ] = isEctValid(request.json['ect'])
            else:
                return jsonify( { 'error': 'ECT must be 9 or 13 lenght without mask.' } )
        if 'nfe' in request.json:
            if not isinstance(request.json['nfe'],str):
                return jsonify( { 'error': 'NFE must be a string type.' } )
            elif len(request.json['nfe']) == 44:
                reg['nfe' ] = isNfeValid(request.json['nfe'])
            else:
                return jsonify( { 'error': 'NFE must be 44 lenght without mask.' } )
        if 'processo' in request.json:
            if not isinstance(request.json['processo'],str):
                return jsonify( { 'error': 'PROCESSO must be a string type.' } )
            elif len(request.json['processo']) == 20:
                reg['processo' ] = isProcessoValid(request.json['processo'])
            else:
                return jsonify( { 'error': 'PROCESSO must be 20 lenght without mask.' } )
        if 'titulo' in request.json:
            if not isinstance(request.json['titulo'],str):
                return jsonify( { 'error': 'TITULO must be a string type.' } )
            elif len(request.json['titulo']) == 12:
                reg['titulo' ] = isTituloValid(request.json['titulo'])
            else:
                return jsonify( { 'error': 'TITULO must be 12 lenght without mask.' } )
        json_result = json.dumps(reg)
        end = time.time()
        elapsed = end - start
        print(request.remote_addr, " - - ", datetime.datetime.now(), " elapsed: ", "{:.4f}".format(elapsed), " seconds")
        return jsonify(json_result)
    else:
        return jsonify( { 'error': 'No keys valid found.' } )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', '8080'))