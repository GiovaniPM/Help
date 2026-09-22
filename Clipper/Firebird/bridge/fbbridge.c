/*
 * fbbridge.c - ponte entre a biblioteca FIREBIRD.LIB (Clipper 5.2) e o banco Firebird.
 *
 * Uso:  FBBRIDGE <arquivo.REQ>
 *
 * O Clipper grava um arquivo de requisicao (KEY=VALUE, uma por linha), roda este
 * programa com RUN e le o arquivo de resposta indicado em RSP=.
 *
 * Requisicao:
 *     ACTION=PING | QUERY | EXEC
 *     USER=, PASS=, DSN=      DSN e "host/porta:caminho\banco.fdb" (porta opcional,
 *                              padrao 3050) ou so o caminho do .fdb para um Firebird local
 *     SQLFILE=                arquivo com o comando SQL
 *     RSP=                    arquivo de resposta
 *     OUT=                    (QUERY) DBF a ser gerado
 *     CODEPAGE=               pagina de codigo do Clipper (padrao cp850)
 *     MAXROWS=                limite de linhas do QUERY (0 = sem limite)
 *     BIND=<tipo>|<valor>     binds posicionais (preenchem os "?" do SQL, na ordem);
 *                              tipo C, N, D, L ou Z (nulo)
 *
 * Resposta:
 *     OK / <linhas afetadas ou retornadas> / <1 se truncou no MAXROWS, senao 0>
 *     ERR / <mensagem>
 *
 * Valores dos binds escapam \ como \\, CR como \r e LF como \n.
 *
 * Acesso ao Firebird: API classica (ibase.h + fbclient), que carrega o cliente do
 * Firebird em tempo de execucao; ele precisa estar no PATH (ou na pasta do
 * programa) com a mesma arquitetura (32/64 bits) deste executavel. A conexao
 * usa charset UTF8 (isc_dpb_lc_ctype), entao o Firebird converte para/do
 * charset de cada coluna automaticamente; todo texto trocado com a ponte aqui
 * dentro e UTF-8.
 */
#include "bridge_core.h"

#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <ibase.h>

#define SQL_DIALECT 3
#define LOB_CHARS   DBF_MAX_CHAR /* so o inicio de um BLOB cabe no campo caractere */

static char g_err[2048]; /* mensagem do ultimo erro */

/* ------------------------------------------------------------------- Erros */

/* Junta as linhas de fb_interpret() em g_err e devolve -1. */
static int fail_isc(const ISC_STATUS *status)
{
    const ISC_STATUS *p = status;
    char line[512];
    size_t n = 0;
    g_err[0] = '\0';
    while (fb_interpret(line, sizeof line, &p)) {
        size_t l = strlen(line);
        if (n && n + 1 < sizeof g_err)
            g_err[n++] = ' ';
        if (n + l >= sizeof g_err)
            l = sizeof g_err - 1 - n;
        memcpy(g_err + n, line, l);
        n += l;
        g_err[n] = '\0';
    }
    if (!g_err[0])
        strcpy(g_err, "erro desconhecido do Firebird");
    return -1;
}

static int fail(const char *fmt, const char *arg)
{
    snprintf(g_err, sizeof g_err, fmt, arg ? arg : "");
    return -1;
}

/* ------------------------------------------------------------------ Estado */

typedef struct {
    isc_db_handle db;
    isc_tr_handle trans;
    isc_stmt_handle stmt;
} Session;

/* --------------------------------------------------------------- Conexao */

