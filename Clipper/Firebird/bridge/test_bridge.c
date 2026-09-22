/*
 * test_bridge.c - testes da ponte (sem banco).
 *
 *   test_bridge                   testa bridge_core (requisicao, binds, DBF)
 *   test_bridge <FBBRIDGE.EXE>    roda o executavel com um banco inexistente e confere o "ERR"
 */
#include "bridge_core.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int failures = 0, checks = 0;

#define CHECK(cond)                                                               \
    do {                                                                          \
        checks++;                                                                 \
        if (!(cond)) {                                                            \
            failures++;                                                           \
            printf("FALHOU %s:%d: %s\n", __FILE__, __LINE__, #cond);              \
        }                                                                         \
    } while (0)

#define CHECK_STR(a, b)                                                           \
    do {                                                                          \
        const char *_a = (a), *_b = (b);                                          \
        checks++;                                                                 \
        if (!_a || strcmp(_a, _b) != 0) {                                         \
            failures++;                                                           \
            printf("FALHOU %s:%d: \"%s\" != \"%s\"\n", __FILE__, __LINE__,        \
                   _a ? _a : "(null)", _b);                                       \
        }                                                                         \
    } while (0)

/* --------------------------------------------------------- leitor de DBF (independente do gravador) */

typedef struct {
    unsigned char *raw;
    size_t size;
    unsigned nrec, hdr, reclen;
    int nfields;
    char name[32][12];
    char type[32];
    int width[32], dec[32];
} Dbf;

static int dbf_open(const char *path, Dbf *d)
{
    size_t pos = 32;
    d->raw = br_read_file(path, &d->size);
    if (!d->raw)
        return 0;
    d->nrec = d->raw[4] | d->raw[5] << 8 | d->raw[6] << 16 | (unsigned)d->raw[7] << 24;
    d->hdr = d->raw[8] | d->raw[9] << 8;
    d->reclen = d->raw[10] | d->raw[11] << 8;
    d->nfields = 0;
    while (d->raw[pos] != 0x0D) {
        int f = d->nfields++;
        memcpy(d->name[f], d->raw + pos, 11);
        d->name[f][11] = '\0';
        d->type[f] = (char)d->raw[pos + 11];
        d->width[f] = d->raw[pos + 16];
        d->dec[f] = d->raw[pos + 17];
        pos += 32;
    }
    return pos + 1 == d->hdr && d->raw[d->size - 1] == 0x1A &&
           d->size == d->hdr + (size_t)d->nrec * d->reclen + 1;
}

/* conteudo do campo f do registro r (novo buffer terminado em '\0') */
static char *dbf_field(const Dbf *d, unsigned r, int f)
{
    size_t off = d->hdr + (size_t)r * d->reclen + 1;
    int i;
    for (i = 0; i < f; i++)
        off += d->width[i];
    return br_strndup((const char *)d->raw + off, d->width[f]);
}

static char *make_temp_path(const char *name)
{
    const char *dir = getenv("TEMP");
    char *p;
    if (!dir)
        dir = getenv("TMPDIR");
    if (!dir)
        dir = ".";
    p = br_alloc(strlen(dir) + strlen(name) + 16);
    sprintf(p, "%s/%s", dir, name);
    return p;
}

/* ------------------------------------------------------------------- testes */

static void test_dbf_tipos(void)
{
    char *path = make_temp_path("fbbridge_t1.dbf"), msg[256];
    char *v_id[] = {"1", "200"}, *v_valor[] = {"10.5", "0.25"};
    char *v_nome[] = {"Jo\xc3\xa3o", NULL}, *v_dt[] = {"20260921", NULL};
    char *v_sum[] = {"-3", NULL}, *v_sum2[] = {"7", "8"};
    Column cols[] = {
        {"ID", COL_N, v_id}, {"VALOR", COL_N, v_valor}, {"NOME", COL_C, v_nome},
        {"DT", COL_D, v_dt}, {"SUM(X)", COL_N, v_sum}, {"SUM(X)", COL_N, v_sum2},
    };
    Dbf d;
    char *f;
    const char *nomes[] = {"ID", "VALOR", "NOME", "DT", "SUM_X_", "SUM_X_1"};
    const char tipos[] = "NNCDNN";
    const int larg[] = {3, 5, 4, 8, 2, 1}, decs[] = {0, 2, 0, 0, 0, 0};
    int i;

    CHECK(br_write_dbf(path, cols, 6, 2, "cp850", 850, msg, sizeof msg) == 0);
    CHECK(dbf_open(path, &d));
    CHECK(d.raw[0] == 0x03);
    CHECK(d.raw[29] == 0x02);
    CHECK(d.nrec == 2 && d.nfields == 6);
    for (i = 0; i < 6; i++) {
        CHECK_STR(d.name[i], nomes[i]);
        CHECK(d.type[i] == tipos[i]);
        CHECK(d.width[i] == larg[i]);
        CHECK(d.dec[i] == decs[i]);
    }
    f = dbf_field(&d, 0, 0); CHECK_STR(f, "  1"); free(f);
    f = dbf_field(&d, 0, 1); CHECK_STR(f, "10.50"); free(f);
    f = dbf_field(&d, 0, 2); CHECK_STR(f, "Jo\xc6o"); free(f); /* a com til = 0xC6 em cp850 */
    f = dbf_field(&d, 0, 3); CHECK_STR(f, "20260921"); free(f);
    f = dbf_field(&d, 0, 4); CHECK_STR(f, "-3"); free(f);
    f = dbf_field(&d, 0, 5); CHECK_STR(f, "7"); free(f);
    f = dbf_field(&d, 1, 0); CHECK_STR(f, "200"); free(f);
    f = dbf_field(&d, 1, 1); CHECK_STR(f, " 0.25"); free(f);
    f = dbf_field(&d, 1, 2); CHECK_STR(f, "    "); free(f);
    f = dbf_field(&d, 1, 3); CHECK_STR(f, "        "); free(f);
    f = dbf_field(&d, 1, 4); CHECK_STR(f, "  "); free(f);
    f = dbf_field(&d, 1, 5); CHECK_STR(f, "8"); free(f);
    free(d.raw);
    free(path);
}

static void test_dbf_vazio(void)
{
    char *path = make_temp_path("fbbridge_t2.dbf"), msg[256];
    Column cols[] = {{"A", COL_C, NULL}};
    Dbf d;
    CHECK(br_write_dbf(path, cols, 1, 0, "cp850", 850, msg, sizeof msg) == 0);
    CHECK(dbf_open(path, &d));
    CHECK(d.nrec == 0 && d.type[0] == 'C' && d.width[0] == 1);
    free(d.raw);
    free(path);
}

static void test_dbf_numeros(void)
{
    char *path = make_temp_path("fbbridge_t3.dbf"), msg[256];
    Dbf d;
    char *f;

    {   /* numero grande demais vira caractere */
        char *v[] = {"1E+24"};
        Column cols[] = {{"N", COL_N, v}};
        CHECK(br_write_dbf(path, cols, 1, 1, "cp850", 850, msg, sizeof msg) == 0);
        CHECK(dbf_open(path, &d));
        CHECK(d.type[0] == 'C');
        free(d.raw);
    }
    {   /* reduz decimais para caber em 19 posicoes (arredonda) */
        char *v[] = {"123456789012.123456789"};
        Column cols[] = {{"N", COL_N, v}};
        CHECK(br_write_dbf(path, cols, 1, 1, "cp850", 850, msg, sizeof msg) == 0);
        CHECK(dbf_open(path, &d));
        CHECK(d.type[0] == 'N' && d.width[0] == 19 && d.dec[0] == 6);
        f = dbf_field(&d, 0, 0); CHECK_STR(f, "123456789012.123457"); free(f);
        free(d.raw);
    }
    {   /* formatos possiveis de numero em texto: ".5", expoente, negativos */
        char *v[] = {".5", "-1.5E+2", "3E-3", "0", "999.99"};
        Column cols[] = {{"N", COL_N, v}};
        CHECK(br_write_dbf(path, cols, 1, 5, "cp850", 850, msg, sizeof msg) == 0);
        CHECK(dbf_open(path, &d));
        CHECK(d.type[0] == 'N' && d.width[0] == 8 && d.dec[0] == 3);
        f = dbf_field(&d, 0, 0); CHECK_STR(f, "   0.500"); free(f);
        f = dbf_field(&d, 1, 0); CHECK_STR(f, "-150.000"); free(f);
        free(d.raw);
    }
    {   /* arredondamento para o par nos empates, e vai-um: 0.5 -> 0, 1.5 -> 2, 2.5 -> 2, 9.5 -> 10 */
        char *v[] = {"0.5", "1.5", "2.5", "9.5", "123456789012345678.5"};
        Column cols[] = {{"N", COL_N, v}};
        CHECK(br_write_dbf(path, cols, 1, 5, "cp850", 850, msg, sizeof msg) == 0);
        CHECK(dbf_open(path, &d));
        CHECK(d.type[0] == 'N' && d.width[0] == 18 && d.dec[0] == 0);
        f = dbf_field(&d, 0, 0); CHECK_STR(f, "                 0"); free(f);
        f = dbf_field(&d, 1, 0); CHECK_STR(f, "                 2"); free(f);
        f = dbf_field(&d, 2, 0); CHECK_STR(f, "                 2"); free(f);
        f = dbf_field(&d, 3, 0); CHECK_STR(f, "                10"); free(f);
        f = dbf_field(&d, 4, 0); CHECK_STR(f, "123456789012345678"); free(f);
        free(d.raw);
    }
    free(path);
}

static void test_dbf_texto_e_logico(void)
{
    char *path = make_temp_path("fbbridge_t4.dbf"), msg[256];
    Dbf d;
    char *f;
    char longo[301];
    char *v_t[] = {longo}, *v_l[] = {"T"}, *v_l2[] = {NULL};

    memset(longo, 'x', 300);
    longo[300] = '\0';
    {
        Column cols[] = {{"T", COL_C, v_t}};
        CHECK(br_write_dbf(path, cols, 1, 1, "cp850", 850, msg, sizeof msg) == 0);
        CHECK(dbf_open(path, &d));
        CHECK(d.width[0] == 254);
        free(d.raw);
    }
    {
        Column cols[] = {{"L1", COL_L, v_l}, {"L2", COL_L, v_l2}};
        CHECK(br_write_dbf(path, cols, 2, 1, "cp850", 850, msg, sizeof msg) == 0);
        CHECK(dbf_open(path, &d));
        f = dbf_field(&d, 0, 0); CHECK_STR(f, "T"); free(f);
        f = dbf_field(&d, 0, 1); CHECK_STR(f, "?"); free(f);
        free(d.raw);
    }
    {   /* caractere sem equivalente na pagina de codigo vira '?' (japones nao existe em cp850) */
        char *v[] = {"a\xe3\x81\x82" "b"};
        Column cols[] = {{"T", COL_C, v}};
        CHECK(br_write_dbf(path, cols, 1, 1, "cp850", 850, msg, sizeof msg) == 0);
        CHECK(dbf_open(path, &d));
        f = dbf_field(&d, 0, 0); CHECK_STR(f, "a?b"); free(f);
        free(d.raw);
    }
    free(path);
}

static void test_nome_campo(void)
{
    char used[4][11];
    size_t n = 0;
    char *a = br_field_name("SUM(X)", used, &n);
    char *b = br_field_name("SUM(X)", used, &n);
    char *c = br_field_name("1abc", used, &n);
    char *d = br_field_name("COLUNA_MUITO_LONGA", used, &n);
    char *e = br_field_name("", used, &n);
    CHECK_STR(a, "SUM_X_");
    CHECK_STR(b, "SUM_X_1");
    CHECK_STR(c, "C1ABC");
    CHECK_STR(d, "COLUNA_MUI");
    CHECK_STR(e, "C");
    free(a); free(b); free(c); free(d); free(e);
}

static void test_requisicao(void)
{
    char *s;
    Bind b;
    Request req;
    char msg[128];
    /* CODEPAGE depois do USER com acento: a pagina vem no proprio arquivo */
    const char *txt =
        "ACTION=QUERY\r\nUSER=jo\xc6o\r\nPASS=p=1\r\nDSN=host:1544/srv\r\nCODEPAGE=cp850\r\n"
        "MAXROWS=65000\r\nRSP=C:\\T\\ORA1.RSP\r\nOUT=C:\\T\\ORA1.DBF\r\nSQLFILE=C:\\T\\ORA1.SQL\r\n"
        "BIND=C|a\\nb\r\nBIND=N|5.0000000000\r\nBIND=D|20260921\r\nBIND=L|T\r\nBIND=Z|\r\n\x1a";

    s = br_unescape("a\\\\b\\r\\nc"); CHECK_STR(s, "a\\b\r\nc"); free(s);
    s = br_unescape("x\\qy\\"); CHECK_STR(s, "x\\qy\\"); free(s);

    br_parse_bind("N|5.0000000000", &b); CHECK(b.type == 'N'); CHECK_STR(b.value, "5.0000000000"); free(b.value);
    br_parse_bind("C|a\\nb", &b); CHECK(b.type == 'C'); CHECK_STR(b.value, "a\nb"); free(b.value);
    br_parse_bind("Z|", &b); CHECK(b.type == 'Z'); free(b.value);
    br_parse_bind("C|x|y", &b); CHECK_STR(b.value, "x|y"); free(b.value);

    CHECK(br_parse_request((const unsigned char *)txt, strlen(txt), &req, msg, sizeof msg) == 0);
    CHECK_STR(req.action, "QUERY");
    CHECK_STR(req.user, "jo\xc3\xa3o"); /* convertido de cp850 para UTF-8 */
    CHECK_STR(req.pass, "p=1");
    CHECK_STR(req.dsn, "host:1544/srv");
    CHECK_STR(req.rsp, "C:\\T\\ORA1.RSP");
    CHECK_STR(req.out, "C:\\T\\ORA1.DBF");
    CHECK_STR(req.sqlfile, "C:\\T\\ORA1.SQL");
    CHECK_STR(req.maxrows, "65000");
    CHECK_STR(req.codepage, "cp850");
    CHECK(req.cp == 850);
    CHECK(req.nbinds == 5);
    CHECK(req.binds[0].type == 'C' && strcmp(req.binds[0].value, "a\nb") == 0);
    CHECK(req.binds[3].type == 'L' && req.binds[4].type == 'Z');
    br_free_request(&req);

    txt = "ACTION=PING\r\nCODEPAGE=cp999999\r\n";
    CHECK(br_parse_request((const unsigned char *)txt, strlen(txt), &req, msg, sizeof msg) != 0);
    br_free_request(&req);
}

static void test_sql(void)
{
    char *s;
    s = br_clean_sql("select 1 from dual;\r\n"); CHECK_STR(s, "select 1 from dual"); free(s);
    s = br_clean_sql("  select 1 ; ; \r\n"); CHECK_STR(s, "select 1 ;"); free(s);
    s = br_clean_sql("begin null; end;"); CHECK_STR(s, "begin null; end;"); free(s);
    s = br_clean_sql("DECLARE x NUMBER; BEGIN NULL; END;\n"); CHECK_STR(s, "DECLARE x NUMBER; BEGIN NULL; END;"); free(s);
}

static void test_codepage(void)
{
    size_t n;
    char *u = br_to_utf8("\x84\x82", 2, 850, &n); /* cp850: ä é */
    CHECK_STR(u, "\xc3\xa4\xc3\xa9");
    free(u);
    u = br_from_utf8("\xc3\xa7", 2, 850, &n); /* ç */
    CHECK(n == 1 && (unsigned char)u[0] == 0x87);
    free(u);
    CHECK(br_codepage_id("cp850") == 850);
    CHECK(br_codepage_id("CP1252") == 1252);
    CHECK(br_codepage_id("xx") == -1);
    CHECK(br_lang_driver("cp437") == 1 && br_lang_driver("cp850") == 2 && br_lang_driver("cp1252") == 3);
}

static void test_double(void)
{
    char buf[64];
    br_double_text(0.1, 0, buf, sizeof buf); CHECK_STR(buf, "0.1");
    br_double_text(2.5, 0, buf, sizeof buf); CHECK_STR(buf, "2.5");
    br_double_text(0.1f, 1, buf, sizeof buf); CHECK_STR(buf, "0.1");
    br_double_text(1e20, 0, buf, sizeof buf); CHECK_STR(buf, "1e+20");
}

/* Roda a ponte com um banco que nao existe: tem que sair com 0 e escrever ERR no .RSP. */
static int test_exe(const char *exe)
{
    char *req = make_temp_path("FBT1.REQ"), *rsp = make_temp_path("FBT1.RSP");
    char *cmd = br_alloc(strlen(exe) + strlen(req) + 16);
    unsigned char *out;
    size_t n;
    char text[1024];
    FILE *f = fopen(req, "wb");

    if (!f)
        return 1;
    fprintf(f, "ACTION=PING\r\nUSER=x\r\nPASS=y\r\nDSN=127.0.0.1/1:C:\\nada.fdb\r\nCODEPAGE=cp850\r\nRSP=%s\r\n\x1a", rsp);
    fclose(f);
    remove(rsp);
    sprintf(cmd, "\"\"%s\" \"%s\"\"", exe, req);
    CHECK(system(cmd) == 0);
    out = br_read_file(rsp, &n);
    CHECK(out != NULL);
    if (out) {
        snprintf(text, sizeof text, "%s", (char *)out);
        CHECK(strncmp(text, "ERR\r\n", 5) == 0);
        CHECK(strlen(text) > 7); /* tem mensagem */
        printf("resposta: %s", text);
        free(out);
    }
    remove(req);
    remove(rsp);
    free(req); free(rsp); free(cmd);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc > 1) {
        test_exe(argv[1]);
    } else {
        test_dbf_tipos();
        test_dbf_vazio();
        test_dbf_numeros();
        test_dbf_texto_e_logico();
        test_nome_campo();
        test_requisicao();
        test_sql();
        test_codepage();
        test_double();
    }
    printf("%d verificacoes, %d falhas\n", checks, failures);
    return failures ? 1 : 0;
}
