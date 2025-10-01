import requests
import json

def create_epic(project, summary, description, due_date, epic_name, reporter_email, ticket, system, module):

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
    },
    "customfields": {
      "customfield_10022": original_estimate
    }
  }
  '''

  payloadObj = {
    "fields": {
      "project": {
        "key": project
      },
      "issuetype": {
        "name": name
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
      },
      "summary": summary,
      "assignee": {
        "id": assignee_id
      },
      "parent": {
        "key": parent_key
      }
    },
    "customfields": {
      "customfield_10022": original_estimate
    }
  }

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

  payload = json.dumps(payloadObj)

  response = requests.request("POST", url, headers=headers, data=payload)

  return response
