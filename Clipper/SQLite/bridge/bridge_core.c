/* bridge_core.c - ver bridge_core.h */
#include "bridge_core.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#endif

/* ---------------------------------------------------------------- Utilitarios */

void *br_alloc(size_t n)
{
    void *p = malloc(n ? n : 1);
    if (!p) {
        fputs("sqlitebridge: memoria insuficiente\n", stderr);
        exit(2);
    }
    return p;
}

void *br_realloc(void *p, size_t n)
{
    p = realloc(p, n ? n : 1);
    if (!p) {
        fputs("sqlitebridge: memoria insuficiente\n", stderr);
        exit(2);
    }
    return p;
}

char *br_strndup(const char *s, size_t n)
{
    char *r = br_alloc(n + 1);
    memcpy(r, s, n);
    r[n] = '\0';
    return r;
}

char *br_strdup(const char *s)
{
    return br_strndup(s, strlen(s));
}

static FILE *open_utf8(const char *path, const char *mode)
{
#ifdef _WIN32
    /* o caminho vem do arquivo .REQ ja convertido para UTF-8 */
    wchar_t wpath[1024], wmode[8];
    if (!MultiByteToWideChar(CP_UTF8, 0, path, -1, wpath, 1024) ||
        !MultiByteToWideChar(CP_UTF8, 0, mode, -1, wmode, 8))
        return NULL;
    return _wfopen(wpath, wmode);
#else
    return fopen(path, mode);
#endif
}

unsigned char *br_read_file(const char *path, size_t *len)
{
    FILE *f = open_utf8(path, "rb");
    unsigned char *buf = NULL;
    size_t cap = 0, n = 0, got;
    if (!f)
        return NULL;
    do {
        if (n + 4096 + 1 > cap) {
            cap = cap ? cap * 2 : 8192;
            buf = br_realloc(buf, cap);
        }
        got = fread(buf + n, 1, cap - n - 1, f);
        n += got;
    } while (got > 0);
    fclose(f);
    buf[n] = '\0';
    *len = n;
    return buf;
}

int br_write_file(const char *path, const void *data, size_t len)
{
    FILE *f = open_utf8(path, "wb");
    int ok;
    if (!f)
        return 1;
    ok = fwrite(data, 1, len, f) == len;
    if (fclose(f) != 0)
        ok = 0;
    return ok ? 0 : 1;
}

/* ------------------------------------------------------- Paginas de codigo */

static int ieq(const char *a, const char *b)
{
    for (; *a && *b; a++, b++)
        if (tolower((unsigned char)*a) != tolower((unsigned char)*b))
            return 0;
    return *a == *b;
}

int br_codepage_id(const char *name)
{
    char *end;
    long n;
    if (ieq(name, "utf-8") || ieq(name, "utf8"))
        return 65001;
    if (ieq(name, "latin1") || ieq(name, "latin-1") || ieq(name, "iso-8859-1"))
        return 28591;
    if (ieq(name, "ascii"))
        return 20127;
    if (ieq(name, "windows-1252"))
        return 1252;
    /* "cp850", "cp437", "cp1252"... */
    if ((name[0] == 'c' || name[0] == 'C') && (name[1] == 'p' || name[1] == 'P') && name[2]) {
        n = strtol(name + 2, &end, 10);
        if (*end == '\0' && n > 0 && n < 65536)
            return (int)n;
    }
    return -1;
}

#ifdef _WIN32

char *br_to_utf8(const char *s, size_t n, int cp, size_t *outlen)
{
    wchar_t *w;
    char *out;
    int nw, no;
    if (n == 0 || cp == 65001) {
        /* UTF-8 ja e o formato de trabalho */
        out = br_strndup(s, n);
        if (outlen)
            *outlen = n;
        return out;
    }
    nw = MultiByteToWideChar(cp, 0, s, (int)n, NULL, 0);
    w = br_alloc((size_t)(nw + 1) * sizeof(wchar_t));
    nw = nw ? MultiByteToWideChar(cp, 0, s, (int)n, w, nw) : 0;
    no = nw ? WideCharToMultiByte(CP_UTF8, 0, w, nw, NULL, 0, NULL, NULL) : 0;
    out = br_alloc((size_t)no + 1);
    if (no)
        WideCharToMultiByte(CP_UTF8, 0, w, nw, out, no, NULL, NULL);
    out[no] = '\0';
    free(w);
    if (outlen)
        *outlen = (size_t)no;
    return out;
}

