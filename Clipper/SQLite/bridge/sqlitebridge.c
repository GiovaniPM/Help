/*
 * sqlitebridge.c - ponte entre a biblioteca SQLITE.LIB (Clipper 5.2) e um banco SQLite.
 *
 * Uso:  SQLITEBRIDGE <arquivo.REQ>
 *
 * O Clipper grava um arquivo de requisicao (KEY=VALUE, uma por linha), roda este
 * programa com RUN e le o arquivo de resposta indicado em RSP=.
 *
 * Requisicao:
 *     ACTION=PING | QUERY | EXEC
 *     FILE=                    caminho do arquivo .db (criado se nao existir)
 *     SQLFILE=                 arquivo com o comando SQL
 *     RSP=                     arquivo de resposta
 *     OUT=                     (QUERY) DBF a ser gerado
 *     CODEPAGE=                pagina de codigo do Clipper (padrao cp850)
 *     MAXROWS=                 limite de linhas do QUERY (0 = sem limite)
 *     BIND=<tipo>|<valor>      binds posicionais (:1, :2 ...); tipo C, N, D, L ou Z (nulo)
 *
 * Resposta:
 *     OK / <linhas afetadas ou retornadas> / <1 se truncou no MAXROWS, senao 0>
 *     ERR / <mensagem>
 *
 * Valores dos binds escapam \ como \\, CR como \r e LF como \n.
 *
 * Acesso ao SQLite: biblioteca embutida (amalgamation), sem servidor nem cliente
 * externo — o executavel ja contem tudo que precisa para abrir o arquivo .db.
 *
 * Datas: o campo D do Clipper vira o texto ISO-8601 "AAAA-MM-DD" (convencao do
 * proprio SQLite, entendida por date()/strftime()) ou, se a coluna guardar segundos
 * desde 1970 (epoch Unix), um INTEGER. Colunas DATE gravadas como numero juliano
 * (REAL) nao sao convertidas.
 */
#include "bridge_core.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "sqlite3.h"

#define LOB_CHARS DBF_MAX_CHAR /* so o inicio de um BLOB/TEXT longo cabe no campo caractere */

static char g_err[2048]; /* mensagem do ultimo erro */

/* ------------------------------------------------------------------- Erros */

static int fail(const char *fmt, const char *arg)
{
    snprintf(g_err, sizeof g_err, fmt, arg ? arg : "");
    return -1;
}

/* Guarda a mensagem de erro do SQLite em g_err e devolve -1. */
static int fail_db(sqlite3 *db)
{
    return fail("%s", sqlite3_errmsg(db));
}

/* ------------------------------------------------------------------- Binds */

/* "digitos[.digitos][E[+-]n]" com sinal opcional (o Clipper manda Str() com 10 decimais). */
static int valid_number(const char *s)
{
    int digits = 0;
    if (*s == '+' || *s == '-')
        s++;
    while (isdigit((unsigned char)*s)) { s++; digits++; }
    if (*s == '.') {
        s++;
        while (isdigit((unsigned char)*s)) { s++; digits++; }
    }
    if (!digits)
        return 0;
    if (*s == 'e' || *s == 'E') {
        s++;
        if (*s == '+' || *s == '-')
            s++;
        if (!isdigit((unsigned char)*s))
            return 0;
        while (isdigit((unsigned char)*s))
            s++;
    }
    return *s == '\0';
}

/* .5, 10.50000, -3.0 ... : sem exponte e sem parte fracionaria significativa vira INTEGER. */
static int number_is_integer(const char *s)
{
    const char *dot = strchr(s, '.');
    if (strchr(s, 'e') || strchr(s, 'E'))
        return 0;
    if (!dot)
        return 1;
    for (dot++; *dot; dot++)
        if (*dot != '0')
            return 0;
    return 1;
}

