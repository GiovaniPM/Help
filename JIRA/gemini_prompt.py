#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
  Gemini Prompt App
  Aplicação que solicita um prompt ao usuário, envia para a API do
  Google Gemini e salva a resposta em um arquivo .txt.
=============================================================================

  COMO USAR:
  ----------
  1. Obtenha sua API Key gratuita:
       - Acesse: https://aistudio.google.com
       - Faça login com sua conta Google
       - Clique em "Get API Key" → "Create API Key"
       - Copie a chave gerada

  2. Instale a biblioteca (caso ainda não tenha):
       pip install google-genai

  3. Configure a variável de ambiente:
       Windows CMD:   set GEMINI_API_KEY=sua-chave-aqui
       PowerShell:    $env:GEMINI_API_KEY = "sua-chave-aqui"
       Linux/macOS:   export GEMINI_API_KEY="sua-chave-aqui"

     Ou edite a variável GEMINI_API_KEY diretamente neste arquivo.

  4. Execute o script:
       python gemini_prompt.py

  5. Digite seu prompt quando solicitado. A resposta será exibida no
     terminal e salva automaticamente em um arquivo .txt.

  6. Digite "sair" para encerrar a aplicação.

  MODELOS DISPONÍVEIS (Tier Gratuito):
  ------------------------------------
  - gemini-3.5-flash   (recomendado - rápido e inteligente)
  - gemini-2.5-flash   (equilibrado)
  - gemini-2.5-pro     (raciocínio avançado)
  - gemini-2.0-flash   (leve e rápido)
=============================================================================
"""

import os
import sys
import datetime

# ============================================================================
# CONFIGURAÇÃO - Preencha aqui ou defina variáveis de ambiente
# ============================================================================

# Chave da API do Gemini (obtenha em https://aistudio.google.com)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "AIzaSyAdrRQZ5vCJsIRxGvqfAZ3qmDMM3vBjztk"

# Modelo a ser utilizado (pode alterar conforme necessidade)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Pasta para salvar as respostas (será criada automaticamente)
PASTA_SAIDA = "respostas_gemini"

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def instalar_genai():
    """Tenta instalar a biblioteca google-genai caso não esteja disponível."""
    print("📦 Biblioteca 'google-genai' não encontrada. Instalando...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "-q"])
        print("✅ Biblioteca 'google-genai' instalada com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao instalar a biblioteca 'google-genai': {e}")
        print("   Tente instalar manualmente com: pip install google-genai")
        sys.exit(1)


def obter_cliente():
    """
    Retorna o cliente do Gemini configurado com a API Key.
    """
    # Importar a biblioteca (instalar se necessário)
    try:
        from google import genai
    except ImportError:
        instalar_genai()
        from google import genai

    # Verificar se a API Key foi configurada
    if not GEMINI_API_KEY:
        print("=" * 60)
        print("⚠️  CONFIGURAÇÃO NECESSÁRIA")
        print("=" * 60)
        print()
        print("Nenhuma API Key do Gemini foi configurada.")
        print()
        print("  PASSO 1 - Obtenha sua chave gratuita:")
        print("    Acesse: https://aistudio.google.com")
        print("    Clique em 'Get API Key' → 'Create API Key'")
        print()
        print("  PASSO 2 - Configure a variável de ambiente:")
        print("    Windows CMD:   set GEMINI_API_KEY=sua-chave-aqui")
        print("    PowerShell:    $env:GEMINI_API_KEY = \"sua-chave-aqui\"")
        print("    Linux/macOS:   export GEMINI_API_KEY=\"sua-chave-aqui\"")
        print()
        print("  Ou edite a variável GEMINI_API_KEY diretamente neste arquivo.")
        print("=" * 60)
        sys.exit(1)

    # Criar cliente com a API Key
    try:
        cliente = genai.Client(api_key=GEMINI_API_KEY)
        print("🔗 Conectado à API do Google Gemini.")
        return cliente
    except Exception as e:
        print(f"❌ Erro ao criar cliente Gemini: {e}")
        sys.exit(1)


def criar_chat(cliente, modelo):
    """
    Cria uma sessão de chat com o modelo especificado.
    O chat mantém o histórico automaticamente para contexto.

    Args:
        cliente: cliente genai.Client
        modelo: nome do modelo (ex: gemini-2.5-flash)

    Returns:
        objeto chat para envio de mensagens
    """
    try:
        chat = cliente.chats.create(model=modelo)
        return chat
    except Exception as e:
        print(f"❌ Erro ao criar sessão de chat: {e}")
        print(f"   Modelo solicitado: {modelo}")
        print("   Verifique se o modelo está disponível no tier gratuito.")
        sys.exit(1)


def enviar_prompt(chat, prompt):
    """
    Envia o prompt para o Gemini via sessão de chat e retorna a resposta.

    Args:
        chat: sessão de chat ativa
        prompt: texto do prompt do usuário

    Returns:
        str: texto da resposta
    """
    try:
        resposta = chat.send_message(prompt)
        return resposta.text
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
    nome_arquivo = f"gemini_resposta_{timestamp}.txt"
    caminho = os.path.join(PASTA_SAIDA, nome_arquivo)

    # Escrever o conteúdo no arquivo
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"{'=' * 60}\n")
        f.write(f"  Data/Hora: {agora.strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"  Modelo: {GEMINI_MODEL}\n")
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
    print("  🤖  GEMINI PROMPT APP")
    print("  Envie prompts e receba respostas salvas em .txt")
    print("=" * 60)
    print()

    # Obter cliente configurado
    cliente = obter_cliente()
    print(f"📌 Modelo: {GEMINI_MODEL}")
    print(f"📂 Respostas serão salvas em: ./{PASTA_SAIDA}/")
    print(f"💡 Digite 'sair' para encerrar.\n")

    # Criar sessão de chat (mantém contexto entre mensagens)
    chat = criar_chat(cliente, GEMINI_MODEL)
    print("💬 Sessão de chat iniciada com sucesso!\n")

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

        print("\n⏳ Aguardando resposta do Gemini...")

        # Enviar prompt e obter resposta
        resposta = enviar_prompt(chat, prompt)

        # Exibir resposta no terminal
        print(f"\n🤖 RESPOSTA:\n{'-' * 40}")
        print(resposta)
        print(f"{'-' * 40}")

        # Salvar resposta em arquivo .txt
        caminho = salvar_resposta(prompt, resposta)
        print(f"\n💾 Resposta salva em: {caminho}")

        contador += 1
        print(f"📊 Total de perguntas nesta sessão: {contador}\n")

    print(f"\n📊 Sessão encerrada. {contador} pergunta(s) realizada(s).")
    if contador > 0:
        print(f"📂 Respostas salvas em: ./{PASTA_SAIDA}/")


if __name__ == "__main__":
    main()