char *br_from_utf8(const char *s, size_t n, int cp, size_t *outlen)
{
    wchar_t *w;
    char *out;
    int nw, no;
    if (n == 0 || cp == 65001) {
        out = br_strndup(s, n);
        if (outlen)
            *outlen = n;
        return out;
    }
    nw = MultiByteToWideChar(CP_UTF8, 0, s, (int)n, NULL, 0);
    w = br_alloc((size_t)(nw + 1) * sizeof(wchar_t));
    nw = nw ? MultiByteToWideChar(CP_UTF8, 0, s, (int)n, w, nw) : 0;
    /* sem "best fit": um caractere sem equivalente vira '?', nao outra letra parecida */
    no = nw ? WideCharToMultiByte(cp, WC_NO_BEST_FIT_CHARS, w, nw, NULL, 0, "?", NULL) : 0;
    out = br_alloc((size_t)no + 1);
    if (no)
        WideCharToMultiByte(cp, WC_NO_BEST_FIT_CHARS, w, nw, out, no, "?", NULL);
    out[no] = '\0';
    free(w);
    if (outlen)
        *outlen = (size_t)no;
    return out;
}

#else /* fora do Windows: so ASCII e Latin-1 (suficiente para compilar e testar) */

char *br_to_utf8(const char *s, size_t n, int cp, size_t *outlen)
{
    char *out = br_alloc(n * 2 + 1);
    size_t o = 0, i;
    for (i = 0; i < n; i++) {
        unsigned char c = (unsigned char)s[i];
        if (c < 0x80 || cp == 65001)
            out[o++] = (char)c;
        else {
            out[o++] = (char)(0xC0 | (c >> 6));
            out[o++] = (char)(0x80 | (c & 0x3F));
        }
    }
    out[o] = '\0';
    if (outlen)
        *outlen = o;
    return out;
}

char *br_from_utf8(const char *s, size_t n, int cp, size_t *outlen)
{
    char *out = br_alloc(n + 1);
    size_t o = 0, i = 0;
    while (i < n) {
        unsigned char c = (unsigned char)s[i];
        if (c < 0x80 || cp == 65001) {
            out[o++] = (char)c;
            i++;
        } else if ((c & 0xE0) == 0xC0 && i + 1 < n && (cp == 1252 || cp == 28591)) {
            out[o++] = (char)(((c & 0x1F) << 6) | (s[i + 1] & 0x3F));
            i += 2;
        } else {
            out[o++] = '?';
            i++;
            while (i < n && ((unsigned char)s[i] & 0xC0) == 0x80)
                i++;
        }
    }
    out[o] = '\0';
    if (outlen)
        *outlen = o;
    return out;
}

#endif

/* ---------------------------------------------------------------- Requisicao */

char *br_unescape(const char *s)
{
    char *out = br_alloc(strlen(s) + 1), *o = out;
    while (*s) {
        if (*s == '\\' && s[1]) {
            switch (s[1]) {
            case 'r': *o++ = '\r'; break;
            case 'n': *o++ = '\n'; break;
            case '\\': *o++ = '\\'; break;
            default: *o++ = '\\'; *o++ = s[1]; break; /* sequencia desconhecida fica como esta */
            }
            s += 2;
        } else {
            *o++ = *s++;
        }
    }
    *o = '\0';
    return out;
}

void br_parse_bind(const char *item, Bind *b)
{
    const char *bar = strchr(item, '|');
    const char *valor = bar ? bar + 1 : "";
    size_t tlen = bar ? (size_t)(bar - item) : strlen(item);
    b->type = 'C';
    if (tlen == 1 && strchr("NDLZ", item[0]))
        b->type = item[0];
    b->value = br_unescape(valor);
}

