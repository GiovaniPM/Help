/*
 * orabridge.c - ponte entre a biblioteca ORACLE.LIB (Clipper 5.2) e o banco Oracle.
 *
 * Uso:  ORABRIDGE <arquivo.REQ>
 *
 * O Clipper grava um arquivo de requisicao (KEY=VALUE, uma por linha), roda este
 * programa com RUN e le o arquivo de resposta indicado em RSP=.
 *
 * Requisicao:
 *     ACTION=PING | QUERY | EXEC
 *     USER=, PASS=, DSN=      DSN pode ser "host:porta/servico" ou um descritor completo
 *     SQLFILE=                arquivo com o comando SQL
 *     RSP=                    arquivo de resposta
 *     OUT=                    (QUERY) DBF a ser gerado
 *     CODEPAGE=               pagina de codigo do Clipper (padrao cp850)
 *     MAXROWS=                limite de linhas do QUERY (0 = sem limite)
 *     BIND=<tipo>|<valor>     binds posicionais (:1, :2 ...); tipo C, N, D, L ou Z (nulo)
 *
 * Resposta:
 *     OK / <linhas afetadas ou retornadas> / <1 se truncou no MAXROWS, senao 0>
 *     ERR / <mensagem>
 *
 * Valores dos binds escapam \ como \\, CR como \r e LF como \n.
 *
 * Acesso ao Oracle: ODPI-C, que carrega o Oracle Client (Instant Client) em tempo de
 * execucao; ele precisa estar no PATH (ou na pasta do programa) com a mesma
 * arquitetura (32/64 bits) deste executavel.
 */
#include "bridge_core.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dpi.h"

#define FETCH_ROWS 500 /* linhas trazidas por viagem de rede */
#define LOB_CHARS  DBF_MAX_CHAR /* so o inicio de um CLOB cabe no campo caractere */

static char g_err[2048]; /* mensagem do ultimo erro */

/* ------------------------------------------------------------------- Erros */

static void copy_err(const dpiErrorInfo *info)
{
    size_t n = info->messageLength;
    if (n >= sizeof g_err)
        n = sizeof g_err - 1;
    memcpy(g_err, info->message, n);
    g_err[n] = '\0';
}

/* Guarda a mensagem do ODPI-C em g_err e devolve -1. */
static int fail_dpi(dpiContext *ctx)
{
    dpiErrorInfo info;
    dpiContext_getError(ctx, &info);
    copy_err(&info);
    return -1;
}

static int fail(const char *fmt, const char *arg)
{
    snprintf(g_err, sizeof g_err, fmt, arg ? arg : "");
    return -1;
}

/* ------------------------------------------------------------------ Estado */

typedef struct {
    dpiContext *ctx;
    dpiConn *conn;
    dpiStmt *stmt;
    dpiVar **binds; /* variaveis dos binds (mantidas ate fechar o comando) */
    size_t nbinds;
} Session;

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

