import http.client
import json

conn = http.client.HTTPSConnection("viacep.com.br")
payload = ''
headers = {}
cep = input('Insira o CEP, somente números sem separadores: ')
conn.request("GET", "/ws/" + cep + "/json/", payload, headers)
res = conn.getresponse()
data = res.read()
json_data = data.decode("utf-8")
json_object = json.loads(json_data)
json_formatted_str =  json.dumps(json_object, indent=2)
print(json_formatted_str)