import importlib.util
import os
import platform
import subprocess
import sys

VERMELHO = "\033[91m"
RESET = "\033[0m"

# nome do módulo para importar -> nome do pacote no pip
BIBLIOTECAS = {
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
    "pymongo": "pymongo",  # também fornece o módulo bson
    "redis": "redis",
    "zmq": "pyzmq",
    "libtorrent": "libtorrent",
    "openai": "openai",
    "google.genai": "google-genai",
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


def consultar_ia(pacote, saida):
    """Pede ao Gemini um diagnóstico e alternativas; nunca levanta exceção."""
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


def gravar_erro(pacote, saida):
    caminho = f"{pacote}.insterr"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"=== DETALHAMENTO DA INSTALAÇÃO ===\n{saida}\n")
        arquivo.write(f"\n=== ANÁLISE DA IA ===\n{consultar_ia(pacote, saida)}\n")
    return caminho


def verificar_e_instalar(bibliotecas=BIBLIOTECAS):
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
            caminho = gravar_erro(pacote, saida)
            print(
                f"{VERMELHO}[ERRO] Falha ao instalar {pacote}. "
                f"Detalhes em {caminho}{RESET}"
            )
            falhas.append(pacote)

    if falhas:
        print(f"\n{VERMELHO}Não foi possível instalar: {', '.join(falhas)}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    verificar_e_instalar()