/* Cria a variavel do bind na posicao pos (1, 2, ...) e associa ao comando. */
static int bind_one(Session *s, uint32_t pos, const Bind *b)
{
    dpiVar *var = NULL;
    dpiData *data;
    char *v = br_strdup(b->value), *t = v;
    size_t len;
    int rc = -1;

    while (isspace((unsigned char)*t))
        t++;
    len = strlen(t);
    while (len && isspace((unsigned char)t[len - 1]))
        t[--len] = '\0';

    switch (b->type) {
    case 'N':
        /* o texto e convertido pelo ODPI-C, sem depender do NLS (separador decimal) do banco */
        if (!valid_number(t)) {
            fail("valor numerico invalido no bind: %s", t);
            goto done;
        }
        if (dpiConn_newVar(s->conn, DPI_ORACLE_TYPE_NUMBER, DPI_NATIVE_TYPE_BYTES, 1, (uint32_t)len,
                           1, 0, NULL, &var, &data) < 0 ||
            dpiVar_setFromBytes(var, 0, t, (uint32_t)len) < 0) {
            fail_dpi(s->ctx);
            goto done;
        }
        break;
    case 'D':
        if (len == 0) {
            /* data vazia do Clipper (CTOD("")) equivale a NULL */
            if (dpiConn_newVar(s->conn, DPI_ORACLE_TYPE_DATE, DPI_NATIVE_TYPE_TIMESTAMP, 1, 0, 0, 0,
                               NULL, &var, &data) < 0) {
                fail_dpi(s->ctx);
                goto done;
            }
            dpiData_setNull(data);
        } else {
            int y, m, d;
            if (len < 8 || sscanf(t, "%4d%2d%2d", &y, &m, &d) != 3) {
                fail("data invalida no bind: %s", t);
                goto done;
            }
            if (dpiConn_newVar(s->conn, DPI_ORACLE_TYPE_DATE, DPI_NATIVE_TYPE_TIMESTAMP, 1, 0, 0, 0,
                               NULL, &var, &data) < 0) {
                fail_dpi(s->ctx);
                goto done;
            }
            dpiData_setTimestamp(data, (int16_t)y, (uint8_t)m, (uint8_t)d, 0, 0, 0, 0, 0, 0);
        }
        break;
    case 'L':
        /* o Oracle SQL nao tem booleano: vai como 1/0 */
        if (dpiConn_newVar(s->conn, DPI_ORACLE_TYPE_NUMBER, DPI_NATIVE_TYPE_INT64, 1, 0, 0, 0, NULL,
                           &var, &data) < 0) {
            fail_dpi(s->ctx);
            goto done;
        }
        dpiData_setInt64(data, (len && strchr("TYS1tys", t[0])) ? 1 : 0);
        break;
    case 'Z':
        if (dpiConn_newVar(s->conn, DPI_ORACLE_TYPE_VARCHAR, DPI_NATIVE_TYPE_BYTES, 1, 1, 1, 0, NULL,
                           &var, &data) < 0) {
            fail_dpi(s->ctx);
            goto done;
        }
        dpiData_setNull(data);
        break;
    default: { /* 'C': texto, sem cortar espacos */
        size_t tl = strlen(b->value);
        if (dpiConn_newVar(s->conn,
                           tl > 4000 ? DPI_ORACLE_TYPE_LONG_VARCHAR : DPI_ORACLE_TYPE_VARCHAR,
                           DPI_NATIVE_TYPE_BYTES, 1, (uint32_t)(tl ? tl : 1), 1, 0, NULL, &var,
                           &data) < 0 ||
            dpiVar_setFromBytes(var, 0, b->value, (uint32_t)tl) < 0) {
            fail_dpi(s->ctx);
            goto done;
        }
        break;
    }
    }
    if (dpiStmt_bindByPos(s->stmt, pos, var) < 0) {
        fail_dpi(s->ctx);
        goto done;
    }
    s->binds = br_realloc(s->binds, (s->nbinds + 1) * sizeof(dpiVar *));
    s->binds[s->nbinds++] = var;
    var = NULL;
    rc = 0;
done:
    if (var)
        dpiVar_release(var);
    free(v);
    return rc;
}

/* ------------------------------------------------------------------ Consulta */

typedef enum { M_TEXT, M_NUM, M_DOUBLE, M_FLOAT, M_INT, M_UINT, M_DATE, M_BOOL, M_CLOB, M_BLOB } Mode;

