import jiralib
import json
import requests
import sys

# Configurações
SETUP_FILE = "setup.json"

def carregar_configuracoes_jira() -> None:
    """
    Carrega as configurações de conexão com o Jira a partir do arquivo setup.json.
    Isso mantém as credenciais e a URL fora do código, o que é mais seguro!
    """
    try:
        with open(SETUP_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Supondo que 'jiralib' seja um módulo que você tem.
            # Se não for, você precisará importar ou definir 'jiralib'.
            jiralib.url = config['url']
            if not jiralib.url.startswith("http"):
                jiralib.url = "https://" + jiralib.url.strip("/")
            jiralib.headers = config['headers']
            print("✓ Configurações do Jira carregadas com sucesso!")
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo de configuração '{SETUP_FILE}' não encontrado.")
        sys.exit(1) # Encerra o script se o arquivo de configuração não existir.
    except KeyError:
        print(f"❌ Erro: O arquivo '{SETUP_FILE}' está mal formatado. 'url' ou 'headers' não encontrados.")
        sys.exit(1)

if __name__ == "__main__":

    carregar_configuracoes_jira()

    with open("tickets.txt", "w", encoding="utf-8") as f:

        output_line = f"Ticket   || "\
                      f"Tipo            || "\
                      f"Data       || "\
                      f"Pai      || "\
                      f"Incidente       || "\
                      f"Descrição                                          ||"
    
        f.write(output_line + "\n")
        print(output_line)
    
        # Endpoint para buscar issues
        url = f"{jiralib.url}/rest/api/3/search/jql"
        start_at = 0
        nextPageToken = ""

        while start_at < 1000:
            # Parâmetros da busca
            query = {
                "jql": f'project = IRIS AND (issuetype = Epic OR (issuetype != Epic AND "Epic Link" IS NOT EMPTY)) ORDER BY key DESC',
                "nextPageToken": nextPageToken,
                "maxResults": 100,
                "fields": ["*all"]
            }
            
            # Requisição
            response = requests.get(url, headers=jiralib.headers, params=query)
            
            if response.status_code == 200:
                issues = response.json().get("issues", [])
                for issue in issues:
                    summary = issue['fields']['summary'][:50]
                    try:
                        output_line = f"{issue['key']} || "\
                                      f"{issue['fields']['issuetype']['name']:<15} || "\
                                      f"{issue['fields']['created'][:10]} || "\
                                      f"{issue['fields']['parent']['key']} || "\
                                      f"                || "\
                                      f"{summary:<50} ||"
                    except:
                        output_line = f"{issue['key']} || "\
                                      f"{issue['fields']['issuetype']['name']:<15} || "\
                                      f"{issue['fields']['created'][:10]} || "\
                                      f"{issue['key']} || "\
                                      f"{issue['fields']['customfield_10300']:<15} || "\
                                      f"{summary:<50} ||"
                    f.write(output_line + "\n")
                    print(output_line)
            else:
                print(f"Erro: {response.status_code} - {response.text}")
            start_at += 100
            nextPageToken = response.json().get("nextPageToken", [])