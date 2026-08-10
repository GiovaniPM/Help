#!/usr/bin/env python3
import argparse
import os
import sys

# 🔹 Opcional: usar chardet se disponível (mais preciso)
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


def detect_encoding(file_path):
    """
    Detecta encoding automaticamente.
    """
    if HAS_CHARDET:
        print("[INFO] Detectando encoding com chardet...")
        with open(file_path, "rb") as f:
            rawdata = f.read(100000)  # lê 100KB
            result = chardet.detect(rawdata)
            encoding = result["encoding"]
            confidence = result["confidence"]

            print(f"[INFO] Encoding detectado: {encoding} (confiança: {confidence:.2f})")

            if encoding:
                return encoding

    # 🔹 fallback manual
    print("[WARN] chardet não disponível ou falhou. Usando fallback...")
    return try_common_encodings(file_path)


def try_common_encodings(file_path):
    """
    Tenta encodings comuns.
    """
    encodings = ["utf-8", "cp1252", "latin-1"]

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                f.readline()
            print(f"[INFO] Encoding válido encontrado: {enc}")
            return enc
        except UnicodeDecodeError:
            print(f"[WARN] Falha com encoding {enc}")

    raise Exception("Não foi possível identificar o encoding do arquivo.")


def split_file(input_file, lines_per_file, output_prefix=None, encoding=None):
    """
    Divide arquivo preservando performance e encoding.
    """
    if not os.path.exists(input_file):
        print(f"[ERRO] Arquivo não encontrado: {input_file}")
        sys.exit(1)

    if output_prefix is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_prefix = base_name + "_part_"

    # 🔥 Detecta encoding automaticamente
    if encoding is None:
        encoding = detect_encoding(input_file)

    print(f"[INFO] Usando encoding: {encoding}")
    print(f"[INFO] Linhas por arquivo: {lines_per_file}")
    print(f"[INFO] Prefixo: {output_prefix}")

    file_count = 1
    line_count = 0
    outfile = None

    try:
        with open(input_file, "r", encoding=encoding, errors="replace") as infile:

            for line in infile:
                if line_count % lines_per_file == 0:
                    if outfile:
                        outfile.close()

                    output_filename = f"{output_prefix}{file_count}.txt"
                    outfile = open(output_filename, "w", encoding=encoding)
                    print(f"[INFO] Criando: {output_filename}")

                    file_count += 1

                outfile.write(line)
                line_count += 1

            if outfile:
                outfile.close()

        print(f"[SUCESSO] Total de linhas: {line_count}")
        print(f"[SUCESSO] Arquivos gerados: {file_count - 1}")

    except Exception as e:
        print(f"[ERRO] Falha durante execução: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Split de arquivo TXT por número de linhas com detecção automática de encoding"
    )

    parser.add_argument("arquivo", help="Arquivo de entrada")
    parser.add_argument("linhas", type=int, help="Linhas por arquivo")

    parser.add_argument(
        "--prefixo",
        help="Prefixo dos arquivos de saída"
    )

    parser.add_argument(
        "--encoding",
        help="Forçar encoding (opcional)"
    )

    args = parser.parse_args()

    if args.linhas <= 0:
        print("[ERRO] Linhas deve ser > 0")
        sys.exit(1)

    split_file(
        input_file=args.arquivo,
        lines_per_file=args.linhas,
        output_prefix=args.prefixo,
        encoding=args.encoding
    )


if __name__ == "__main__":
    main()