/* Avanca para a proxima linha (CR, LF ou CRLF); devolve o fim da linha atual. */
static const char *line_end(const char *p, const char *end, const char **next)
{
    const char *q = p;
    while (q < end && *q != '\r' && *q != '\n')
        q++;
    *next = q;
    if (q < end) {
        if (*q == '\r' && q + 1 < end && q[1] == '\n')
            (*next) += 2;
        else
            (*next)++;
    }
    return q;
}

static void set_field(char **dst, const char *value, size_t n)
{
    free(*dst);
    *dst = br_strndup(value, n);
}

int br_parse_request(const unsigned char *buf, size_t n, Request *req, char *msg, size_t msgsz)
{
    char *clean = br_alloc(n + 1), *text;
    size_t nclean = 0, i, ntext;
    const char *p, *end, *next, *le;
    char cpname[64] = "cp850";

    memset(req, 0, sizeof *req);
    /* MemoWrit() do Clipper pode terminar o arquivo com Ctrl-Z */
    for (i = 0; i < n; i++)
        if (buf[i] != 0x1A)
            clean[nclean++] = (char)buf[i];

    /*
     * A pagina de codigo vem dentro do proprio arquivo, entao a primeira leitura
     * so olha os bytes ASCII (as chaves sao ASCII) para descobrir o CODEPAGE=...
     */
    p = clean;
    end = clean + nclean;
    while (p < end) {
        char line[128];
        size_t k = 0;
        le = line_end(p, end, &next);
        for (; p < le && k < sizeof line - 1; p++)
            if ((unsigned char)*p < 0x80)
                line[k++] = *p;
        line[k] = '\0';
        if (k >= 9) {
            char head[10];
            memcpy(head, line, 9);
            head[9] = '\0';
            if (ieq(head, "CODEPAGE=")) {
                char *v = line + 9, *e;
                size_t j;
                while (*v && isspace((unsigned char)*v))
                    v++;
                e = v + strlen(v);
                while (e > v && isspace((unsigned char)e[-1]))
                    e--;
                *e = '\0';
                if (*v) {
                    for (j = 0; v[j] && j < sizeof cpname - 1; j++)
                        cpname[j] = (char)tolower((unsigned char)v[j]);
                    cpname[j] = '\0';
                }
            }
        }
        p = next;
    }
    req->codepage = br_strdup(cpname);
    req->cp = br_codepage_id(cpname);
    if (req->cp < 0) {
        snprintf(msg, msgsz, "pagina de codigo desconhecida: %s", cpname);
        free(clean);
        return 1;
    }

    /* ... e a segunda leitura ja usa a pagina de codigo certa (acentos de USER, SQL etc.) */
    text = br_to_utf8(clean, nclean, req->cp, &ntext);
    free(clean);
    p = text;
    end = text + ntext;
    while (p < end) {
        const char *eq;
        le = line_end(p, end, &next);
        eq = memchr(p, '=', (size_t)(le - p));
        if (eq) {
            const char *k0 = p, *k1 = eq;
            char key[32];
            size_t kl, j;
            const char *val = eq + 1;
            size_t vl = (size_t)(le - val);
            while (k0 < k1 && isspace((unsigned char)*k0))
                k0++;
            while (k1 > k0 && isspace((unsigned char)k1[-1]))
                k1--;
            kl = (size_t)(k1 - k0);
            if (kl < sizeof key) {
                for (j = 0; j < kl; j++)
                    key[j] = (char)toupper((unsigned char)k0[j]);
                key[kl] = '\0';
                if (strcmp(key, "BIND") == 0) {
                    char *item = br_strndup(val, vl);
                    req->binds = br_realloc(req->binds, (req->nbinds + 1) * sizeof(Bind));
                    br_parse_bind(item, &req->binds[req->nbinds++]);
                    free(item);
                } else if (strcmp(key, "ACTION") == 0) set_field(&req->action, val, vl);
                else if (strcmp(key, "FILE") == 0) set_field(&req->file, val, vl);
                else if (strcmp(key, "SQLFILE") == 0) set_field(&req->sqlfile, val, vl);
                else if (strcmp(key, "RSP") == 0) set_field(&req->rsp, val, vl);
                else if (strcmp(key, "OUT") == 0) set_field(&req->out, val, vl);
                else if (strcmp(key, "MAXROWS") == 0) set_field(&req->maxrows, val, vl);
            }
        }
        p = next;
    }
    free(text);
    return 0;
}

