import requests
import json

def create_epic(project, summary, description, due_date, epic_name, reporter_email, ticket, system, module):

  payloadObj = {
    "fields": {}
  }

  payloadObj["fields"]["customfield_10018"] = epic_name
  payloadObj["fields"]["customfield_10101"] = reporter_email
  payloadObj["fields"]["customfield_10102"] = {"value": system}
  payloadObj["fields"]["customfield_10103"] = {"value": module}
  payloadObj["fields"]["customfield_10104"] = due_date
  payloadObj["fields"]["customfield_10105"] = 0
  payloadObj["fields"]["customfield_10107"] = {"type": "doc","version": 1,"content": [{"type": "paragraph","content": [{"type": "text","text": description}]}]}
  payloadObj["fields"]["customfield_10300"] = ticket
  payloadObj["fields"]["issuetype"] = {"name": "Epic"}
  payloadObj["fields"]["project"] = {"key": project}
  payloadObj["fields"]["summary"] = summary[:255]
  
  payload = json.dumps(payloadObj)
  
  print(payload)

  response = requests.request("POST", url, headers=headers, data=payload)

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
  payloadObj["fields"]["summary"] = summary[:255]  
  
  payload = json.dumps(payloadObj)
  
  print(payload)

  response = requests.request("POST", url, headers=headers, data=payload)

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
  payloadObj["fields"]["summary"] = summary[:255]
  payloadObj["fields"]["timetracking"] = {"originalEstimate": original_estimate}
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", url, headers=headers, data=payload)

  return response