static int connect_db(Session *s, const Request *req)
{
    ISC_STATUS_ARRAY status;
    char dpb[600], *p = dpb; /* cabe user+pass (255 bytes cada, no pior caso) + lc_ctype */
    size_t ul = strlen(req->user), pl = strlen(req->pass);

    if (ul > 255 || pl > 255)
        return fail("%s", "usuario ou senha grande demais");

    *p++ = isc_dpb_version1;
    *p++ = isc_dpb_user_name;
    *p++ = (char)ul;
    memcpy(p, req->user, ul);
    p += ul;
    *p++ = isc_dpb_password;
    *p++ = (char)pl;
    memcpy(p, req->pass, pl);
    p += pl;
    *p++ = isc_dpb_lc_ctype;
    *p++ = 4;
    memcpy(p, "UTF8", 4);
    p += 4;

    s->db = 0;
    if (isc_attach_database(status, (short)strlen(req->dsn), req->dsn, &s->db,
                            (short)(p - dpb), dpb))
        return fail_isc(status);
    return 0;
}

static int start_tr(Session *s)
{
    ISC_STATUS_ARRAY status;
    s->trans = 0;
    if (isc_start_transaction(status, &s->trans, 1, &s->db, 0, (char *)NULL))
        return fail_isc(status);
    return 0;
}

static int prepare(Session *s, const char *sql)
{
    ISC_STATUS_ARRAY status;
    s->stmt = 0;
    if (isc_dsql_allocate_statement(status, &s->db, &s->stmt))
        return fail_isc(status);
    if (isc_dsql_prepare(status, &s->trans, &s->stmt, 0, sql, SQL_DIALECT, NULL))
        return fail_isc(status);
    return 0;
}

/* ------------------------------------------------------------- XSQLDA/binds */

/* Aloca e zera um XSQLDA para n colunas/parametros. */
static XSQLDA *alloc_sqlda(short n)
{
    XSQLDA *sqlda = (XSQLDA *)br_alloc(XSQLDA_LENGTH(n ? n : 1));
    memset(sqlda, 0, XSQLDA_LENGTH(n ? n : 1));
    sqlda->version = SQLDA_VERSION1;
    sqlda->sqln = n ? n : 1;
    return sqlda;
}

/* isc_dsql_describe[_bind]() com o vetor redimensionado se precisar de mais colunas. */
static int describe(Session *s, int is_bind, XSQLDA **out)
{
    ISC_STATUS_ARRAY status;
    XSQLDA *sqlda = alloc_sqlda(1);
    ISC_STATUS rc = is_bind ? isc_dsql_describe_bind(status, &s->stmt, SQL_DIALECT, sqlda)
                             : isc_dsql_describe(status, &s->stmt, SQL_DIALECT, sqlda);
    if (rc) {
        free(sqlda);
        return fail_isc(status);
    }
    if (sqlda->sqld > sqlda->sqln) {
        short n = sqlda->sqld;
        free(sqlda);
        sqlda = alloc_sqlda(n);
        rc = is_bind ? isc_dsql_describe_bind(status, &s->stmt, SQL_DIALECT, sqlda)
                     : isc_dsql_describe(status, &s->stmt, SQL_DIALECT, sqlda);
        if (rc) {
            free(sqlda);
            return fail_isc(status);
        }
    }
    *out = sqlda;
    return 0;
}

/* Converte um double para inteiro escalado (10^-scale), como o Firebird guarda NUMERIC/DECIMAL. */
static ISC_INT64 to_scaled(double val, short scale)
{
    double factor = pow(10.0, (double)-scale);
    double scaled = val * factor;
    return (ISC_INT64)(scaled >= 0 ? scaled + 0.5 : scaled - 0.5);
}

/* Formata um inteiro escalado (10^scale) como texto decimal. */
static void format_scaled(ISC_INT64 v, short scale, char *out, size_t outsz)
{
    char digits[40];
    int neg = v < 0;
    unsigned long long av = neg ? (unsigned long long)(-v) : (unsigned long long)v;
    int nd = snprintf(digits, sizeof digits, "%llu", av);

    if (scale >= 0) {
        /* caso raro (NUMERIC com escala positiva); normalmente scale == 0 */
        int i;
        size_t n = (size_t)snprintf(out, outsz, "%s%s", neg ? "-" : "", digits);
        for (i = 0; i < scale && n + 1 < outsz; i++)
            out[n++] = '0';
        out[n < outsz ? n : outsz - 1] = '\0';
    } else {
        int dec = -scale;
        if (nd <= dec)
            snprintf(out, outsz, "%s0.%0*llu", neg ? "-" : "", dec, av);
        else
            snprintf(out, outsz, "%s%.*s.%s", neg ? "-" : "", nd - dec, digits, digits + (nd - dec));
    }
}

