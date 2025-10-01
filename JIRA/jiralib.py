import requests
import json

'''
url = "https://tkebrasil.atlassian.net/rest/api/3/issue"

headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Authorization': 'Basic Z2lvdmFuaS5tZXNxdWl0YUB0a2VsZXZhdG9yLmNvbTpBVEFUVDN4RmZHRjB4eldURlhnSUdYWjdFZjJyY2JCR3RKc0kyQzFMT1RRWERWRGhtcWlobE1mMjducFJ3WU5Za1dtY0x6dTM4T3lOU2Ixd1ZHVW1MQnBKRTB1cjhiTkx5UllZNDlJaXQxSmIzdFhqYmVqQWExVzZlbXNWdnhjaW5XOWVXOEQwTVE2eWx5eDJhbUtYQW5xaExUSzBUTDg2UEUzX0tCMFdpU1FLcl9WOXZmYUQ2VHM9MDk4QUIzQkE=',
  'Cookie': 'atlassian.xsrf.token=d161a0b3b93d7f39534e69925933f115d7c07a09_lin'
}
'''

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
