import requests
import json

def create_epic(project, summary, description, due_date, epic_name, reporter_email, ticket, system, module):

  '''
  payloadObj = {
    "fields": {
      "project": {
        "key": project
      },
      "issuetype": {
        "name": "Epic"
      },
      "summary": summary,
      "customfield_10018": epic_name,
      "customfield_10104": due_date,
      "customfield_10105": 0,
      "customfield_10300": ticket,
      "customfield_10107": {
        "type": "doc",
        "version": 1,
        "content": [
          {
            "type": "paragraph",
            "content": [
              {
                "type": "text",
                "text": description
              }
            ]
          }
        ]
      },
      "customfield_10102": {
        "value": system
      },
      "customfield_10103": {
        "value": module
      },
      "customfield_10101": reporter_email
    }
  }
  '''

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
  payloadObj["fields"]["summary"] = summary
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", url, headers=headers, data=payload)

  return response

def create_story(project, name, summary, description, assignee_id, reporter_id, parent_key, original_estimate):

  '''
  payloadObj = {
    "fields": {
      "project": {
        "key": project
      },
      "issuetype": {
        "name": name
      },
      "customfield_10022": original_estimate,
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {
            "type": "paragraph",
            "content": [
              {
                "type": "text",
                "text": description
              }
            ]
          }
        ]
      },
      "summary": summary,
      "assignee": {
        "id": assignee_id
      },
      "reporter": {
        "id": reporter_id
      },
      "parent": {
        "key": parent_key
      }
    }
  }
  '''

  '''
  payloadObj = {
    "fields": {
      "project": {
        "key": project
      },
      "issuetype": {
        "name": name
      },
      "customfield_10022": original_estimate,
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {
            "type": "paragraph",
            "content": [
              {
                "type": "text",
                "text": description
              }
            ]
          }
        ]
      },
      "summary": summary,
      "assignee": {
        "id": assignee_id
      },
      "parent": {
        "key": parent_key
      }
    },
  }
  '''

  payloadObj = {
    "fields": {}
  }

  payloadObj["fields"]["assignee"] = {"id": assignee_id}
  payloadObj["fields"]["customfield_10022"] = original_estimate
  payloadObj["fields"]["description"] = {"type": "doc","version": 1,"content": [{"type": "paragraph","content": [{"type": "text","text": description}]}]}
  payloadObj["fields"]["issuetype"] = {"name": name}
  payloadObj["fields"]["parent"] = {"key": parent_key}
  payloadObj["fields"]["project"] = {"key": project}
  payloadObj["fields"]["reporter"] = {"id": reporter_id}
  payloadObj["fields"]["summary"] = summary  
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", url, headers=headers, data=payload)

  return response

def create_task(project, name, summary, description, assignee_id, reporter_id, parent_key, original_estimate):

  '''
  payloadObj = {
    "fields": {
      "project": {
        "key": project
      },
      "issuetype": {
        "name": name
      },
      "summary": summary,
      "assignee": {
        "id": assignee_id
      },
      "reporter": {
        "id": reporter_id
      },
      "timetracking": {
        "originalEstimate": original_estimate
      },
      "parent": {
        "key": parent_key
      },
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {
            "type": "paragraph",
            "content": [
              {
                "type": "text",
                "text": description
              }
            ]
          }
        ]
      }
    }
  }
  '''

  '''
  payloadObj = {
    "fields": {
      "project": {
        "key": project
      },
      "issuetype": {
        "name": name
      },
      "summary": summary,
      "assignee": {
        "id": assignee_id
      },
      "timetracking": {
        "originalEstimate": original_estimate
      },
      "parent": {
        "key": parent_key
      },
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {
            "type": "paragraph",
            "content": [
              {
                "type": "text",
                "text": description
              }
            ]
          }
        ]
      }
    }
  }
  '''

  payloadObj = {
    "fields": {}
  }

  payloadObj["fields"]["assignee"] = {"id": assignee_id}
  payloadObj["fields"]["description"] = {"type": "doc","version": 1,"content": [{"type": "paragraph","content": [{"type": "text","text": description}]}]}
  payloadObj["fields"]["issuetype"] = {"name": name}
  payloadObj["fields"]["parent"] = {"key": parent_key}
  payloadObj["fields"]["project"] = {"key": project}
  payloadObj["fields"]["reporter"] = {"id": reporter_id}
  payloadObj["fields"]["summary"] = summary
  payloadObj["fields"]["timetracking"] = {"originalEstimate": original_estimate}
  
  payload = json.dumps(payloadObj)

  response = requests.request("POST", url, headers=headers, data=payload)

  return response
