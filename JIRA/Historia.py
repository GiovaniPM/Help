import requests
import json

url = "https://tkebrasil.atlassian.net/rest/api/3/issue"

payload = json.dumps({
  "fields": {
    "project": {
      "key": "TRE"
    },
    "issuetype": {
      "name": "História"
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
              "text": "Estrutura de armazenamento no SAP"
            }
          ]
        }
      ]
    },
    "summary": "Estrutura de armazenamento no SAP",
    "assignee": {
      "id": "557058:004709f9-0a88-4979-a875-f58ca3985cf7"
    },
    "reporter": {
      "id": "712020:8364b9cf-88a2-4399-9f86-fff7bed77ce2"
    },
    "parent": {
      "key": "TRE-860"
    }
  },
  "customfields": {
    "customfield_10022": 0.5
  }
})
headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'Authorization': 'Basic Z2lvdmFuaS5tZXNxdWl0YUB0a2VsZXZhdG9yLmNvbTpBVEFUVDN4RmZHRjB4eldURlhnSUdYWjdFZjJyY2JCR3RKc0kyQzFMT1RRWERWRGhtcWlobE1mMjducFJ3WU5Za1dtY0x6dTM4T3lOU2Ixd1ZHVW1MQnBKRTB1cjhiTkx5UllZNDlJaXQxSmIzdFhqYmVqQWExVzZlbXNWdnhjaW5XOWVXOEQwTVE2eWx5eDJhbUtYQW5xaExUSzBUTDg2UEUzX0tCMFdpU1FLcl9WOXZmYUQ2VHM9MDk4QUIzQkE=',
  'Cookie': 'atlassian.xsrf.token=d161a0b3b93d7f39534e69925933f115d7c07a09_lin'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
