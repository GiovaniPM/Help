import argparse
import importlib.util
import os
import platform
import subprocess
import sys

"""
  COMO USAR:
  ----------
  1. Obtenha sua API Key gratuita:
       - Acesse: https://aistudio.google.com
          - https://console.cloud.google.com/
       - Faça login com sua conta Google
       - Clique em "Get API Key" → "Create API Key"
       - Copie a chave gerada

  2. Instale a biblioteca (caso ainda não tenha):
       pip install google-genai

  3. Configure a variável de ambiente:
       Windows CMD:   set GEMINI_API_KEY=sua-chave-aqui
       PowerShell:    $env:GEMINI_API_KEY = "sua-chave-aqui"
       Linux/macOS:   export GEMINI_API_KEY="sua-chave-aqui"

  4. Por padrão a consulta à IA fica DESATIVADA quando um pacote falhar
     ao instalar. Para ativá-la:
       Variável de ambiente:  set USAR_IA_DIAGNOSTICO=1
       Linha de comando:      python instalar_dependencias.py --com-ia
"""

VERMELHO = "\033[91m"
RESET = "\033[0m"

# Liga/desliga por padrão a consulta à IA em caso de falha na instalação.
# Sem nenhuma opção informada, o padrão é NÃO consultar (--sem-ia).
# Pode ser sobrescrito por variável de ambiente (USAR_IA_DIAGNOSTICO=0/1) ou
# pela flag --sem-ia / --com-ia na linha de comando.
USAR_IA_PADRAO = os.getenv("USAR_IA_DIAGNOSTICO", "0").strip().lower() not in (
    "0",
    "false",
    "nao",
    "não",
)

# nome do módulo para importar -> nome do pacote no pip
BIBLIOTECAS = {
    "google.genai": "google-genai",
    "openai": "openai",
    "numpy": "numpy",
    "bokeh": "bokeh",
    "pandas": "pandas",
    "openpyxl": "openpyxl",
    "xlsxwriter": "XlsxWriter",
    "plotly": "plotly",
    "tensorflow": "tensorflow",
    "streamlit": "streamlit",
    "flask": "flask",
    "flask_cors": "flask-cors",
    "requests": "requests",
    "bs4": "beautifulsoup4",
    "chardet": "chardet",
    "cryptography": "cryptography",
    "pycep_correios": "pycep-correios",
    "customtkinter": "customtkinter",
    "PIL": "pillow",
    "cx_Oracle": "cx_Oracle",
    "oracledb": "oracledb",
    "pymongo": "pymongo",  # também fornece o módulo bson
    "redis": "redis",
    "zmq": "pyzmq",
    "libtorrent": "libtorrent",
    "pipwin": "pipwin",  # instalador de wheels não-oficiais p/ pacotes sem wheel no pip (Windows)
}


def instalada(modulo):
    try:
        return importlib.util.find_spec(modulo) is not None
    except ModuleNotFoundError:  # pacote pai (ex.: "google") ausente
        return False


def instalar(pacote):
    """Instala o pacote; retorna (sucesso, saída completa do pip)."""
    resultado = subprocess.run(
        [sys.executable, "-m", "pip", "install", pacote],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return resultado.returncode == 0, resultado.stdout


def consultar_ia(pacote, saida, usar_ia=USAR_IA_PADRAO):
    """Pede ao Gemini um diagnóstico e alternativas; nunca levanta exceção."""
    if not usar_ia:
        return "Consulta à IA desativada (USAR_IA_DIAGNOSTICO=0 ou --sem-ia)."
    chave = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not chave:
        return "Consulta à IA não realizada: defina GEMINI_API_KEY (ou GOOGLE_API_KEY)."
    try:
        from google import genai
    except ImportError:
        return "Consulta à IA não realizada: biblioteca google-genai não instalada."

    prompt = (
        f"A instalação do pacote Python '{pacote}' via pip falhou.\n"
        f"Ambiente: Python {sys.version.split()[0]}, "
        f"{platform.platform()}, {platform.machine()}.\n\n"
        "Saída completa do pip:\n"
        f"{saida[-12000:]}\n\n"
        "Em português: (1) identifique a causa provável do erro; "
        "(2) sugira alternativas de solução, em ordem de probabilidade de "
        "sucesso, com os comandos exatos a executar."
    )
    try:
        cliente = genai.Client(api_key=chave)
        modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        return cliente.models.generate_content(model=modelo, contents=prompt).text
    except Exception as erro:
        return f"Consulta à IA falhou: {erro}"


def gravar_erro(pacote, saida, usar_ia=USAR_IA_PADRAO):
    caminho = f"{pacote}.insterr"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"=== DETALHAMENTO DA INSTALAÇÃO ===\n{saida}\n")
        arquivo.write(f"\n=== ANÁLISE DA IA ===\n{consultar_ia(pacote, saida, usar_ia)}\n")
    return caminho


def verificar_e_instalar(bibliotecas=BIBLIOTECAS, usar_ia=USAR_IA_PADRAO):
    if os.name == "nt":
        os.system("")  # habilita sequências ANSI no terminal do Windows
    falhas = []
    for modulo, pacote in bibliotecas.items():
        if instalada(modulo):
            print(f"[OK] {pacote} já está instalada.")
            continue
        sucesso, saida = instalar(pacote)
        if sucesso:
            print(f"[OK] {pacote} instalada com sucesso.")
        else:
            caminho = gravar_erro(pacote, saida, usar_ia)
            print(
                f"{VERMELHO}[ERRO] Falha ao instalar {pacote}. "
                f"Detalhes em {caminho}{RESET}"
            )
            falhas.append(pacote)

    if falhas:
        print(f"\n{VERMELHO}Não foi possível instalar: {', '.join(falhas)}{RESET}")
        sys.exit(1)


def analisar_argumentos():
    parser = argparse.ArgumentParser(description="Verifica e instala as dependências do projeto.")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument(
        "--sem-ia",
        dest="usar_ia",
        action="store_false",
        default=USAR_IA_PADRAO,
        help="Não consultar a IA (Gemini) quando uma instalação falhar.",
    )
    grupo.add_argument(
        "--com-ia",
        dest="usar_ia",
        action="store_true",
        help="Forçar a consulta à IA quando uma instalação falhar.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    argumentos = analisar_argumentos()
    verificar_e_instalar(usar_ia=argumentos.usar_ia)
