import http.client
import json

token = "4759%7CNKBm8YLSvwLBw3OkdqOlGPCK15ex8444"
conn = http.client.HTTPSConnection("api.invertexto.com")
payload = ''
headers = {}
cic = input('Insira o CNPJ, somente números sem separadores: ')
#conn.request("GET", "/v1/cnpj/79227963000182?token=4759%7CNKBm8YLSvwLBw3OkdqOlGPCK15ex8444", payload, headers)
conn.request("GET", "/v1/cnpj/" + cic + "?token=" + token, payload, headers)
res = conn.getresponse()
data = res.read()
json_data = data.decode("utf-8")
json_object = json.loads(json_data)
json_formatted_str =  json.dumps(json_object, indent=2)
print(json_formatted_str)