void br_free_request(Request *req)
{
    size_t i;
    free(req->action); free(req->file);
    free(req->sqlfile); free(req->rsp); free(req->out); free(req->codepage);
    free(req->maxrows);
    for (i = 0; i < req->nbinds; i++)
        free(req->binds[i].value);
    free(req->binds);
    memset(req, 0, sizeof *req);
}

char *br_clean_sql(const char *sql)
{
    size_t n;
    while (*sql && isspace((unsigned char)*sql))
        sql++;
    n = strlen(sql);
    while (n && isspace((unsigned char)sql[n - 1]))
        n--;
    return br_strndup(sql, n);
}

/* ------------------------------------------------------------------ Decimais */

/* Numero em texto: sinal, parte inteira (sem zeros a esquerda) e parte fracionaria. */
typedef struct {
    int neg;
    char *ip;
    char *fp;
} Dec;

static void dec_free(Dec *d)
{
    free(d->ip);
    free(d->fp);
    d->ip = d->fp = NULL;
}

/* Aceita [+-]digitos[.digitos][E[+-]n] e ".5"; NaN/infinito e lixo devolvem 0. */
static int dec_parse(const char *s, Dec *d)
{
    const char *p = s;
    char *mant;
    size_t nm = 0, intlen = 0, ndig;
    long exp = 0, point;
    int seen_point = 0;

    d->ip = d->fp = NULL;
    d->neg = 0;
    while (isspace((unsigned char)*p))
        p++;
    if (*p == '+' || *p == '-')
        d->neg = *p++ == '-';
    mant = br_alloc(strlen(p) + 1);
    for (; *p; p++) {
        if (isdigit((unsigned char)*p)) {
            mant[nm++] = *p;
            if (!seen_point)
                intlen++;
        } else if (*p == '.' && !seen_point) {
            seen_point = 1;
        } else {
            break;
        }
    }
    ndig = nm;
    if (ndig == 0) {
        free(mant);
        return 0;
    }
    if (*p == 'e' || *p == 'E') {
        char *end;
        exp = strtol(p + 1, &end, 10);
        if (end == p + 1)
            goto bad;
        p = end;
        if (exp > 1000 || exp < -1000)
            goto bad;
    }
    while (isspace((unsigned char)*p))
        p++;
    if (*p)
        goto bad;

    /* posicao da virgula dentro de mant depois de aplicar o expoente */
    point = (long)intlen + exp;
    if (point <= 0) {
        size_t z = (size_t)(-point);
        d->ip = br_strdup("0");
        d->fp = br_alloc(z + ndig + 1);
        memset(d->fp, '0', z);
        memcpy(d->fp + z, mant, ndig);
        d->fp[z + ndig] = '\0';
    } else if ((size_t)point >= ndig) {
        size_t z = (size_t)point - ndig;
        d->ip = br_alloc((size_t)point + 1);
        memcpy(d->ip, mant, ndig);
        memset(d->ip + ndig, '0', z);
        d->ip[point] = '\0';
        d->fp = br_strdup("");
    } else {
        d->ip = br_strndup(mant, (size_t)point);
        d->fp = br_strndup(mant + point, ndig - (size_t)point);
    }
    /* zeros a esquerda da parte inteira */
    {
        char *ip = d->ip;
        size_t skip = 0, len = strlen(ip);
        while (skip + 1 < len && ip[skip] == '0')
            skip++;
        if (skip)
            memmove(ip, ip + skip, len - skip + 1);
    }
    free(mant);
    return 1;
bad:
    free(mant);
    return 0;
}

