/*
 * bridge_core.h - parte da ORABRIDGE que nao depende do Oracle.
 *
 * Le a requisicao do Clipper (.REQ), converte binds e paginas de codigo e grava o
 * DBF (dBase III) do resultado. Fica separada de orabridge.c para poder ser
 * testada sem banco de dados (test_bridge.c).
 *
 * Todas as strings em memoria sao UTF-8 (e o que o ODPI-C usa); a pagina de codigo
 * do Clipper (cp850 etc.) so existe nas bordas: ao ler arquivos e ao gravar o DBF/.RSP.
 */
#ifndef BRIDGE_CORE_H
#define BRIDGE_CORE_H

#include <stddef.h>

/* Limites do formato DBF usado pelo Clipper 5.2 */
#define DBF_MAX_CHAR 254 /* tamanho maximo de um campo caractere */
#define DBF_MAX_NUM  19  /* largura maxima de um campo numerico (inclui sinal e ponto) */

/* ---------------------------------------------------------------- Utilitarios */

/* malloc/realloc que encerram o programa se faltar memoria */
void *br_alloc(size_t n);
void *br_realloc(void *p, size_t n);
char *br_strndup(const char *s, size_t n);
char *br_strdup(const char *s);

/* Le o arquivo inteiro (em um buffer com '\0' extra no fim). NULL se nao abrir. */
unsigned char *br_read_file(const char *path_utf8, size_t *len);

/* Grava o arquivo inteiro. Retorna 0 se deu certo. */
int br_write_file(const char *path_utf8, const void *data, size_t len);

/* ------------------------------------------------------- Paginas de codigo */

/* Nome ("cp850", "utf-8", "latin1"...) para numero da pagina do Windows; -1 se desconhecido. */
int br_codepage_id(const char *name);

/* Converte da pagina de codigo para UTF-8 (bytes invalidos viram U+FFFD). */
char *br_to_utf8(const char *s, size_t n, int cp, size_t *outlen);

/* Converte de UTF-8 para a pagina de codigo (sem equivalente vira '?'). */
char *br_from_utf8(const char *s, size_t n, int cp, size_t *outlen);

/* ---------------------------------------------------------------- Requisicao */

typedef struct {
    char type;   /* 'C', 'N', 'D', 'L' ou 'Z' (nulo) */
    char *value; /* valor ja sem escape */
} Bind;

typedef struct {
    char *action, *user, *pass, *dsn, *sqlfile, *rsp, *out;
    char *codepage; /* nome, minusculo (padrao "cp850") */
    int cp;         /* numero da pagina de codigo */
    char *maxrows;  /* texto; NULL, vazio ou 0 = sem limite */
    Bind *binds;
    size_t nbinds;
} Request;

/* Desfaz o escape do Clipper: \\ -> \, \r -> CR, \n -> LF (sequencia desconhecida fica como esta). */
char *br_unescape(const char *s);

/* Le o conteudo do .REQ. Retorna 0 se deu certo; senao msg recebe o motivo. */
int br_parse_request(const unsigned char *buf, size_t n, Request *req, char *msg, size_t msgsz);
void br_free_request(Request *req);

/* Separa "<tipo>|<valor>" (valor sem escape). */
void br_parse_bind(const char *item, Bind *b);

/* Remove o ';' final, que o Oracle rejeita fora de blocos PL/SQL (novo buffer). */
char *br_clean_sql(const char *sql);

/* ---------------------------------------------------------------------- DBF */

typedef enum { COL_N, COL_D, COL_L, COL_C } ColKind;

/*
 * Uma coluna do resultado. vals[i] e NULL para NULL; senao:
 *   COL_N  numero em texto decimal ("-10.5", ".5", "1.5E+3", ...)
 *   COL_D  "AAAAMMDD"
 *   COL_L  "T" ou "F"
 *   COL_C  texto UTF-8
 */
typedef struct {
    char *name; /* nome da coluna no Oracle (UTF-8) */
    ColKind kind;
    char **vals;
} Column;

/* Grava o DBF. Retorna 0 se deu certo; senao msg recebe o motivo. */
int br_write_dbf(const char *path, const Column *cols, size_t ncols, size_t nrows,
                 const char *codepage, int cp, char *msg, size_t msgsz);

/* Nome de campo DBF valido e unico (maiusculo, A-Z 0-9 _, ate 10 caracteres). */
char *br_field_name(const char *name, char used[][11], size_t *nused);

/* Numero do "language driver" do cabecalho do DBF para a pagina de codigo. */
int br_lang_driver(const char *codepage);

/* Texto mais curto que reproduz o double (ex.: 0.1 e nao 0.1000000000000000055). */
void br_double_text(double v, int is_float, char *out, size_t outsz);

/* ---------------------------------------------------------------------- .RSP */

/* Grava o .RSP: linhas separadas por CRLF, na pagina de codigo do Clipper. */
int br_write_response(const char *path, int cp, const char *const *lines, size_t nlines);

#endif
