#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  Copilot Prompt App
  Aplicação que solicita um prompt ao usuário, envia para a API da
  Azure OpenAI (motor do Copilot) e salva a resposta em um arquivo .txt.
=============================================================================

  COMO USAR:
  ----------
  1. Instale a biblioteca openai (caso ainda não tenha):
       pip install openai

  2. Configure as variáveis abaixo OU defina variáveis de ambiente:
       - AZURE_OPENAI_ENDPOINT  (ex: https://seu-recurso.openai.azure.com/)
       - AZURE_OPENAI_API_KEY   (sua chave de API)
       - AZURE_OPENAI_DEPLOYMENT (nome do deployment, ex: gpt-4o)
       - AZURE_OPENAI_API_VERSION (ex: 2024-02-15-preview)

     ** Alternativamente, se você tiver uma chave da OpenAI direta: **
       - OPENAI_API_KEY

  3. Execute o script:
       python copilot_prompt.py

  4. Digite seu prompt quando solicitado. A resposta será exibida no
     terminal e salva automaticamente em um arquivo .txt.

  5. Digite "sair" para encerrar a aplicação.
=============================================================================
"""

import os
import sys
import datetime

# ============================================================================
# CONFIGURAÇÃO - Preencha aqui ou defina variáveis de ambiente
# ============================================================================

# Opção 1: Azure OpenAI (recomendado para ambiente corporativo)
AZURE_OPENAI_ENDPOINT   = os.getenv("AZURE_OPENAI_ENDPOINT", "")      # Ex: "https://seu-recurso.openai.azure.com/"
AZURE_OPENAI_API_KEY    = os.getenv("AZURE_OPENAI_API_KEY", "")       # Sua chave de API
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")    # Ex: "gpt-4o"
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Opção 2: OpenAI direta (se não usar Azure)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o")

# Pasta para salvar as respostas (será criada automaticamente)
PASTA_SAIDA = "respostas_copilot"

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def instalar_openai():
    """Tenta instalar a biblioteca openai caso não esteja disponível."""
    print("📦 Biblioteca 'openai' não encontrada. Instalando...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "-q"])
        print("✅ Biblioteca 'openai' instalada com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao instalar a biblioteca 'openai': {e}")
        print("   Tente instalar manualmente com: pip install openai")
        sys.exit(1)


def obter_cliente():
    """
    Retorna o cliente da OpenAI configurado.
    Prioridade: Azure OpenAI > OpenAI direta.
    """
    try:
        import openai
    except ImportError:
        instalar_openai()
        import openai

    # Opção 1: Azure OpenAI
    if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_DEPLOYMENT:
        from openai import AzureOpenAI
        cliente = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
        )
        modelo = AZURE_OPENAI_DEPLOYMENT
        print("🔗 Conectado à Azure OpenAI.")
        return cliente, modelo

    # Opção 2: OpenAI direta
    elif OPENAI_API_KEY:
        from openai import OpenAI
        cliente = OpenAI(api_key=OPENAI_API_KEY)
        modelo = OPENAI_MODEL
        print("🔗 Conectado à OpenAI.")
        return cliente, modelo

    else:
        print("=" * 60)
        print("⚠️  CONFIGURAÇÃO NECESSÁRIA")
        print("=" * 60)
        print()
        print("Nenhuma chave de API foi configurada.")
        print("Por favor, configure uma das opções abaixo:")
        print()
        print("  OPÇÃO 1 - Azure OpenAI (variáveis de ambiente):")
        print("    set AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com/")
        print("    set AZURE_OPENAI_API_KEY=sua-chave-aqui")
        print("    set AZURE_OPENAI_DEPLOYMENT=gpt-4o")
        print()
        print("  OPÇÃO 2 - OpenAI direta (variável de ambiente):")
        print("    set OPENAI_API_KEY=sua-chave-aqui")
        print()
        print("  Ou edite as variáveis diretamente no arquivo copilot_prompt.py")
        print("=" * 60)
        sys.exit(1)


def enviar_prompt(cliente, modelo, prompt, historico=None):
    """
    Envia o prompt para a API e retorna a resposta.
    
    Args:
        cliente: cliente OpenAI/AzureOpenAI
        modelo: nome do modelo/deployment
        prompt: texto do prompt do usuário
        historico: lista de mensagens anteriores (para contexto)
    
    Returns:
        str: texto da resposta
    """
    if historico is None:
        historico = []

    mensagens = [
        {"role": "system", "content": "Você é um assistente útil e responde em português do Brasil."}
    ] + historico + [
        {"role": "user", "content": prompt}
    ]

    try:
        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=mensagens,
            temperature=0.7,
            max_tokens=4096,
        )
        return resposta.choices[0].message.content

    except Exception as e:
        return f"❌ Erro ao obter resposta da API: {e}"


def salvar_resposta(prompt, resposta):
    """
    Salva o prompt e a resposta em um arquivo .txt com timestamp.
    
    Returns:
        str: caminho do arquivo salvo
    """
    # Criar pasta de saída se não existir
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    # Gerar nome do arquivo com timestamp
    agora = datetime.datetime.now()
    timestamp = agora.strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"copilot_resposta_{timestamp}.txt"
    caminho = os.path.join(PASTA_SAIDA, nome_arquivo)

    # Escrever o conteúdo no arquivo
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"{'=' * 60}\n")
        f.write(f"  Data/Hora: {agora.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(f"📝 PROMPT:\n")
        f.write(f"{'-' * 40}\n")
        f.write(f"{prompt}\n\n")
        f.write(f"🤖 RESPOSTA:\n")
        f.write(f"{'-' * 40}\n")
        f.write(f"{resposta}\n")

    return caminho


# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

def main():
    print()
    print("=" * 60)
    print("  🤖  COPILOT PROMPT APP")
    print("  Envie prompts e receba respostas salvas em .txt")
    print("=" * 60)
    print()

    # Obter cliente configurado
    cliente, modelo = obter_cliente()
    print(f"📌 Modelo: {modelo}")
    print(f"📂 Respostas serão salvas em: ./{PASTA_SAIDA}/")
    print(f"💡 Digite 'sair' para encerrar.\n")

    # Histórico da conversa (para manter contexto)
    historico = []
    contador = 0

    while True:
        print("-" * 60)
        prompt = input("📝 Digite seu prompt:\n> ").strip()

        # Verificar se o usuário quer sair
        if prompt.lower() in ("sair", "exit", "quit", "q"):
            print("\n👋 Encerrando. Até a próxima!")
            break

        # Verificar se o prompt não está vazio
        if not prompt:
            print("⚠️  Prompt vazio. Tente novamente.\n")
            continue

        print("\n⏳ Aguardando resposta...")

        # Enviar prompt e obter resposta
        resposta = enviar_prompt(cliente, modelo, prompt, historico)

        # Exibir resposta no terminal
        print(f"\n🤖 RESPOSTA:\n{'-' * 40}")
        print(resposta)
        print(f"{'-' * 40}")

        # Salvar resposta em arquivo .txt
        caminho = salvar_resposta(prompt, resposta)
        print(f"\n💾 Resposta salva em: {caminho}")

        # Atualizar histórico para manter contexto
        historico.append({"role": "user", "content": prompt})
        historico.append({"role": "assistant", "content": resposta})

        # Limitar histórico para não exceder limites de tokens
        if len(historico) > 20:
            historico = historico[-20:]

        contador += 1
        print(f"📊 Total de perguntas nesta sessão: {contador}\n")

    print(f"\n📊 Sessão encerrada. {contador} pergunta(s) realizada(s).")
    if contador > 0:
        print(f"📂 Respostas salvas em: ./{PASTA_SAIDA}/")


if __name__ == "__main__":
    main()