/* Formata com exatamente "dec" casas; arredonda para o par mais proximo nos empates (como o Decimal do Python). */
static char *dec_format(const Dec *d, size_t dec)
{
    size_t il = strlen(d->ip), fl = strlen(d->fp), total, k;
    char *digits, *out, *o;
    int up = 0;

    /* digits = parte inteira + as "dec" primeiras casas (com zeros se faltar) */
    total = il + dec;
    digits = br_alloc(total + 2);
    memcpy(digits, d->ip, il);
    for (k = 0; k < dec; k++)
        digits[il + k] = k < fl ? d->fp[k] : '0';
    digits[total] = '\0';

    if (fl > dec) {
        const char *rest = d->fp + dec;
        if (rest[0] > '5') {
            up = 1;
        } else if (rest[0] == '5') {
            const char *q = rest + 1;
            while (*q == '0')
                q++;
            up = *q != '\0' || ((digits[total - 1] - '0') & 1);
        }
    }
    if (up) {
        size_t j = total;
        while (j > 0) {
            if (digits[j - 1] == '9') {
                digits[j - 1] = '0';
                j--;
            } else {
                digits[j - 1]++;
                break;
            }
        }
        if (j == 0) { /* o vai-um passou da primeira casa: 999 -> 1000 */
            memmove(digits + 1, digits, total + 1);
            digits[0] = '1';
            total++;
        }
    }

    out = o = br_alloc(total + 3);
    if (d->neg)
        *o++ = '-';
    memcpy(o, digits, total - dec);
    o += total - dec;
    if (dec) {
        *o++ = '.';
        memcpy(o, digits + total - dec, dec);
        o += dec;
    }
    *o = '\0';
    free(digits);
    return out;
}

void br_double_text(double v, int is_float, char *out, size_t outsz)
{
    int prec;
    for (prec = 1; prec <= 17; prec++) {
        snprintf(out, outsz, "%.*g", prec, v);
        if (is_float ? (strtod(out, NULL) == v || (float)strtod(out, NULL) == (float)v)
                     : strtod(out, NULL) == v)
            break;
    }
}

/* ---------------------------------------------------------------------- DBF */

int br_lang_driver(const char *codepage)
{
    if (strcmp(codepage, "cp437") == 0)
        return 0x01;
    if (strcmp(codepage, "cp850") == 0)
        return 0x02;
    if (strcmp(codepage, "cp1252") == 0)
        return 0x03;
    return 0;
}

char *br_field_name(const char *name, char used[][11], size_t *nused)
{
    size_t cap = strlen(name) + 2, n = 0, i;
    char *base = br_alloc(cap + 1), *final;
    const unsigned char *p = (const unsigned char *)name;

    /* cada caractere que nao seja letra/digito ASCII ou '_' vira '_' (um por caractere, nao por byte) */
    for (; *p; p++) {
        if ((*p & 0xC0) == 0x80)
            continue; /* byte de continuacao do UTF-8 */
        if (*p < 0x80 && (isalnum(*p) || *p == '_'))
            base[n++] = (char)toupper(*p);
        else
            base[n++] = '_';
    }
    base[n] = '\0';
    if (n == 0 || isdigit((unsigned char)base[0])) {
        memmove(base + 1, base, n + 1);
        base[0] = 'C';
        n++;
    }
    if (n > 10) {
        base[10] = '\0';
        n = 10;
    }

    final = br_alloc(11);
    strcpy(final, base);
    for (int seq = 1;; seq++) {
        int taken = 0;
        for (i = 0; i < *nused; i++)
            if (strcmp(used[i], final) == 0)
                taken = 1;
        if (!taken)
            break;
        {
            char suf[16];
            size_t keep;
            snprintf(suf, sizeof suf, "%d", seq);
            keep = 10 - strlen(suf);
            if (keep > n)
                keep = n;
            memcpy(final, base, keep);
            strcpy(final + keep, suf);
        }
    }
    strcpy(used[(*nused)++], final);
    free(base);
    return final;
}

typedef struct {
    char name[11];
    char type;
    size_t width;
    size_t dec;
    unsigned char *data; /* nrows * width bytes */
} Field;

/*
 * Formata a coluna numerica: todos os valores usam o mesmo numero de decimais (o
 * maior encontrado), como exige o campo N do DBF. Se estourar 19 posicoes, sacrifica
 * casas decimais (arredonda) ate caber. Devolve 0 se nem a parte inteira couber
 * (o chamador usa campo caractere).
 */