/* Bind na posicao pos (1, 2, ...) do comando preparado. */
static int bind_one(sqlite3_stmt *stmt, int pos, const Bind *b)
{
    char *v = br_strdup(b->value), *t = v;
    size_t len;
    int rc = SQLITE_OK;

    while (isspace((unsigned char)*t))
        t++;
    len = strlen(t);
    while (len && isspace((unsigned char)t[len - 1]))
        t[--len] = '\0';

    switch (b->type) {
    case 'N':
        if (!valid_number(t)) {
            fail("valor numerico invalido no bind: %s", t);
            free(v);
            return -1;
        }
        rc = number_is_integer(t) ? sqlite3_bind_int64(stmt, pos, strtoll(t, NULL, 10))
                                   : sqlite3_bind_double(stmt, pos, strtod(t, NULL));
        break;
    case 'D':
        if (len == 0) {
            rc = sqlite3_bind_null(stmt, pos);
        } else {
            int y, m, d;
            char iso[11];
            if (len < 8 || sscanf(t, "%4d%2d%2d", &y, &m, &d) != 3) {
                fail("data invalida no bind: %s", t);
                free(v);
                return -1;
            }
            /* "AAAA-MM-DD": formato de data recomendado pelo proprio SQLite */
            snprintf(iso, sizeof iso, "%04d-%02d-%02d", y, m, d);
            rc = sqlite3_bind_text(stmt, pos, iso, -1, SQLITE_TRANSIENT);
        }
        break;
    case 'L':
        /* o SQLite nao tem tipo booleano: vai como 1/0 */
        rc = sqlite3_bind_int(stmt, pos, (len && strchr("TYS1tys", t[0])) ? 1 : 0);
        break;
    case 'Z':
        rc = sqlite3_bind_null(stmt, pos);
        break;
    default: /* 'C': texto, sem cortar espacos */
        rc = sqlite3_bind_text(stmt, pos, b->value, (int)strlen(b->value), SQLITE_TRANSIENT);
        break;
    }
    free(v);
    if (rc != SQLITE_OK) {
        fail("%s", sqlite3_errstr(rc));
        return -1;
    }
    return 0;
}

/* ------------------------------------------------------------------ Consulta */

/* -1 = ainda nao decidido (coluna sem tipo declarado, so souberemos ao ver um valor). */
typedef struct {
    char *name;
    ColKind kind;
} QCol;

static void hex_encode(const unsigned char *p, size_t n, char *out)
{
    static const char hex[] = "0123456789ABCDEF";
    size_t i;
    for (i = 0; i < n; i++) {
        out[2 * i] = hex[p[i] >> 4];
        out[2 * i + 1] = hex[p[i] & 15];
    }
    out[2 * n] = '\0';
}

/* Kind sugerido pelo tipo declarado da coluna (CREATE TABLE ... coluna TIPO); NULL numa
 * expressao (COUNT(*), literais...), que so sera decidido ao ver o primeiro valor. */
static ColKind decltype_kind(const char *decl)
{
    char up[64];
    size_t i;
    if (!decl)
        return (ColKind)-1;
    for (i = 0; decl[i] && i < sizeof up - 1; i++)
        up[i] = (char)toupper((unsigned char)decl[i]);
    up[i] = '\0';
    if (strstr(up, "INT"))
        return COL_N;
    if (strstr(up, "BOOL"))
        return COL_L;
    if (strstr(up, "DATE") || strstr(up, "TIME"))
        return COL_D;
    if (strstr(up, "REAL") || strstr(up, "FLOA") || strstr(up, "DOUB") || strstr(up, "NUM") ||
        strstr(up, "DEC"))
        return COL_N;
    return COL_C; /* CHAR, VARCHAR, TEXT, CLOB, BLOB (o BLOB vira hexadecimal, campo C) */
}

/* "AAAA-MM-DD..." -> "AAAAMMDD"; segundos desde 1970 (INTEGER) -> "AAAAMMDD". */
static char *sqlite_cell_date(sqlite3_stmt *stmt, int c)
{
    char buf[32];
    if (sqlite3_column_type(stmt, c) == SQLITE_INTEGER) {
        time_t t = (time_t)sqlite3_column_int64(stmt, c);
        struct tm *g = gmtime(&t);
        int year;
        if (!g)
            return NULL;
        year = g->tm_year + 1900;
        if (year < 0 || year > 9999) /* fora do intervalo do campo D do Clipper */
            return NULL;
        snprintf(buf, sizeof buf, "%04d%02d%02d", year, g->tm_mon + 1, g->tm_mday);
        return br_strdup(buf);
    }
    {
        const unsigned char *txt = sqlite3_column_text(stmt, c);
        int n = sqlite3_column_bytes(stmt, c), k = 0;
        if (!txt)
            return NULL;
        for (; n > 0 && k < 8; txt++, n--)
            if (isdigit(*txt))
                buf[k++] = (char)*txt;
        if (k < 8) /* numero juliano (REAL) ou texto num formato desconhecido: nao convertido */
            return NULL;
        buf[8] = '\0';
        return br_strdup(buf);
    }
}