/* Cria o valor de um bind (posicao pos-1 de in_sqlda) a partir do valor do Clipper. */
static int bind_one(XSQLVAR *var, const Bind *b)
{
    short base = (short)(var->sqltype & ~1);
    char *v = br_strdup(b->value), *t = v;
    size_t len;
    int rc = 0;

    while (isspace((unsigned char)*t))
        t++;
    len = strlen(t);
    while (len && isspace((unsigned char)t[len - 1]))
        t[--len] = '\0';

    var->sqlind = (short *)br_alloc(sizeof(short));
    *var->sqlind = 0;
    var->sqltype = (short)(base | 1);

    if (b->type == 'Z' || ((b->type == 'N' || b->type == 'D') && len == 0)) {
        var->sqllen = 0;
        var->sqldata = br_alloc(1);
        *var->sqlind = -1;
        goto done;
    }

    switch (b->type) {
    case 'N': {
        char *endp;
        double val = strtod(t, &endp);
        if (endp == t || *endp) {
            fail("valor numerico invalido no bind: %s", t);
            rc = -1;
            break;
        }
        switch (base) {
        case SQL_SHORT: {
            ISC_SHORT iv = (ISC_SHORT)to_scaled(val, var->sqlscale);
            var->sqllen = 2;
            var->sqldata = br_alloc(2);
            memcpy(var->sqldata, &iv, 2);
            break;
        }
        case SQL_LONG: {
            ISC_LONG iv = (ISC_LONG)to_scaled(val, var->sqlscale);
            var->sqllen = 4;
            var->sqldata = br_alloc(4);
            memcpy(var->sqldata, &iv, 4);
            break;
        }
        case SQL_INT64: {
            ISC_INT64 iv = to_scaled(val, var->sqlscale);
            var->sqllen = 8;
            var->sqldata = br_alloc(8);
            memcpy(var->sqldata, &iv, 8);
            break;
        }
        case SQL_FLOAT: {
            float f = (float)val;
            var->sqllen = 4;
            var->sqldata = br_alloc(4);
            memcpy(var->sqldata, &f, 4);
            break;
        }
        case SQL_DOUBLE:
        case SQL_D_FLOAT: {
            double d = val;
            var->sqltype = (short)(SQL_DOUBLE | 1);
            var->sqllen = 8;
            var->sqldata = br_alloc(8);
            memcpy(var->sqldata, &d, 8);
            break;
        }
        default:
            /* parametro nao numerico (ex.: coluna texto): manda o texto e deixa
             * o Firebird converter, do mesmo jeito que faria com um literal */
            var->sqltype = (short)(SQL_TEXT | 1);
            var->sqllen = (short)len;
            var->sqldata = br_alloc(len ? len : 1);
            memcpy(var->sqldata, t, len);
            break;
        }
        break;
    }
    case 'D': {
        int y, mo, d;
        struct tm tm;
        if (len < 8 || sscanf(t, "%4d%2d%2d", &y, &mo, &d) != 3) {
            fail("data invalida no bind: %s", t);
            rc = -1;
            break;
        }
        memset(&tm, 0, sizeof tm);
        tm.tm_year = y - 1900;
        tm.tm_mon = mo - 1;
        tm.tm_mday = d;
        switch (base) {
        case SQL_TYPE_DATE: {
            ISC_DATE dt;
            isc_encode_sql_date(&tm, &dt);
            var->sqllen = 4;
            var->sqldata = br_alloc(4);
            memcpy(var->sqldata, &dt, 4);
            break;
        }
        case SQL_TIMESTAMP: {
            ISC_TIMESTAMP ts;
            isc_encode_timestamp(&tm, &ts);
            var->sqllen = 8;
            var->sqldata = br_alloc(8);
            memcpy(var->sqldata, &ts, 8);
            break;
        }
        default: {
            char buf[16];
            size_t bl;
            snprintf(buf, sizeof buf, "%04d-%02d-%02d", y, mo, d);
            bl = strlen(buf);
            var->sqltype = (short)(SQL_TEXT | 1);
            var->sqllen = (short)bl;
            var->sqldata = br_alloc(bl);
            memcpy(var->sqldata, buf, bl);
            break;
        }
        }
        break;
    }
    case 'L': {
        int tv = (len && strchr("TYS1tys", t[0])) ? 1 : 0;
        if (base == SQL_BOOLEAN) {
            var->sqllen = 1;
            var->sqldata = br_alloc(1);
            var->sqldata[0] = (char)tv;
        } else {
            ISC_LONG iv = tv;
            var->sqltype = (short)(SQL_LONG | 1);
            var->sqllen = 4;
            var->sqldata = br_alloc(4);
            memcpy(var->sqldata, &iv, 4);
        }
        break;
    }
    default: { /* 'C': texto, sem cortar espacos */
        size_t tl = strlen(b->value);
        var->sqltype = (short)(SQL_TEXT | 1);
        var->sqllen = (short)tl;
        var->sqldata = br_alloc(tl ? tl : 1);
        memcpy(var->sqldata, b->value, tl);
        break;
    }
    }
done:
    free(v);
    return rc;
}