static int build_numeric(const Column *col, size_t nrows, Field *f)
{
    Dec *decs = br_alloc((nrows ? nrows : 1) * sizeof(Dec));
    char *ok = br_alloc(nrows ? nrows : 1);
    size_t r, dec = 0, width;
    int result = 0;

    for (r = 0; r < nrows; r++) {
        ok[r] = col->vals[r] && dec_parse(col->vals[r], &decs[r]);
        if (ok[r] && strlen(decs[r].fp) > dec)
            dec = strlen(decs[r].fp);
    }
    for (;;) {
        char **texts = br_alloc((nrows ? nrows : 1) * sizeof(char *));
        width = 1;
        for (r = 0; r < nrows; r++) {
            texts[r] = ok[r] ? dec_format(&decs[r], dec) : NULL;
            if (texts[r] && strlen(texts[r]) > width)
                width = strlen(texts[r]);
        }
        if (width <= DBF_MAX_NUM) {
            f->type = 'N';
            f->width = width;
            f->dec = dec;
            f->data = br_alloc(nrows * width + 1);
            for (r = 0; r < nrows; r++) {
                /* alinhado a direita; NULL vira brancos */
                size_t len = texts[r] ? strlen(texts[r]) : 0;
                memset(f->data + r * width, ' ', width);
                if (len)
                    memcpy(f->data + r * width + (width - len), texts[r], len);
            }
            result = 1;
        }
        for (r = 0; r < nrows; r++)
            free(texts[r]);
        free(texts);
        if (result || dec == 0)
            break;
        dec--;
    }
    for (r = 0; r < nrows; r++)
        if (ok[r])
            dec_free(&decs[r]);
    free(decs);
    free(ok);
    return result;
}

/*
 * Campo caractere: a largura e medida em bytes ja na pagina de codigo do Clipper (um
 * "a" com til ocupa 1 byte em cp850). Caracteres sem equivalente viram '?'.
 */
static void build_char(const Column *col, size_t nrows, int cp, Field *f)
{
    char **raw = br_alloc((nrows ? nrows : 1) * sizeof(char *));
    size_t *len = br_alloc((nrows ? nrows : 1) * sizeof(size_t)), r, width = 0;

    for (r = 0; r < nrows; r++) {
        if (col->vals[r]) {
            raw[r] = br_from_utf8(col->vals[r], strlen(col->vals[r]), cp, &len[r]);
        } else {
            raw[r] = br_strdup("");
            len[r] = 0;
        }
        if (len[r] > width)
            width = len[r];
    }
    if (width == 0)
        width = 1;
    if (width > DBF_MAX_CHAR)
        width = DBF_MAX_CHAR;
    f->type = 'C';
    f->width = width;
    f->dec = 0;
    f->data = br_alloc(nrows * width + 1);
    for (r = 0; r < nrows; r++) {
        size_t n = len[r] < width ? len[r] : width;
        memset(f->data + r * width, ' ', width);
        memcpy(f->data + r * width, raw[r], n);
        free(raw[r]);
    }
    free(raw);
    free(len);
}

static void put_le(unsigned char *p, unsigned long v, int bytes)
{
    int i;
    for (i = 0; i < bytes; i++)
        p[i] = (unsigned char)((v >> (8 * i)) & 0xFF);
}