/* Texto do valor da coluna c da linha atual (malloc), ou NULL para NULL do banco. */
static char *sqlite_cell_text(sqlite3_stmt *stmt, int c, ColKind kind)
{
    char buf[64];
    if (sqlite3_column_type(stmt, c) == SQLITE_NULL)
        return NULL;
    if (kind == COL_D)
        return sqlite_cell_date(stmt, c);
    if (kind == COL_L)
        return br_strdup(sqlite3_column_int64(stmt, c) ? "T" : "F");
    /* segue o tipo real do valor (o SQLite tem tipagem dinamica por celula) e nao o
     * declarado na coluna, para nunca perder um valor por causa de um "kind" errado */
    switch (sqlite3_column_type(stmt, c)) {
    case SQLITE_INTEGER:
        snprintf(buf, sizeof buf, "%lld", (long long)sqlite3_column_int64(stmt, c));
        return br_strdup(buf);
    case SQLITE_FLOAT:
        br_double_text(sqlite3_column_double(stmt, c), 0, buf, sizeof buf);
        return br_strdup(buf);
    case SQLITE_BLOB: {
        int n = sqlite3_column_bytes(stmt, c);
        const void *raw = sqlite3_column_blob(stmt, c);
        int use = n < LOB_CHARS / 2 ? n : LOB_CHARS / 2; /* hexadecimal dobra de tamanho */
        char *hex = br_alloc((size_t)use * 2 + 1);
        hex_encode((const unsigned char *)raw, (size_t)use, hex);
        return hex;
    }
    default: { /* SQLITE_TEXT */
        const unsigned char *txt = sqlite3_column_text(stmt, c);
        int n = sqlite3_column_bytes(stmt, c);
        return br_strndup((const char *)txt, (size_t)(n < 0 ? 0 : n));
    }
    }
}

/* Executa o SELECT e grava o DBF. Devolve 0 se deu certo. */
static int do_query(sqlite3 *db, sqlite3_stmt *stmt, const Request *req, long *count, int *truncated)
{
    int ncols = sqlite3_column_count(stmt), c, step;
    QCol *cols;
    Column *plain;
    size_t nrows = 0, cap = 0, r;
    long limit = 0;
    int rc = -1;
    char msg[512];

    if (ncols == 0)
        return fail("%s", "o comando SQL nao retorna colunas (use SQLITE EXEC)");
    if (req->maxrows)
        limit = atol(req->maxrows);
    if (limit < 0)
        limit = 0;

    /* "cols" guarda o tipo (kind) de cada coluna; "plain" (mesmo nome, tamanho fixo em
     * ncols) e o vetor que vai para br_write_dbf, so os vals[] crescem durante o fetch */
    cols = br_alloc((size_t)ncols * sizeof(QCol));
    plain = br_alloc((size_t)ncols * sizeof(Column));
    for (c = 0; c < ncols; c++) {
        cols[c].name = br_strdup(sqlite3_column_name(stmt, c));
        cols[c].kind = decltype_kind(sqlite3_column_decltype(stmt, c));
        plain[c].name = cols[c].name;
        plain[c].vals = NULL;
    }

    for (;;) {
        step = sqlite3_step(stmt);
        if (step == SQLITE_DONE)
            break;
        if (step != SQLITE_ROW) {
            fail_db(db);
            goto done;
        }
        if (limit && (long)nrows == limit) {
            *truncated = 1;
            break;
        }
        if (nrows == cap) {
            cap = cap ? cap * 2 : 1024;
            for (c = 0; c < ncols; c++)
                plain[c].vals = br_realloc(plain[c].vals, cap * sizeof(char *));
        }
        for (c = 0; c < ncols; c++) {
            /* coluna de expressao (kind ainda nao decidido): usa o tipo do primeiro valor nao-nulo */
            if ((int)cols[c].kind == -1 && sqlite3_column_type(stmt, c) != SQLITE_NULL)
                cols[c].kind = sqlite3_column_type(stmt, c) == SQLITE_TEXT ? COL_C : COL_N;
            plain[c].kind = (int)cols[c].kind == -1 ? COL_C : cols[c].kind;
            plain[c].vals[nrows] = sqlite_cell_text(stmt, c, plain[c].kind);
        }
        nrows++;
    }

    rc = br_write_dbf(req->out, plain, (size_t)ncols, nrows, req->codepage, req->cp, msg, sizeof msg);
    if (rc != 0)
        fail("%s", msg);
    *count = (long)nrows;
done:
    for (c = 0; c < ncols; c++) {
        for (r = 0; r < nrows; r++)
            free(plain[c].vals[r]);
        free(plain[c].vals);
        free(cols[c].name);
    }
    free(plain);
    free(cols);
    return rc;
}

/* --------------------------------------------------------------------- Acoes */

static int ci_eq(const char *a, const char *b)
{
    for (; *a && *b; a++, b++)
        if (toupper((unsigned char)*a) != toupper((unsigned char)*b))
            return 0;
    return *a == *b;
}

static char *read_sql(const Request *req)
{
    size_t n, ntext;
    unsigned char *raw, *p;
    char *text, *sql;
    size_t i, k = 0;

    if (!req->sqlfile) {
        fail("campo ausente: %s", "SQLFILE");
        return NULL;
    }
    raw = br_read_file(req->sqlfile, &n);
    if (!raw) {
        fail("nao foi possivel ler %s", req->sqlfile);
        return NULL;
    }
    /* arquivo texto do Clipper (pagina de codigo DOS), sem o Ctrl-Z final */
    p = raw;
    for (i = 0; i < n; i++)
        if (raw[i] != 0x1A)
            p[k++] = raw[i];
    text = br_to_utf8((char *)p, k, req->cp, &ntext);
    free(raw);
    sql = br_clean_sql(text);
    free(text);
    return sql;
}