static void free_sqlda_data(XSQLDA *sqlda)
{
    short i;
    if (!sqlda)
        return;
    for (i = 0; i < sqlda->sqld; i++) {
        free(sqlda->sqlvar[i].sqldata);
        free(sqlda->sqlvar[i].sqlind);
    }
    free(sqlda);
}

/* ------------------------------------------------------------------ Colunas */

typedef enum {
    M_TEXT, M_VARTEXT, M_SHORT, M_LONG, M_INT64, M_DOUBLE, M_FLOAT,
    M_DATE, M_TIMESTAMP, M_TIME, M_BOOL, M_BLOB_TEXT, M_BLOB_BIN
} Mode;

typedef struct {
    Column col;
    Mode mode;
    short scale;
    XSQLVAR *var;
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

static void set_mode(QCol *q, XSQLVAR *var)
{
    short base = (short)(var->sqltype & ~1);
    q->col.kind = COL_C;
    q->mode = M_TEXT;
    q->scale = 0;
    switch (base) {
    case SQL_SHORT: q->mode = M_SHORT; q->col.kind = COL_N; q->scale = var->sqlscale; break;
    case SQL_LONG: q->mode = M_LONG; q->col.kind = COL_N; q->scale = var->sqlscale; break;
    case SQL_INT64: q->mode = M_INT64; q->col.kind = COL_N; q->scale = var->sqlscale; break;
    case SQL_DOUBLE:
    case SQL_D_FLOAT: q->mode = M_DOUBLE; q->col.kind = COL_N; break;
    case SQL_FLOAT: q->mode = M_FLOAT; q->col.kind = COL_N; break;
    case SQL_TYPE_DATE: q->mode = M_DATE; q->col.kind = COL_D; break;
    case SQL_TIMESTAMP: q->mode = M_TIMESTAMP; q->col.kind = COL_D; break;
    case SQL_TYPE_TIME: q->mode = M_TIME; q->col.kind = COL_C; break; /* Clipper nao tem tipo hora */
    case SQL_BOOLEAN: q->mode = M_BOOL; q->col.kind = COL_L; break;
    case SQL_VARYING: q->mode = M_VARTEXT; q->col.kind = COL_C; break;
    case SQL_TEXT: q->mode = M_TEXT; q->col.kind = COL_C; break;
    case SQL_BLOB:
        q->mode = (var->sqlsubtype == 1) ? M_BLOB_TEXT : M_BLOB_BIN;
        q->col.kind = COL_C;
        break;
    default: /* SQL_ARRAY, SQL_QUAD (RDB$DB_KEY) etc.: melhor esforco como texto */
        q->mode = M_TEXT;
        q->col.kind = COL_C;
        break;
    }
}

static void alloc_var_buffer(XSQLVAR *var)
{
    short base = (short)(var->sqltype & ~1);
    var->sqltype = (short)(base | 1);
    var->sqlind = (short *)br_alloc(sizeof(short));
    switch (base) {
    case SQL_VARYING:
        var->sqldata = br_alloc((size_t)var->sqllen + 2);
        break;
    case SQL_BLOB:
    case SQL_ARRAY:
        var->sqllen = sizeof(ISC_QUAD);
        var->sqldata = br_alloc(sizeof(ISC_QUAD));
        break;
    default:
        var->sqldata = br_alloc(var->sqllen ? (size_t)var->sqllen : 1);
        break;
    }
}

/* Le so o inicio do BLOB (o campo caractere do DBF tem no maximo 254 posicoes). */
static char *read_blob(Session *s, QCol *q, int *err)
{
    ISC_STATUS_ARRAY status;
    isc_blob_handle bh = 0;
    ISC_QUAD id;
    unsigned short seg_len;
    char seg[512];
    size_t limit = LOB_CHARS * 4, got = 0; /* UTF-8: ate 4 bytes por caractere */
    char *out = br_alloc(limit + 1);

    memcpy(&id, q->var->sqldata, sizeof id);
    if (isc_open_blob2(status, &s->db, &s->trans, &bh, &id, 0, NULL)) {
        *err = 1;
        fail_isc(status);
        free(out);
        return NULL;
    }
    for (;;) {
        ISC_STATUS st = isc_get_segment(status, &bh, &seg_len, (unsigned short)sizeof seg, seg);
        if (st != 0 && status[1] != isc_segment) {
            if (status[1] != isc_segstr_eof) {
                *err = 1;
                fail_isc(status);
                isc_close_blob(status, &bh);
                free(out);
                return NULL;
            }
            break; /* fim do blob */
        }
        if (seg_len) {
            size_t take = seg_len;
            if (got + take > limit)
                take = limit - got;
            memcpy(out + got, seg, take);
            got += take;
        }
        if (got >= limit)
            break;
    }
    isc_close_blob(status, &bh);
    if (q->mode == M_BLOB_BIN) {
        char *hex = br_alloc(got * 2 + 1);
        hex_encode((unsigned char *)out, got, hex);
        free(out);
        return hex;
    }
    out[got] = '\0';
    return out;
}

/* Texto do valor da coluna (malloc), ou NULL para NULL do banco. */
static char *cell_text(Session *s, QCol *q, int *err)
{
    XSQLVAR *var = q->var;
    char buf[64];

    if (*var->sqlind < 0)
        return NULL;
    switch (q->mode) {
    case M_TEXT: {
        size_t n = (size_t)var->sqllen;
        while (n && var->sqldata[n - 1] == ' ')
            n--;
        return br_strndup(var->sqldata, n);
    }
    case M_VARTEXT: {
        /* SQL_VARYING: 2 bytes de tamanho (little endian) seguidos dos dados */
        unsigned short vlen;
        memcpy(&vlen, var->sqldata, 2);
        return br_strndup(var->sqldata + 2, vlen);
    }
    case M_SHORT: {
        ISC_SHORT v;
        memcpy(&v, var->sqldata, 2);
        format_scaled(v, q->scale, buf, sizeof buf);
        return br_strdup(buf);
    }
    case M_LONG: {
        ISC_LONG v;
        memcpy(&v, var->sqldata, 4);
        format_scaled(v, q->scale, buf, sizeof buf);
        return br_strdup(buf);
    }
    case M_INT64: {
        ISC_INT64 v;
        memcpy(&v, var->sqldata, 8);
        format_scaled(v, q->scale, buf, sizeof buf);
        return br_strdup(buf);
    }
    case M_DOUBLE: {
        double v;
        memcpy(&v, var->sqldata, 8);
        br_double_text(v, 0, buf, sizeof buf);
        return br_strdup(buf);
    }
    case M_FLOAT: {
        float v;
        memcpy(&v, var->sqldata, 4);
        br_double_text((double)v, 1, buf, sizeof buf);
        return br_strdup(buf);
    }
    case M_DATE: {
        ISC_DATE d;
        struct tm tm;
        memcpy(&d, var->sqldata, 4);
        isc_decode_sql_date(&d, &tm);
        snprintf(buf, sizeof buf, "%04d%02d%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);
        return br_strdup(buf);
    }
    case M_TIMESTAMP: {
        /* o campo D do Clipper nao guarda hora */
        ISC_TIMESTAMP t;
        struct tm tm;
        memcpy(&t, var->sqldata, 8);
        isc_decode_timestamp(&t, &tm);
        snprintf(buf, sizeof buf, "%04d%02d%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);
        return br_strdup(buf);
    }
    case M_TIME: {
        ISC_TIME t;
        struct tm tm;
        memcpy(&t, var->sqldata, 4);
        isc_decode_sql_time(&t, &tm);
        snprintf(buf, sizeof buf, "%02d:%02d:%02d", tm.tm_hour, tm.tm_min, tm.tm_sec);
        return br_strdup(buf);
    }
    case M_BOOL:
        return br_strdup(var->sqldata[0] ? "T" : "F");
    case M_BLOB_TEXT:
    case M_BLOB_BIN:
        return read_blob(s, q, err);
    }
    return NULL;
}

static void free_columns(QCol *cols, XSQLDA *out_sqlda, size_t nrows)
{
    unsigned short c, ncols = out_sqlda ? (unsigned short)out_sqlda->sqld : 0;
    for (c = 0; c < ncols; c++) {
        size_t r;
        for (r = 0; r < nrows; r++)
            free(cols[c].col.vals[r]);
        free(cols[c].col.vals);
        free(cols[c].col.name);
    }
    free(cols);
    free_sqlda_data(out_sqlda);
}

/* Numero de linhas afetadas (INSERT/UPDATE/DELETE); 0 se nao conseguir ler (nao fatal). */
static long affected_rows(Session *s)
{
    ISC_STATUS_ARRAY status;
    char item = isc_info_sql_records;
    char res[64];
    long total = 0;
    short len, end, i;

    if (isc_dsql_sql_info(status, &s->stmt, 1, &item, sizeof res, res) || res[0] != isc_info_sql_records)
        return 0;
    len = (short)isc_vax_integer(res + 1, 2);
    end = (short)(3 + len);
    if (end > (short)sizeof res)
        end = (short)sizeof res;
    i = 3;
    while (i + 3 <= end) {
        char code = res[i++];
        short l = (short)isc_vax_integer(res + i, 2);
        i += 2;
        if (i + l > end)
            break;
        if (code == isc_info_req_insert_count || code == isc_info_req_update_count ||
            code == isc_info_req_delete_count)
            total += isc_vax_integer(res + i, l);
        i += l;
    }
    return total;
}

/* Executa o SELECT (com os binds ja descritos em in_sqlda) e grava o DBF. */
static int do_query(Session *s, const Request *req, XSQLDA *in_sqlda, long *count, int *truncated)
{
    ISC_STATUS_ARRAY status;
    XSQLDA *out_sqlda = NULL;
    QCol *cols = NULL;
    unsigned short ncols, c;
    size_t nrows = 0, cap = 0;
    long limit = 0;
    int rc = -1, err = 0;
    char msg[512];

    if (req->maxrows)
        limit = atol(req->maxrows);
    if (limit < 0)
        limit = 0;

    if (describe(s, 0, &out_sqlda) < 0)
        return -1;
    ncols = (unsigned short)out_sqlda->sqld;
    if (ncols == 0) {
        free(out_sqlda);
        return fail("%s", "o comando SQL nao retorna colunas (use FB EXEC)");
    }

    cols = br_alloc(ncols * sizeof(QCol));
    memset(cols, 0, ncols * sizeof(QCol));
    for (c = 0; c < ncols; c++) {
        XSQLVAR *var = &out_sqlda->sqlvar[c];
        const char *nm = var->aliasname_length ? var->aliasname : var->sqlname;
        short nl = var->aliasname_length ? var->aliasname_length : var->sqlname_length;
        cols[c].col.name = br_strndup(nm, (size_t)nl);
        set_mode(&cols[c], var);
        alloc_var_buffer(var);
        cols[c].var = var;
    }

    if (isc_dsql_execute(status, &s->trans, &s->stmt, SQL_DIALECT, in_sqlda)) {
        fail_isc(status);
        goto done;
    }

    for (;;) {
        ISC_STATUS fst;
        if (limit && (long)nrows == limit) {
            *truncated = 1;
            break;
        }
        fst = isc_dsql_fetch(status, &s->stmt, SQL_DIALECT, out_sqlda);
        if (fst == 100)
            break; /* sem mais linhas */
        if (fst) {
            fail_isc(status);
            goto done;
        }
        if (nrows == cap) {
            cap = cap ? cap * 2 : 1024;
            for (c = 0; c < ncols; c++)
                cols[c].col.vals = br_realloc(cols[c].col.vals, cap * sizeof(char *));
        }
        for (c = 0; c < ncols; c++) {
            cols[c].col.vals[nrows] = cell_text(s, &cols[c], &err);
            if (err)
                goto done;
        }
        nrows++;
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
    free_columns(cols, out_sqlda, nrows);
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
    ISC_STATUS_ARRAY status;
    char *sql = NULL;
    const char *action = req->action ? req->action : "";
    int rc = -1, is_ping;
    size_t i;
    XSQLDA *in_sqlda = NULL;

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
        sql = br_strdup("SELECT 1 FROM RDB$DATABASE"); /* so verifica se a conexao e a consulta funcionam */
    }

    if (connect_db(&s, req) < 0)
        goto done;
    if (start_tr(&s) < 0)
        goto done;
    if (prepare(&s, sql) < 0)
        goto done;

    if (!is_ping && req->nbinds > 0) {
        if (describe(&s, 1, &in_sqlda) < 0)
            goto done;
        if ((size_t)in_sqlda->sqld != req->nbinds) {
            snprintf(g_err, sizeof g_err,
                     "numero de binds nao confere: a consulta espera %d, foram enviados %u",
                     (int)in_sqlda->sqld, (unsigned)req->nbinds);
            goto done;
        }
        for (i = 0; i < req->nbinds; i++)
            if (bind_one(&in_sqlda->sqlvar[i], &req->binds[i]) < 0)
                goto done;
    }

    if (is_ping) {
        if (isc_dsql_execute(status, &s.trans, &s.stmt, SQL_DIALECT, NULL))
            fail_isc(status);
        else
            rc = 0;
    } else if (ci_eq(action, "EXEC")) {
        if (isc_dsql_execute(status, &s.trans, &s.stmt, SQL_DIALECT, in_sqlda)) {
            fail_isc(status);
        } else {
            *count = affected_rows(&s);
            rc = 0;
        }
    } else {
        rc = do_query(&s, req, in_sqlda, count, truncated);
    }
done:
    free_sqlda_data(in_sqlda);
    if (s.stmt) {
        ISC_STATUS_ARRAY st2;
        isc_dsql_free_statement(st2, &s.stmt, DSQL_drop);
    }
    if (s.trans) {
        ISC_STATUS_ARRAY st2;
        if (rc == 0)
            isc_commit_transaction(st2, &s.trans);
        else
            isc_rollback_transaction(st2, &s.trans);
    }
    if (s.db) {
        ISC_STATUS_ARRAY st2;
        isc_detach_database(st2, &s.db);
    }
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
        fputs("Uso: FBBRIDGE <arquivo.REQ>\n", stderr);
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