int br_write_dbf(const char *path, const Column *cols, size_t ncols, size_t nrows,
                 const char *codepage, int cp, char *msg, size_t msgsz)
{
    Field *fields = br_alloc((ncols ? ncols : 1) * sizeof(Field));
    char (*used)[11] = br_alloc((ncols ? ncols : 1) * 11);
    size_t nused = 0, c, r, reclen = 1, hdrlen, total, pos;
    unsigned char *out;
    time_t now = time(NULL);
    struct tm *tm = localtime(&now);
    int rc = 0;

    for (c = 0; c < ncols; c++) {
        Field *f = &fields[c];
        char *nm = br_field_name(cols[c].name, used, &nused);
        strcpy(f->name, nm);
        free(nm);
        f->data = NULL;

        if (cols[c].kind == COL_N && build_numeric(&cols[c], nrows, f)) {
            /* pronto */
        } else if (cols[c].kind == COL_D) {
            /* o campo D do Clipper nao guarda hora */
            f->type = 'D';
            f->width = 8;
            f->dec = 0;
            f->data = br_alloc(nrows * 8 + 1);
            for (r = 0; r < nrows; r++) {
                if (cols[c].vals[r])
                    memcpy(f->data + r * 8, cols[c].vals[r], 8);
                else
                    memset(f->data + r * 8, ' ', 8);
            }
        } else if (cols[c].kind == COL_L) {
            /* "?" e o logico nao inicializado do dBase */
            f->type = 'L';
            f->width = 1;
            f->dec = 0;
            f->data = br_alloc(nrows + 1);
            for (r = 0; r < nrows; r++)
                f->data[r] = cols[c].vals[r] ? (cols[c].vals[r][0] == 'T' ? 'T' : 'F') : '?';
        } else {
            /* texto; tambem o destino do numero que nao coube em N(19) */
            build_char(&cols[c], nrows, cp, f);
        }
        reclen += f->width;
    }

    hdrlen = 32 + 32 * ncols + 1; /* cabecalho + descritores + terminador 0x0D */
    if (reclen > 0xFFFF || hdrlen > 0xFFFF || nrows > 0xFFFFFFFFul) {
        snprintf(msg, msgsz, "resultado grande demais para o formato DBF");
        rc = 1;
        goto done;
    }

    total = hdrlen + nrows * reclen + 1;
    out = br_alloc(total);
    memset(out, 0, hdrlen);
    out[0] = 0x03; /* dBase III sem memo */
    out[1] = (unsigned char)(tm ? tm->tm_year : 0);
    out[2] = (unsigned char)(tm ? tm->tm_mon + 1 : 1);
    out[3] = (unsigned char)(tm ? tm->tm_mday : 1);
    put_le(out + 4, (unsigned long)nrows, 4);
    put_le(out + 8, (unsigned long)hdrlen, 2);
    put_le(out + 10, (unsigned long)reclen, 2);
    out[29] = (unsigned char)br_lang_driver(codepage); /* pagina de codigo dos textos */

    for (c = 0; c < ncols; c++) {
        unsigned char *d = out + 32 + 32 * c;
        memcpy(d, fields[c].name, strlen(fields[c].name)); /* resto ja e 0x00 */
        d[11] = (unsigned char)fields[c].type;
        d[16] = (unsigned char)fields[c].width;
        d[17] = (unsigned char)fields[c].dec;
    }
    out[hdrlen - 1] = 0x0D;

    pos = hdrlen;
    for (r = 0; r < nrows; r++) {
        out[pos++] = ' '; /* espaco = registro nao apagado */
        for (c = 0; c < ncols; c++) {
            memcpy(out + pos, fields[c].data + r * fields[c].width, fields[c].width);
            pos += fields[c].width;
        }
    }
    out[pos++] = 0x1A; /* marcador de fim de arquivo */

    if (br_write_file(path, out, pos) != 0) {
        snprintf(msg, msgsz, "nao foi possivel gravar %s", path);
        rc = 1;
    }
    free(out);
done:
    for (c = 0; c < ncols; c++)
        free(fields[c].data);
    free(fields);
    free(used);
    return rc;
}

/* ---------------------------------------------------------------------- .RSP */

int br_write_response(const char *path, int cp, const char *const *lines, size_t nlines)
{
    size_t i, cap = 16, n = 0, olen;
    char *text, *conv;
    int rc;
    for (i = 0; i < nlines; i++)
        cap += strlen(lines[i]) + 2;
    text = br_alloc(cap);
    for (i = 0; i < nlines; i++) {
        size_t l = strlen(lines[i]);
        memcpy(text + n, lines[i], l);
        n += l;
        text[n++] = '\r';
        text[n++] = '\n';
    }
    conv = br_from_utf8(text, n, cp, &olen);
    rc = br_write_file(path, conv, olen);
    free(text);
    free(conv);
    return rc;
}
