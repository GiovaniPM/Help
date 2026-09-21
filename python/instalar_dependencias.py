import importlib.util
import subprocess
import sys

# nome do módulo para importar -> nome do pacote no pip
BIBLIOTECAS = {
    "numpy": "numpy",
    "bokeh": "bokeh",
}


def instalada(modulo):
    return importlib.util.find_spec(modulo) is not None


def instalar(pacote):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])


def verificar_e_instalar(bibliotecas=BIBLIOTECAS):
    for modulo, pacote in bibliotecas.items():
        if instalada(modulo):
            print(f"[OK] {pacote} já está instalada.")
            continue
        print(f"[..] {pacote} não encontrada. Instalando...")
        try:
            instalar(pacote)
            print(f"[OK] {pacote} instalada com sucesso.")
        except subprocess.CalledProcessError:
            print(f"[ERRO] Falha ao instalar {pacote}.")
            sys.exit(1)


if __name__ == "__main__":
    verificar_e_instalar()