typedef struct {
    Column col;
    Mode mode;
    dpiVar *var;
    dpiData *data;
    size_t cap;
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

/* Texto do valor da linha i (malloc), ou NULL para NULL do banco. */
static char *cell_text(QCol *q, uint32_t i, dpiContext *ctx, int *err)
{
    dpiData *d = &q->data[i];
    char buf[64];

    if (d->isNull)
        return NULL;
    switch (q->mode) {
    case M_NUM:
    case M_TEXT:
        return br_strndup(d->value.asBytes.ptr, d->value.asBytes.length);
    case M_DOUBLE:
        br_double_text(d->value.asDouble, 0, buf, sizeof buf);
        return br_strdup(buf);
    case M_FLOAT:
        br_double_text((double)d->value.asFloat, 1, buf, sizeof buf);
        return br_strdup(buf);
    case M_INT:
        snprintf(buf, sizeof buf, "%lld", (long long)d->value.asInt64);
        return br_strdup(buf);
    case M_UINT:
        snprintf(buf, sizeof buf, "%llu", (unsigned long long)d->value.asUint64);
        return br_strdup(buf);
    case M_DATE:
        snprintf(buf, sizeof buf, "%04d%02d%02d", d->value.asTimestamp.year, d->value.asTimestamp.month,
                 d->value.asTimestamp.day);
        return br_strdup(buf);
    case M_BOOL:
        return br_strdup(d->value.asBoolean ? "T" : "F");
    case M_CLOB:
    case M_BLOB: {
        /* so o inicio do LOB: o campo caractere do DBF tem no maximo 254 posicoes */
        uint64_t got = LOB_CHARS * 4, amount = q->mode == M_CLOB ? LOB_CHARS : LOB_CHARS / 2;
        char *raw = br_alloc(LOB_CHARS * 4 + 1);
        if (dpiLob_readBytes(d->value.asLOB, 1, amount, raw, &got) < 0) {
            fail_dpi(ctx);
            *err = 1;
            free(raw);
            return NULL;
        }
        if (q->mode == M_BLOB) {
            char *hex = br_alloc((size_t)got * 2 + 1);
            hex_encode((unsigned char *)raw, (size_t)got, hex); /* RAW/BLOB: hexadecimal */
            free(raw);
            return hex;
        }
        raw[got] = '\0';
        return raw;
    }
    }
    return NULL;
}

/*
 * Cria a variavel de saida da coluna. O tipo pedido ao ODPI-C define como o valor
 * chega: NUMBER como texto (sem perder precisao), datas como estrutura, o resto como
 * texto (o Oracle converte RAW em hexadecimal, ROWID em texto etc.).
 */
static int define_column(Session *s, uint32_t pos, const dpiQueryInfo *qi, QCol *q)
{
    dpiOracleTypeNum ot = qi->typeInfo.oracleTypeNum;
    dpiOracleTypeNum vt = DPI_ORACLE_TYPE_VARCHAR;
    dpiNativeTypeNum nt = DPI_NATIVE_TYPE_BYTES;
    uint32_t size = 1;

    q->mode = M_TEXT;
    q->col.kind = COL_C;
    switch (ot) {
    case DPI_ORACLE_TYPE_NUMBER:
        vt = DPI_ORACLE_TYPE_NUMBER; q->mode = M_NUM; q->col.kind = COL_N;
        break;
    case DPI_ORACLE_TYPE_NATIVE_DOUBLE:
        vt = ot; nt = DPI_NATIVE_TYPE_DOUBLE; q->mode = M_DOUBLE; q->col.kind = COL_N;
        break;
    case DPI_ORACLE_TYPE_NATIVE_FLOAT:
        vt = ot; nt = DPI_NATIVE_TYPE_FLOAT; q->mode = M_FLOAT; q->col.kind = COL_N;
        break;
    case DPI_ORACLE_TYPE_NATIVE_INT:
        vt = ot; nt = DPI_NATIVE_TYPE_INT64; q->mode = M_INT; q->col.kind = COL_N;
        break;
    case DPI_ORACLE_TYPE_NATIVE_UINT:
        vt = ot; nt = DPI_NATIVE_TYPE_UINT64; q->mode = M_UINT; q->col.kind = COL_N;
        break;
    case DPI_ORACLE_TYPE_DATE:
    case DPI_ORACLE_TYPE_TIMESTAMP:
    case DPI_ORACLE_TYPE_TIMESTAMP_TZ:
    case DPI_ORACLE_TYPE_TIMESTAMP_LTZ:
        /* o campo D do Clipper nao guarda hora */
        vt = ot; nt = DPI_NATIVE_TYPE_TIMESTAMP; q->mode = M_DATE; q->col.kind = COL_D;
        break;
    case DPI_ORACLE_TYPE_BOOLEAN:
        vt = ot; nt = DPI_NATIVE_TYPE_BOOLEAN; q->mode = M_BOOL; q->col.kind = COL_L;
        break;
    case DPI_ORACLE_TYPE_CLOB:
    case DPI_ORACLE_TYPE_NCLOB:
        vt = ot; nt = DPI_NATIVE_TYPE_LOB; q->mode = M_CLOB;
        break;
    case DPI_ORACLE_TYPE_BLOB:
        vt = ot; nt = DPI_NATIVE_TYPE_LOB; q->mode = M_BLOB;
        break;
    default: {
        /* VARCHAR2, CHAR, RAW, ROWID, LONG etc. viram texto; folga para a conversao de charset */
        uint32_t base = qi->typeInfo.clientSizeInBytes;
        if (qi->typeInfo.dbSizeInBytes > base)
            base = qi->typeInfo.dbSizeInBytes;
        if (qi->typeInfo.sizeInChars > base)
            base = qi->typeInfo.sizeInChars;
        size = base * 4;
        if (size < 64)
            size = 64;
        if (base == 0 || size > 32767)
            size = 32767;
        break;
    }
    }
    if (dpiConn_newVar(s->conn, vt, nt, FETCH_ROWS, size, 1, 0, NULL, &q->var, &q->data) < 0 ||
        dpiStmt_define(s->stmt, pos, q->var) < 0)
        return fail_dpi(s->ctx);
    return 0;
}

static void free_columns(QCol *cols, size_t ncols, size_t nrows)
{
    size_t c, r;
    for (c = 0; c < ncols; c++) {
        for (r = 0; r < nrows; r++)
            free(cols[c].col.vals[r]);
        free(cols[c].col.vals);
        free(cols[c].col.name);
        if (cols[c].var)
            dpiVar_release(cols[c].var);
    }
    free(cols);
}

/* Executa o SELECT e grava o DBF. Devolve 0 se deu certo. */
static int do_query(Session *s, const Request *req, long *count, int *truncated)
{
    uint32_t ncols = 0, c;
    QCol *cols = NULL;
    size_t nrows = 0, cap = 0;
    long limit = 0;
    int more = 1, stop = 0, rc = -1, err = 0;
    char msg[512];

    if (req->maxrows)
        limit = atol(req->maxrows);
    if (limit < 0)
        limit = 0;

    dpiStmt_setFetchArraySize(s->stmt, FETCH_ROWS);
    if (dpiStmt_execute(s->stmt, DPI_MODE_EXEC_DEFAULT, &ncols) < 0)
        return fail_dpi(s->ctx);
    if (ncols == 0)
        return fail("%s", "o comando SQL nao retorna colunas (use ORA EXEC)");

    cols = br_alloc(ncols * sizeof(QCol));
    memset(cols, 0, ncols * sizeof(QCol));
    for (c = 0; c < ncols; c++) {
        dpiQueryInfo qi;
        if (dpiStmt_getQueryInfo(s->stmt, c + 1, &qi) < 0) {
            fail_dpi(s->ctx);
            goto done;
        }
        cols[c].col.name = br_strndup(qi.name, qi.nameLength);
        if (define_column(s, c + 1, &qi, &cols[c]) < 0)
            goto done;
    }

    while (more && !stop) {
        uint32_t idx, got, i;
        if (dpiStmt_fetchRows(s->stmt, FETCH_ROWS, &idx, &got, &more) < 0) {
            fail_dpi(s->ctx);
            goto done;
        }
        for (i = 0; i < got; i++) {
            /* uma linha alem do limite basta para saber que houve corte */
            if (limit && (long)nrows == limit) {
                *truncated = 1;
                stop = 1;
                break;
            }
            if (nrows == cap) {
                cap = cap ? cap * 2 : 1024;
                for (c = 0; c < ncols; c++)
                    cols[c].col.vals = br_realloc(cols[c].col.vals, cap * sizeof(char *));
            }
            for (c = 0; c < ncols; c++) {
                cols[c].col.vals[nrows] = cell_text(&cols[c], i, s->ctx, &err);
                if (err)
                    goto done;
            }
            nrows++;
        }
    }

    {
        Column *plain = br_alloc(ncols * sizeof(Column));
        for (c = 0; c < ncols; c++)
            plain[c] = cols[c].col;
        rc = br_write_dbf(req->out, plain, ncols, nrows, req->codepage, req->cp, msg, sizeof msg);
        free(plain);
        if (rc != 0)
            fail("%s", msg);
    }
    *count = (long)nrows;
done:
    free_columns(cols, ncols, nrows);
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
    Session s;
    dpiErrorInfo info;
    char *sql = NULL;
    const char *action = req->action ? req->action : "";
    uint32_t ncols;
    int rc = -1, is_ping;
    size_t i;

    memset(&s, 0, sizeof s);
    *count = 0;
    *truncated = 0;

    if (!req->user) return fail("campo ausente: %s", "USER");
    if (!req->pass) return fail("campo ausente: %s", "PASS");
    if (!req->dsn) return fail("campo ausente: %s", "DSN");

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
        sql = br_strdup("select 1 from dual"); /* so verifica se a conexao e a consulta funcionam */
    }

    if (dpiContext_createWithParams(DPI_MAJOR_VERSION, DPI_MINOR_VERSION, NULL, &s.ctx, &info) < 0) {
        copy_err(&info); /* tipicamente: Oracle Client nao encontrado (DPI-1047) */
        goto done;
    }
    if (dpiConn_create(s.ctx, req->user, (uint32_t)strlen(req->user), req->pass,
                       (uint32_t)strlen(req->pass), req->dsn, (uint32_t)strlen(req->dsn), NULL, NULL,
                       &s.conn) < 0) {
        fail_dpi(s.ctx);
        goto done;
    }
    if (dpiConn_prepareStmt(s.conn, 0, sql, (uint32_t)strlen(sql), NULL, 0, &s.stmt) < 0) {
        fail_dpi(s.ctx);
        goto done;
    }
    for (i = 0; !is_ping && i < req->nbinds; i++)
        if (bind_one(&s, (uint32_t)(i + 1), &req->binds[i]) < 0)
            goto done;

    if (is_ping) {
        if (dpiStmt_execute(s.stmt, DPI_MODE_EXEC_DEFAULT, &ncols) < 0)
            fail_dpi(s.ctx);
        else
            rc = 0;
    } else if (ci_eq(action, "EXEC")) {
        uint64_t rows = 0;
        /* commit junto com a execucao */
        if (dpiStmt_execute(s.stmt, DPI_MODE_EXEC_COMMIT_ON_SUCCESS, &ncols) < 0) {
            fail_dpi(s.ctx);
        } else {
            dpiStmt_getRowCount(s.stmt, &rows);
            *count = (long)rows;
            rc = 0;
        }
    } else {
        rc = do_query(&s, req, count, truncated);
    }
done:
    for (i = 0; i < s.nbinds; i++)
        dpiVar_release(s.binds[i]);
    free(s.binds);
    if (s.stmt)
        dpiStmt_release(s.stmt);
    if (s.conn) {
        dpiConn_close(s.conn, DPI_MODE_CONN_CLOSE_DEFAULT, NULL, 0);
        dpiConn_release(s.conn);
    }
    if (s.ctx)
        dpiContext_destroy(s.ctx);
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
        fputs("Uso: ORABRIDGE <arquivo.REQ>\n", stderr);
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
        /* qualquer falha (login, SQL, DBF...) vira "ERR" + mensagem numa linha so; o RUN do
         * Clipper nao recebe codigo de saida, entao o erro vai pelo .RSP */
        one_line(g_err);
        lines[0] = "ERR";
        lines[1] = g_err[0] ? g_err : "erro desconhecido";
        br_write_response(req.rsp, req.cp, lines, 2);
    }
    br_free_request(&req);
    return 0;
}