static int run(const Request *req, long *count, int *truncated)
{
    sqlite3 *db = NULL;
    sqlite3_stmt *stmt = NULL;
    char *sql = NULL;
    const char *action = req->action ? req->action : "";
    int rc = -1, is_ping, ncols;
    size_t i;

    *count = 0;
    *truncated = 0;

    if (!req->file) return fail("campo ausente: %s", "FILE");

    is_ping = ci_eq(action, "PING");
    if (!is_ping && !ci_eq(action, "QUERY") && !ci_eq(action, "EXEC"))
        return fail("ACTION invalida: '%s'", action);
    if (!is_ping) {
        if (ci_eq(action, "QUERY") && !req->out)
            return fail("campo ausente: %s", "OUT");
        sql = read_sql(req);
        if (!sql)
            return -1;
    } else {
        sql = br_strdup("select 1"); /* so verifica se o arquivo abre e a consulta funciona */
    }

    /* cria o arquivo se nao existir, como o SQLite sempre fez */
    if (sqlite3_open_v2(req->file, &db, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE, NULL) != SQLITE_OK) {
        fail_db(db);
        goto done;
    }
    sqlite3_busy_timeout(db, 5000);
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        fail_db(db);
        goto done;
    }
    for (i = 0; !is_ping && i < req->nbinds; i++)
        if (bind_one(stmt, (int)(i + 1), &req->binds[i]) < 0)
            goto done;

    if (is_ping) {
        int step = sqlite3_step(stmt);
        if (step != SQLITE_ROW && step != SQLITE_DONE)
            fail_db(db);
        else
            rc = 0;
    } else if (ci_eq(action, "EXEC")) {
        ncols = sqlite3_column_count(stmt);
        if (ncols != 0) {
            fail("%s", "o comando SQL retorna colunas (use SQLITE USE)");
        } else if (sqlite3_step(stmt) != SQLITE_DONE) {
            fail_db(db);
        } else {
            *count = sqlite3_changes(db);
            rc = 0;
        }
    } else {
        rc = do_query(db, stmt, req, count, truncated);
    }
done:
    if (stmt)
        sqlite3_finalize(stmt);
    if (db)
        sqlite3_close(db);
    free(sql);
    return rc;
}

/* --------------------------------------------------------------------- main */

/* Uma linha so, sem espacos repetidos: o .RSP e lido linha a linha pelo Clipper. */
static void one_line(char *s)
{
    char *start = s, *o = s;
    int pending_space = 0;
    for (; *s; s++) {
        if (isspace((unsigned char)*s)) {
            pending_space = 1;
            continue;
        }
        if (pending_space && o != start)
            *o++ = ' ';
        pending_space = 0;
        *o++ = *s;
    }
    *o = '\0';
}

int main(int argc, char **argv)
{
    Request req;
    unsigned char *buf;
    size_t n;
    char msg[256], count_text[32];
    const char *lines[3];
    long count = 0;
    int truncated = 0;

    msg[0] = '\0';
    if (argc != 2) {
        fputs("Uso: SQLITEBRIDGE <arquivo.REQ>\n", stderr);
        return 2;
    }
    buf = br_read_file(argv[1], &n);
    if (!buf) {
        fprintf(stderr, "requisicao invalida: nao foi possivel ler %s\n", argv[1]);
        return 2;
    }
    /* sem RSP nao ha como responder ao Clipper */
    if (br_parse_request(buf, n, &req, msg, sizeof msg) != 0 || !req.rsp) {
        fprintf(stderr, "requisicao invalida: %s\n", req.rsp || msg[0] ? msg : "campo ausente: RSP");
        return 2;
    }
    free(buf);

    g_err[0] = '\0';
    if (run(&req, &count, &truncated) == 0) {
        snprintf(count_text, sizeof count_text, "%ld", count);
        lines[0] = "OK";
        lines[1] = count_text;
        lines[2] = truncated ? "1" : "0";
        br_write_response(req.rsp, req.cp, lines, 3);
    } else {
        /* qualquer falha (arquivo, SQL, DBF...) vira "ERR" + mensagem numa linha so; o RUN do
         * Clipper nao recebe codigo de saida, entao o erro vai pelo .RSP */
        one_line(g_err);
        lines[0] = "ERR";
        lines[1] = g_err[0] ? g_err : "erro desconhecido";
        br_write_response(req.rsp, req.cp, lines, 2);
    }
    br_free_request(&req);
    return 0;
}
