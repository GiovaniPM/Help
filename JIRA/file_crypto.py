#!/usr/bin/env python3
"""
file_crypto.py
Criptografa e descriptografa arquivos usando AES (Fernet + PBKDF2).

Uso:
    python file_crypto.py encrypt <arquivo> --key <chave>
    python file_crypto.py decrypt <arquivo> --key <chave>
    python file_crypto.py genkey

Exemplos:
    python file_crypto.py encrypt relatorio.csv --key "MinhaSenhaForte@2026"
    python file_crypto.py decrypt relatorio.csv.enc --key "MinhaSenhaForte@2026"
    python file_crypto.py genkey
"""

import argparse
import base64
import hashlib
import os
import subprocess
import sys


# ──────────────────────────────────────────────
# Auto-instalação de dependências
# ──────────────────────────────────────────────
def ensure_dependency(package: str, import_name: str = None):
    """
    Verifica se o pacote está instalado.
    Se não estiver, instala automaticamente via pip.
    """
    import_name = import_name or package
    try:
        __import__(import_name)
    except ImportError:
        print(f"⚠️  Biblioteca '{package}' não encontrada. Instalando automaticamente...\n")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            print(f"  ✅ '{package}' instalada com sucesso!\n")
        except subprocess.CalledProcessError:
            print(f"❌ Erro: Não foi possível instalar '{package}'.")
            print(f"   Tente manualmente: pip install {package}")
            sys.exit(1)


# Garante que a biblioteca esteja disponível antes de importar
ensure_dependency("cryptography")

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ──────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────
SALT_SIZE = 16          # 16 bytes de salt
ITERATIONS = 480_000    # Iterações PBKDF2
ENC_EXTENSION = ".enc"


# ──────────────────────────────────────────────
# Funções de derivação de chave
# ──────────────────────────────────────────────
def derive_key(password: str, salt: bytes) -> bytes:
    """
    Deriva uma chave Fernet (AES-128-CBC) a partir de uma senha
    usando PBKDF2-HMAC-SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
    return key


# ──────────────────────────────────────────────
# Criptografar
# ──────────────────────────────────────────────
def encrypt_file(filepath: str, password: str) -> str:
    """
    Criptografa o arquivo e salva com extensão .enc.
    O salt é armazenado nos primeiros 16 bytes do arquivo criptografado.
    """
    if not os.path.isfile(filepath):
        print(f"❌ Erro: Arquivo '{filepath}' não encontrado.")
        sys.exit(1)

    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    fernet = Fernet(key)

    with open(filepath, "rb") as f:
        original_data = f.read()

    encrypted_data = fernet.encrypt(original_data)

    output_path = filepath + ENC_EXTENSION
    with open(output_path, "wb") as f:
        f.write(salt + encrypted_data)

    return output_path


# ──────────────────────────────────────────────
# Descriptografar
# ──────────────────────────────────────────────
def decrypt_file(filepath: str, password: str) -> str:
    """
    Descriptografa um arquivo .enc e restaura o arquivo original.
    """
    if not os.path.isfile(filepath):
        print(f"❌ Erro: Arquivo '{filepath}' não encontrado.")
        sys.exit(1)

    with open(filepath, "rb") as f:
        file_data = f.read()

    if len(file_data) < SALT_SIZE:
        print("❌ Erro: Arquivo criptografado inválido ou corrompido.")
        sys.exit(1)

    salt = file_data[:SALT_SIZE]
    encrypted_data = file_data[SALT_SIZE:]

    key = derive_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except InvalidToken:
        print("❌ Erro: Chave incorreta ou arquivo corrompido.")
        sys.exit(1)

    if filepath.endswith(ENC_EXTENSION):
        output_path = filepath[: -len(ENC_EXTENSION)]
    else:
        output_path = filepath + ".dec"

    if os.path.exists(output_path):
        output_path = _safe_output_name(output_path)

    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    return output_path


# ──────────────────────────────────────────────
# Gerar chave aleatória
# ──────────────────────────────────────────────
def generate_random_key() -> str:
    """Gera uma chave aleatória segura (base64, 32 bytes)."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")


# ──────────────────────────────────────────────
# Utilitários
# ──────────────────────────────────────────────
def _safe_output_name(path: str) -> str:
    """Adiciona sufixo numérico para não sobrescrever arquivo existente."""
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = f"{base}_decrypted{ext}"
    while os.path.exists(new_path):
        new_path = f"{base}_decrypted({counter}){ext}"
        counter += 1
    return new_path


def _file_hash(filepath: str) -> str:
    """Calcula SHA-256 do arquivo para verificação de integridade."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="🔐 File Crypto — Criptografa e descriptografa arquivos com AES (Fernet + PBKDF2).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  Criptografar:
    python file_crypto.py encrypt relatorio.csv --key "MinhaSenha@2026"

  Descriptografar:
    python file_crypto.py decrypt relatorio.csv.enc --key "MinhaSenha@2026"

  Gerar chave aleatória:
    python file_crypto.py genkey
        """,
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comando a executar.")

    # ── Subcomando: encrypt ──
    enc_parser = subparsers.add_parser("encrypt", help="Criptografa um arquivo.")
    enc_parser.add_argument("arquivo", help="Caminho do arquivo a criptografar.")
    enc_parser.add_argument(
        "-k", "--key", required=True, help="Chave (senha) de criptografia.",
    )

    # ── Subcomando: decrypt ──
    dec_parser = subparsers.add_parser("decrypt", help="Descriptografa um arquivo .enc.")
    dec_parser.add_argument("arquivo", help="Caminho do arquivo a descriptografar.")
    dec_parser.add_argument(
        "-k", "--key", required=True, help="Chave (senha) usada na criptografia.",
    )

    # ── Subcomando: genkey ──
    subparsers.add_parser("genkey", help="Gera uma chave aleatória segura.")

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        sys.exit(0)

    # ── Gerar chave ──
    if args.comando == "genkey":
        key = generate_random_key()
        print(f"\n🔑 Chave gerada com sucesso:\n")
        print(f"   {key}\n")
        print("   ⚠️  Guarde esta chave em local seguro!\n")
        return

    # ── Criptografar ──
    if args.comando == "encrypt":
        file_size = os.path.getsize(args.arquivo)
        print(f"\n🔒 Criptografando '{args.arquivo}' ({file_size:,} bytes)...\n")

        original_hash = _file_hash(args.arquivo)
        output = encrypt_file(args.arquivo, args.key)
        enc_size = os.path.getsize(output)

        print(f"  ✅ Arquivo criptografado: {output} ({enc_size:,} bytes)")
        print(f"  🔍 SHA-256 original:      {original_hash}")
        print(f"\n  ⚠️  Guarde a chave em local seguro!\n")

    # ── Descriptografar ──
    elif args.comando == "decrypt":
        file_size = os.path.getsize(args.arquivo)
        print(f"\n🔓 Descriptografando '{args.arquivo}' ({file_size:,} bytes)...\n")

        output = decrypt_file(args.arquivo, args.key)
        dec_size = os.path.getsize(output)
        restored_hash = _file_hash(output)

        print(f"  ✅ Arquivo restaurado:  {output} ({dec_size:,} bytes)")
        print(f"  🔍 SHA-256 restaurado:  {restored_hash}")
        print(f"\n  ✅ Descriptografia concluída com sucesso!\n")


if __name__ == "__main__":
    main()