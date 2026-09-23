import argparse

parser = argparse.ArgumentParser(description="Exemplo de parâmetro")
parser.add_argument('--nome', type=str, required=True, help='Seu nome')
args = parser.parse_args()

print("Nome recebido:", args.nome)
