import requests
import json
import logging
import re
import unicodedata

from datetime import datetime

def create_epic(project, summary, description, due_date, epic_name, reporter_email, ticket, system, module):

  payloadObj = {
    "fields": {}
  }

  payloadObj["fields"]["customfield_10018"] = normalize_text(epic_name)[:255]  
  payloadObj["fields"]["customfield_10101"] = reporter_email
  payloadObj["fields"]["customfield_10102"] = {"value": system}
  payloadObj["fields"]["customfield_10103"] = {"value": module}
  payloadObj["fields"]["customfield_10104"] = due_date
  payloadObj["fields"]["customfield_10105"] = 0
  payloadObj["fields"]["customfield_10107"] = {"type": "doc","version": 1,"content": [{"type": "paragraph","content": [{"type": "text","text": description}]}]}
  payloadObj["fields"]["customfield_10300"] = ticket
  payloadObj["fields"]["issuetype"] = {"name": "Epic"}
  payloadObj["fields"]["project"] = {"key": project}
  payloadObj["fields"]["summary"] = normalize_text(summary)[:255]
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", f"{url}/rest/api/3/issue", headers=headers, data=payload)

  return response

def create_story(project, name, summary, description, assignee_id, reporter_id, parent_key, original_estimate):

  payloadObj = {
    "fields": {}
  }

  payloadObj["fields"]["assignee"] = {"id": assignee_id}
  payloadObj["fields"]["customfield_10022"] = original_estimate
  payloadObj["fields"]["description"] = {"type": "doc","version": 1,"content": [{"type": "paragraph","content": [{"type": "text","text": description}]}]}
  payloadObj["fields"]["issuetype"] = {"name": name}
  payloadObj["fields"]["parent"] = {"key": parent_key}
  payloadObj["fields"]["project"] = {"key": project}
  if project not in ['TRE']:
    payloadObj["fields"]["reporter"] = {"id": reporter_id}
  payloadObj["fields"]["summary"] = normalize_text(summary)[:255]  
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", f"{url}/rest/api/3/issue", headers=headers, data=payload)

  return response

def create_task(project, name, summary, description, assignee_id, reporter_id, parent_key, original_estimate):

  payloadObj = {
    "fields": {}
  }

  payloadObj["fields"]["assignee"] = {"id": assignee_id}
  payloadObj["fields"]["description"] = {"type": "doc","version": 1,"content": [{"type": "paragraph","content": [{"type": "text","text": description}]}]}
  payloadObj["fields"]["issuetype"] = {"name": name}
  payloadObj["fields"]["parent"] = {"key": parent_key}
  payloadObj["fields"]["project"] = {"key": project}
  if project not in ['TRE']:
    payloadObj["fields"]["reporter"] = {"id": reporter_id}
  payloadObj["fields"]["summary"] = normalize_text(summary)[:255]
  payloadObj["fields"]["timetracking"] = {"originalEstimate": original_estimate}
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", f"{url}/rest/api/3/issue", headers=headers, data=payload)

  return response

def advance_status(parent_key, status_id):

  payloadObj = {
    "transition": {}
  }

  payloadObj["transition"]["id"] = status_id
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", f"{url}/rest/api/2/issue/{parent_key}/transitions", headers=headers, data=payload)

  return response


def normalize_text(input_text: str) -> str:
    # Remove quebras de linha
    input_text = input_text.replace('\n', ' ').replace('\r', ' ')
    
    # Normaliza para ASCII
    normalized = unicodedata.normalize('NFKD', input_text)
    ascii_text = normalized.encode('ASCII', 'ignore').decode('ASCII')
    
    # Remove caracteres especiais, mantendo letras, números e espaços
    return re.sub(r'[^a-zA-Z0-9 ]', '', ascii_text)

def add_output(text: str) -> None:

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cleaned_text = normalize_text(text)

    logging.info(f"{timestamp} - {cleaned_text}")
    print(text)