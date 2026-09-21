#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Prompt App
Solicita prompts ao usuário, envia para a API do Google Gemini (com contexto
de chat) e salva cada resposta em um arquivo .txt.

USO:
  1. Obtenha uma API Key em https://aistudio.google.com ("Get API Key").
  2. pip install google-genai
  3. Defina a variável de ambiente (NUNCA grave a chave no código):
       CMD:         set GEMINI_API_KEY=sua-chave
       PowerShell:  $env:GEMINI_API_KEY = "sua-chave"
       Linux/macOS: export GEMINI_API_KEY="sua-chave"
  4. python gemini_prompt.py   (digite "sair" para encerrar)

Variáveis opcionais: GEMINI_MODEL (padrão gemini-2.5-flash), GEMINI_OUTPUT_DIR.
"""

import datetime
import os
import subprocess
import sys
from pathlib import Path

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODELO = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PASTA_SAIDA = Path(os.getenv("GEMINI_OUTPUT_DIR") or Path(__file__).resolve().parent / "respostas_gemini")
COMANDOS_SAIR = {"sair", "exit", "quit", "q"}

LINHA = "=" * 60
SEP = "-" * 40

AJUDA_CONFIG = f"""{LINHA}
⚠️  CONFIGURAÇÃO NECESSÁRIA
{LINHA}

Nenhuma API Key do Gemini foi configurada.

  1. Obtenha sua chave em https://aistudio.google.com ("Get API Key")
  2. Defina a variável de ambiente GEMINI_API_KEY:
       CMD:         set GEMINI_API_KEY=sua-chave
       PowerShell:  $env:GEMINI_API_KEY = "sua-chave"
       Linux/macOS: export GEMINI_API_KEY="sua-chave"
{LINHA}"""


def abortar(msg):
    print(msg)
    sys.exit(1)


def importar_genai():
    """Importa google-genai, instalando-o se necessário."""
    try:
        from google import genai
        return genai
    except ImportError:
        print("📦 Instalando 'google-genai'...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "google-genai"]
            )
        except (subprocess.CalledProcessError, OSError) as e:
            abortar(f"❌ Falha na instalação ({e}). Execute: pip install google-genai")
        from google import genai
        return genai


def criar_chat():
    """Cria o cliente e uma sessão de chat (o histórico é mantido pelo SDK)."""
    if not API_KEY:
        abortar(AJUDA_CONFIG)
    genai = importar_genai()
    try:
        chat = genai.Client(api_key=API_KEY).chats.create(model=MODELO)
    except Exception as e:
        abortar(f"❌ Erro ao criar sessão de chat (modelo: {MODELO}): {e}")
    print("🔗 Conectado à API do Google Gemini.")
    return chat


def enviar_prompt(chat, prompt):
    """Envia o prompt e retorna (texto, sucesso)."""
    try:
        return chat.send_message(prompt).text or "(resposta vazia)", True
    except Exception as e:
        return f"❌ Erro ao obter resposta da API: {e}", False


def salvar_resposta(prompt, resposta):
    """Salva prompt e resposta em um .txt com timestamp único e retorna o caminho."""
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    agora = datetime.datetime.now()
    base = f"gemini_resposta_{agora:%Y%m%d_%H%M%S}"
    caminho = PASTA_SAIDA / f"{base}.txt"
    n = 1
    while caminho.exists():  # evita sobrescrever respostas no mesmo segundo
        caminho = PASTA_SAIDA / f"{base}_{n}.txt"
        n += 1

    caminho.write_text(
        f"{LINHA}\n"
        f"  Data/Hora: {agora:%d/%m/%Y %H:%M:%S}\n"
        f"  Modelo: {MODELO}\n"
        f"{LINHA}\n\n"
        f"📝 PROMPT:\n{SEP}\n{prompt}\n\n"
        f"🤖 RESPOSTA:\n{SEP}\n{resposta}\n",
        encoding="utf-8",
    )
    return caminho


def ler_prompt():
    """Lê o prompt; retorna None ao receber EOF/Ctrl+C."""
    try:
        return input("📝 Digite seu prompt:\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def main():
    print(f"\n{LINHA}\n  🤖  GEMINI PROMPT APP\n{LINHA}\n")
    chat = criar_chat()
    print(f"📌 Modelo: {MODELO}")
    print(f"📂 Respostas em: {PASTA_SAIDA}")
    print("💡 Digite 'sair' para encerrar.\n")

    contador = 0
    while True:
        print("-" * 60)
        prompt = ler_prompt()
        if prompt is None or prompt.lower() in COMANDOS_SAIR:
            print("\n👋 Encerrando. Até a próxima!")
            break
        if not prompt:
            print("⚠️  Prompt vazio. Tente novamente.\n")
            continue

        print("\n⏳ Aguardando resposta do Gemini...")
        resposta, ok = enviar_prompt(chat, prompt)
        print(f"\n🤖 RESPOSTA:\n{SEP}\n{resposta}\n{SEP}")

        if ok:  # não grava mensagens de erro como se fossem respostas
            print(f"\n💾 Resposta salva em: {salvar_resposta(prompt, resposta)}")
            contador += 1
            print(f"📊 Total de perguntas nesta sessão: {contador}\n")

    print(f"\n📊 Sessão encerrada. {contador} pergunta(s) realizada(s).")


if __name__ == "__main__":
    main()
