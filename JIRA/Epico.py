import requests
import json

url = "https://tkebrasil.atlassian.net/rest/api/3/issue"

payload = json.dumps({
  "fields": {
    "project": {
      "key": "TRE"
    },
    "issuetype": {
      "name": "Epic"
    },
    "summary": "Teste Giovani 001",
    "customfield_10018": "Teste Giovani 001",
    "customfield_10104": "2025-09-23",
    "customfield_10105": 0,
    "customfield_10300": "0",
    "customfield_10107": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Teste Giovani 001"
            }
          ]
        }
      ]
    },
    "customfield_10102": {
      "value": "INTERFACE"
    },
    "customfield_10103": {
      "value": "ALTERAÇÃO"
    },
    "customfield_10101": "ensemble@thyssenkruppelevadores.com.br"
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
