import http.client
import json

token = "bb37c60db7af2928d142d6a2"
conn = http.client.HTTPSConnection("v6.exchangerate-api.com")
payload = ''
headers = {}
conn.request("GET", "/v6/" + token + "/latest/BRL", payload, headers)
res = conn.getresponse()
data = res.read()
json_data = data.decode("utf-8")
json_object = json.loads(json_data)
json_formatted_str =  json.dumps(json_object, indent=2)
print(json_formatted_str)