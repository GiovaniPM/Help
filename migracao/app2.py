import re
import sqlite3
import threading
import unicodedata
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

APP_TITLE = "Registro e Acompanhamento de Incidentes de Migracao"
DB_PATH = Path(__file__).resolve().parent / "incidentes_migracao.db"

AMBIENTES = ["DEV", "QA", "HML", "PRD", "DR"]
FASES = ["Planejamento", "Pre-cutover", "Cutover", "Validacao", "Hypercare", "Rollback", "Encerramento"]
TIPOS = ["Aplicacao", "Banco de Dados", "Infraestrutura", "Rede/DNS", "Autenticacao/Certificado", "Integracao/API", "Batch/Job", "Performance", "Seguranca", "Dados", "Comunicacao", "Outro"]
SEVERIDADES = ["S1 - Critico", "S2 - Alto", "S3 - Medio", "S4 - Baixo"]
PRIORIDADES = ["P1 - Imediata", "P2 - Alta", "P3 - Normal", "P4 - Baixa"]
STATUS = ["Novo", "Em analise", "Mitigado", "Em correcao", "Aguardando terceiro", "Aguardando negocio", "Resolvido", "Encerrado", "Cancelado"]
IMPACTOS = ["Indisponibilidade total", "Indisponibilidade parcial", "Degradacao", "Erro funcional", "Atraso operacional", "Sem impacto ao usuario", "Risco de compliance", "Risco de seguranca"]
SIM_NAO = ["Sim", "Nao", "N/A"]
COMUNICACOES = ["Nao iniciado", "Comunicado inicial enviado", "Atualizacao enviada", "Comunicado de resolucao enviado", "N/A"]
TIMES = ["Aplicacao", "Infraestrutura", "Banco de Dados", "Redes", "Seguranca", "AMS/Suporte", "Integracao", "Negocio", "Fornecedor", "Projeto", "Outro"]
OPEN_STATUS = ["Novo", "Em analise", "Mitigado", "Em correcao", "Aguardando terceiro", "Aguardando negocio"]
CLOSED_STATUS = ["Resolvido", "Encerrado"]

SEV_COLORS = {"S1 - Critico": "#d64545", "S2 - Alto": "#e8833a", "S3 - Medio": "#e3b341", "S4 - Baixo": "#4c9a6a"}
SEV_BADGE = {"S1 - Critico": "red", "S2 - Alto": "orange", "S3 - Medio": "yellow", "S4 - Baixo": "green"}
SEV_ICON = {"S1 - Critico": "🔴", "S2 - Alto": "🟠", "S3 - Medio": "🟡", "S4 - Baixo": "🟢"}

DT_FMT_DB = "%Y-%m-%d %H:%M:%S"
DT_FMT_BR = "%d/%m/%Y %H:%M"
DT_STEP = timedelta(minutes=5)
NOVO = "__novo__"

# Campo no banco -> coluna exibida/exportada (a ordem define COLUMNS e o INSERT).
FIELD_MAP = {
    "id": "ID",
    "data_abertura": "Data/Hora Abertura",
    "ambiente": "Ambiente",
    "sistema": "Sistema/Aplicacao",
    "componente": "Componente/Interface",
    "fase": "Fase da Migracao",
    "tipo": "Tipo",
    "severidade": "Severidade",
    "prioridade": "Prioridade",
    "status": "Status",
    "impacto": "Impacto",
    "descricao": "Sintoma/Descricao",
    "causa": "Causa Provavel",
    "responsavel": "Responsavel",
    "time_responsavel": "Time Responsavel",
    "fornecedor": "Fornecedor/Parceiro",
    "mitigacao": "Acao Imediata/Mitigacao",
    "proximos_passos": "Proximos Passos",
    "sla": "SLA Alvo (h)",
    "prazo": "Prazo",
    "data_resolucao": "Data/Hora Resolucao",
    "evidencia": "Evidencia/Link",
    "dependencias": "Dependencias",
    "comunicacao": "Comunicacao",
    "rca_necessario": "RCA Necessario?",
    "rca_entregue": "RCA Entregue?",
    "licoes": "Licoes Aprendidas",
    "ultima_atualizacao": "Ultima Atualizacao",
    "observacoes": "Observacoes",
}
DB_FIELDS = list(FIELD_MAP)
DATE_FIELDS = ["data_abertura", "prazo", "data_resolucao", "ultima_atualizacao"]

COLUMNS = [
    "ID", "Data/Hora Abertura", "Ambiente", "Sistema/Aplicacao", "Componente/Interface",
    "Fase da Migracao", "Tipo", "Severidade", "Prioridade", "Status", "Impacto", "Sintoma/Descricao",
    "Causa Provavel", "Responsavel", "Time Responsavel", "Fornecedor/Parceiro", "Acao Imediata/Mitigacao",
    "Proximos Passos", "SLA Alvo (h)", "Prazo", "Data/Hora Resolucao", "Duracao (h)", "Aging Aberto (h)",
    "Evidencia/Link", "Dependencias", "Comunicacao", "RCA Necessario?", "RCA Entregue?", "Licoes Aprendidas",
    "Ultima Atualizacao", "Observacoes"
]

st.set_page_config(page_title="Incidentes de Migracao", page_icon="🚨", layout="wide")

CSS = """
<style>
.app-header {
    padding: 18px 24px; border-radius: 14px; margin-bottom: 8px;
    background: linear-gradient(135deg, #1f3b73 0%, #3a6fd8 100%); color: #fff;
}
.app-header h1 { color: #fff; font-size: 1.55rem; margin: 0; padding: 0; }
.app-header p { color: rgba(255,255,255,.85); margin: 4px 0 0 0; font-size: .92rem; }
[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,.25); border-radius: 12px;
    padding: 12px 16px; background: rgba(128,128,128,.06);
}
[data-testid="stMetricValue"] { font-size: 1.8rem; }
.section-title { font-weight: 600; font-size: 1.02rem; margin-bottom: .25rem; }
</style>
"""


# --------------------------------------------------------------------------- #
# Utilitarios
# --------------------------------------------------------------------------- #
def is_missing(value):
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def clean_text(value):
    return "" if is_missing(value) else str(value).strip()


def to_float(value, default):
    if is_missing(value) or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


ISO_RE = re.compile(r"^\s*\d{4}-\d{1,2}-\d{1,2}")


def parse_dt(value):
    """Converte para datetime sem segundos; datas ISO (AAAA-MM-DD) nao usam dayfirst."""
    if is_missing(value):
        return None
    if isinstance(value, datetime):
        return pd.Timestamp(value).to_pydatetime().replace(microsecond=0)
    text = str(value).strip()
    if not text:
        return None
    parsed = pd.to_datetime(text, dayfirst=not ISO_RE.match(text), errors="coerce")
    return None if pd.isna(parsed) else parsed.to_pydatetime().replace(microsecond=0)


def fmt_dt(value, fmt="%d/%m/%Y %H:%M:%S"):
    parsed = parse_dt(value)
    return parsed.strftime(fmt) if parsed else ""


def db_dt(value):
    return value.strftime(DT_FMT_DB) if value else None


def option_index(options, value, default=0):
    return options.index(value) if value in options else default


def normalize_header(text):
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text).strip().lower()


def flash(message, icon="✅"):
    st.session_state["_flash"] = (message, icon)


def show_flash():
    if "_flash" in st.session_state:
        message, icon = st.session_state.pop("_flash")
        st.toast(message, icon=icon)


def sev_badge(sev):
    return f":{SEV_BADGE.get(sev, 'gray')}-badge[{sev}]" if sev else ""


def status_badge(status):
    if status in CLOSED_STATUS:
        color = "green"
    elif status == "Cancelado":
        color = "gray"
    elif status == "Mitigado":
        color = "violet"
    else:
        color = "blue"
    return f":{color}-badge[{status}]" if status else ""


# --------------------------------------------------------------------------- #
# Banco de dados
# --------------------------------------------------------------------------- #
@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS incidentes (
            id TEXT PRIMARY KEY,
            data_abertura TEXT NOT NULL,
            {", ".join(f"{f} {'REAL' if f == 'sla' else 'TEXT'}" for f in DB_FIELDS[2:])}
        )
    """)
    conn.commit()
    return conn


@st.cache_resource
def get_lock():
    return threading.Lock()


def generate_id(conn):
    rows = conn.execute("SELECT id FROM incidentes WHERE id LIKE 'INC-IRIS-%'").fetchall()
    max_n = 0
    for (inc_id,) in rows:
        try:
            max_n = max(max_n, int(str(inc_id).split("-")[-1]))
        except ValueError:
            pass
    return f"INC-IRIS-{max_n + 1:04d}"


def incident_exists(conn, incident_id):
    return conn.execute("SELECT 1 FROM incidentes WHERE id = ?", (incident_id,)).fetchone() is not None


def save_record(conn, record):
    placeholders = ", ".join(f":{f}" for f in DB_FIELDS)
    with get_lock():
        conn.execute(f"INSERT OR REPLACE INTO incidentes ({', '.join(DB_FIELDS)}) VALUES ({placeholders})",
                     {f: record.get(f) for f in DB_FIELDS})
        conn.commit()


def delete_record(conn, incident_id):
    with get_lock():
        conn.execute("DELETE FROM incidentes WHERE id = ?", (incident_id,))
        conn.commit()


def load_data(conn):
    raw = pd.read_sql_query("SELECT * FROM incidentes", conn)
    if raw.empty:
        return pd.DataFrame(columns=COLUMNS)

    out = raw[DB_FIELDS].rename(columns=FIELD_MAP)
    for field in DATE_FIELDS:
        col = FIELD_MAP[field]
        out[col] = pd.to_datetime(out[col].map(parse_dt), errors="coerce")
    out["SLA Alvo (h)"] = pd.to_numeric(out["SLA Alvo (h)"], errors="coerce")

    now = pd.Timestamp.now()
    abertura = out["Data/Hora Abertura"]
    resolucao = out["Data/Hora Resolucao"]
    is_open = out["Status"].isin(OPEN_STATUS)
    # Fechado sem data de resolucao nao tem duracao conhecida (antes crescia para sempre).
    agora_se_aberto = pd.Series(now, index=out.index).where(is_open)
    fim = resolucao.where(resolucao.notna(), agora_se_aberto)
    out["Duracao (h)"] = ((fim - abertura).dt.total_seconds() / 3600).round(2)
    out["Aging Aberto (h)"] = ((now - abertura).dt.total_seconds() / 3600).round(2).where(is_open, 0)
    return out[COLUMNS].sort_values("Data/Hora Abertura", ascending=False, ignore_index=True)


def overdue_mask(df):
    now = pd.Timestamp.now()
    return df["Status"].isin(OPEN_STATUS) & df["Prazo"].notna() & (df["Prazo"] < now)


def rca_pending_mask(df):
    return df["RCA Necessario?"].eq("Sim") & ~df["RCA Entregue?"].eq("Sim")


def compute_kpis(df):
    open_mask = df["Status"].isin(OPEN_STATUS)
    mttr = df.loc[df["Data/Hora Resolucao"].notna(), "Duracao (h)"].mean()
    aging = df.loc[open_mask, "Aging Aberto (h)"].mean()
    return {
        "Total de Incidentes": len(df),
        "Abertos": int(open_mask.sum()),
        "Criticos S1 abertos": int((open_mask & df["Severidade"].eq("S1 - Critico")).sum()),
        "Altos S2 abertos": int((open_mask & df["Severidade"].eq("S2 - Alto")).sum()),
        "Vencidos": int(overdue_mask(df).sum()),
        "RCA Pendente": int(rca_pending_mask(df).sum()),
        "MTTR (h)": round(float(mttr), 2) if pd.notna(mttr) else 0.0,
        "Aging medio abertos (h)": round(float(aging), 2) if pd.notna(aging) else 0.0,
    }


def build_dashboard_table(df):
    if df.empty:
        return pd.DataFrame({"Indicador": [], "Valor": []})
    return pd.DataFrame(list(compute_kpis(df).items()), columns=["Indicador", "Valor"], dtype=object)


# --------------------------------------------------------------------------- #
# Importacao / exportacao
# --------------------------------------------------------------------------- #
def _style_sheet(ws):
    from openpyxl.styles import Alignment, Font, PatternFill

    fill = PatternFill("solid", fgColor="1F3B73")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = fill
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for col in ws.columns:
        width = max((len(str(c.value)) for c in col if c.value is not None), default=0)
        ws.column_dimensions[col[0].column_letter].width = min(max(12, width + 2), 60)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def to_excel(df):
    output = BytesIO()
    export_df = df.copy()
    for field in DATE_FIELDS:
        export_df[FIELD_MAP[field]] = export_df[FIELD_MAP[field]].apply(fmt_dt)
    listas = pd.DataFrame({
        "Ambiente": pd.Series(AMBIENTES),
        "Fase da Migracao": pd.Series(FASES),
        "Tipo de Incidente": pd.Series(TIPOS),
        "Severidade": pd.Series(SEVERIDADES),
        "Prioridade": pd.Series(PRIORIDADES),
        "Status": pd.Series(STATUS),
        "Impacto": pd.Series(IMPACTOS),
        "Sim/Nao": pd.Series(SIM_NAO),
        "Comunicacao": pd.Series(COMUNICACOES),
        "Time Responsavel": pd.Series(TIMES),
    })
    guia = pd.DataFrame({"Guia de Uso": [
        "Objetivo: centralizar registro, priorizacao, acompanhamento, evidencias, comunicacao e licoes aprendidas de incidentes de migracao.",
        "Como usar: registre cada incidente, acompanhe status, SLA, RCA e evidencias, e utilize o dashboard para governanca executiva e operacional.",
        "RCA: marque Sim para incidentes criticos, recorrentes, producao, compliance, seguranca ou impacto executivo.",
    ]})
    sheets = {
        "Registro de Incidentes": export_df,
        "Listas": listas,
        "Dashboard": build_dashboard_table(df),
        "Guia de Uso": guia,
    }
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, data in sheets.items():
            data.to_excel(writer, index=False, sheet_name=name)
            _style_sheet(writer.sheets[name])
    return output.getvalue()


def read_import_file(uploaded):
    book = pd.ExcelFile(uploaded, engine="openpyxl")
    sheet = "Registro de Incidentes" if "Registro de Incidentes" in book.sheet_names else book.sheet_names[0]
    imp = book.parse(sheet)
    # Aceita cabecalhos com ou sem acento ("Sistema/Aplicação" == "Sistema/Aplicacao").
    by_header = {normalize_header(v): k for k, v in FIELD_MAP.items()}
    imp = imp.rename(columns=lambda c: by_header.get(normalize_header(c), c))
    imp = imp.dropna(how="all")
    return sheet, imp


def import_rows(conn, imp, overwrite):
    inseridos = atualizados = ignorados = 0
    erros = []
    for pos, (_, row) in enumerate(imp.iterrows(), start=2):
        try:
            inc_id = clean_text(row.get("id")) or generate_id(conn)
            exists = incident_exists(conn, inc_id)
            if exists and not overwrite:
                ignorados += 1
                continue
            abertura = parse_dt(row.get("data_abertura")) or datetime.now().replace(second=0, microsecond=0)
            sla = to_float(row.get("sla"), 0.0)
            prazo = parse_dt(row.get("prazo")) or abertura + timedelta(hours=sla)
            rec = {f: clean_text(row.get(f)) for f in DB_FIELDS}
            rec.update({
                "id": inc_id,
                "data_abertura": db_dt(abertura),
                "sla": sla,
                "prazo": db_dt(prazo),
                "data_resolucao": db_dt(parse_dt(row.get("data_resolucao"))),
                "ultima_atualizacao": db_dt(datetime.now()),
            })
            save_record(conn, rec)
            if exists:
                atualizados += 1
            else:
                inseridos += 1
        except Exception as exc:  # noqa: BLE001 - reporta a linha e segue com as demais
            erros.append(f"Linha {pos}: {exc}")
    return inseridos, atualizados, ignorados, erros


def seed_examples(conn):
    if conn.execute("SELECT COUNT(*) FROM incidentes").fetchone()[0] > 0:
        return
    examples = [
        ("INC-IRIS-0001", "2026-07-10 09:00:00", "PRD", "<Sistema>", "<Interface/Componente>", "Cutover", "Integracao/API", "S2 - Alto", "P2 - Alta", "Em correcao", "Degradacao", "Exemplo: falha intermitente durante validacao pos-cutover.", "Em investigacao", "<Nome>", "Aplicacao", "<Fornecedor>", "Mitigacao temporaria aplicada/pendente", "Executar analise tecnica e atualizar stakeholders", 4, "2026-07-10 13:00:00", None, "<Link evidencia>", "<Dependencias>", "Comunicado inicial enviado", "Sim", "Nao", "", "2026-07-10 10:00:00", "Linha de exemplo - substituir ou remover"),
        ("INC-IRIS-0002", "2026-07-10 10:30:00", "QA", "<Sistema>", "<Job/Batch>", "Validacao", "Batch/Job", "S3 - Medio", "P3 - Normal", "Mitigado", "Atraso operacional", "Exemplo: job de validacao executou com atraso apos alteracao de agendamento.", "Dependencia de janela de execucao", "<Nome>", "AMS/Suporte", "N/A", "Reexecucao manual realizada", "Monitorar proxima execucao", 8, "2026-07-10 18:30:00", "2026-07-10 12:00:00", "<Link evidencia>", "<Dependencias>", "Atualizacao enviada", "Nao", "N/A", "Registrar janela recomendada para proximos cutovers", "2026-07-10 12:05:00", "Linha de exemplo - substituir ou remover"),
    ]
    for rec in examples:
        save_record(conn, dict(zip(DB_FIELDS, rec)))


# --------------------------------------------------------------------------- #
# Graficos
# --------------------------------------------------------------------------- #
def chart_status(df):
    data = df["Status"].value_counts().reindex(STATUS, fill_value=0).rename_axis("Status").reset_index(name="Qtd")
    data["Situacao"] = data["Status"].map(lambda s: "Aberto" if s in OPEN_STATUS else "Fechado")
    return alt.Chart(data).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("Qtd:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("Status:N", sort=STATUS, title=None),
        color=alt.Color("Situacao:N", title=None, legend=alt.Legend(orient="bottom"),
                        scale=alt.Scale(domain=["Aberto", "Fechado"], range=["#3a6fd8", "#9aa5b1"])),
        tooltip=["Status", "Qtd"],
    ).properties(height=290)


def chart_severidade(df):
    data = df["Severidade"].value_counts().reindex(SEVERIDADES, fill_value=0).rename_axis("Severidade").reset_index(name="Qtd")
    return alt.Chart(data).mark_arc(innerRadius=60, padAngle=0.02).encode(
        theta=alt.Theta("Qtd:Q"),
        color=alt.Color("Severidade:N", title=None, legend=alt.Legend(orient="bottom", columns=2),
                        scale=alt.Scale(domain=SEVERIDADES, range=[SEV_COLORS[s] for s in SEVERIDADES])),
        tooltip=["Severidade", "Qtd"],
    ).properties(height=290)


def chart_tipo(df):
    data = df["Tipo"].value_counts().rename_axis("Tipo").reset_index(name="Qtd")
    return alt.Chart(data).mark_bar(cornerRadiusEnd=4, color="#6c8fd8").encode(
        x=alt.X("Qtd:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("Tipo:N", sort="-x", title=None),
        tooltip=["Tipo", "Qtd"],
    ).properties(height=290)


def chart_heatmap(df):
    heat = pd.crosstab(df["Ambiente"], df["Severidade"]).reindex(index=AMBIENTES, columns=SEVERIDADES, fill_value=0)
    data = heat.stack().rename("Qtd").reset_index()
    base = alt.Chart(data).encode(
        x=alt.X("Severidade:N", sort=SEVERIDADES, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Ambiente:N", sort=AMBIENTES, title=None),
    )
    rect = base.mark_rect(cornerRadius=4).encode(
        color=alt.Color("Qtd:Q", scale=alt.Scale(scheme="orangered"), legend=None),
        tooltip=["Ambiente", "Severidade", "Qtd"],
    )
    text = base.mark_text(fontWeight="bold").encode(
        text="Qtd:Q",
        color=alt.condition(alt.datum.Qtd > max(1, int(data["Qtd"].max()) / 2), alt.value("white"), alt.value("#333")),
    )
    return (rect + text).properties(height=260)


def chart_timeline(df):
    abertos = df["Data/Hora Abertura"].dropna().dt.floor("D").value_counts().rename("Abertos")
    resolvidos = df["Data/Hora Resolucao"].dropna().dt.floor("D").value_counts().rename("Resolvidos")
    data = pd.concat([abertos, resolvidos], axis=1).fillna(0).sort_index()
    data = data.rename_axis("Dia").reset_index().melt("Dia", var_name="Evento", value_name="Qtd")
    return alt.Chart(data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("yearmonthdate(Dia):O", title=None, axis=alt.Axis(format="%d/%m", labelAngle=0)),
        xOffset="Evento:N",
        y=alt.Y("Qtd:Q", title=None, axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("Evento:N", title=None, legend=alt.Legend(orient="bottom"),
                        scale=alt.Scale(domain=["Abertos", "Resolvidos"], range=["#d64545", "#4c9a6a"])),
        tooltip=[alt.Tooltip("Dia:T", format="%d/%m/%Y"), "Evento", "Qtd"],
    ).properties(height=260)


# --------------------------------------------------------------------------- #
# Tabelas
# --------------------------------------------------------------------------- #
def table_config():
    dt_col = st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")
    hours = st.column_config.NumberColumn(format="%.1f h")
    return {
        "Data/Hora Abertura": dt_col,
        "Prazo": dt_col,
        "Data/Hora Resolucao": dt_col,
        "Ultima Atualizacao": dt_col,
        "SLA Alvo (h)": hours,
        "Duracao (h)": hours,
        "Aging Aberto (h)": hours,
        "Sintoma/Descricao": st.column_config.TextColumn(width="large"),
    }


def decorate(df):
    """Copia para exibicao com icones de severidade e situacao do prazo."""
    view = df.copy()
    vencido = overdue_mask(df)
    view.insert(1, "Situacao", ["⏰ Vencido" if v else ("Aberto" if s in OPEN_STATUS else "Fechado")
                                for v, s in zip(vencido, df["Status"])])
    view["Severidade"] = df["Severidade"].map(lambda s: f"{SEV_ICON.get(s, '')} {s}".strip() if s else "")
    return view


# --------------------------------------------------------------------------- #
# Paginas
# --------------------------------------------------------------------------- #
def page_dashboard():
    conn = get_conn()
    df = load_data(conn)
    if df.empty:
        st.info("Nenhum incidente registrado ainda. Use **Novo/Editar Incidente** ou carregue os exemplos no menu lateral.", icon="ℹ️")
        return

    amb = st.pills("Ambiente", AMBIENTES, selection_mode="multi", key="dash_amb",
                   help="Sem selecao = todos os ambientes")
    if amb:
        df = df[df["Ambiente"].isin(amb)]
    if df.empty:
        st.warning("Nenhum incidente para os ambientes selecionados.")
        return

    m = compute_kpis(df)
    r1 = st.columns(4)
    r1[0].metric("Total de incidentes", m["Total de Incidentes"])
    r1[1].metric("Abertos", m["Abertos"])
    r1[2].metric("🔴 Criticos S1 abertos", m["Criticos S1 abertos"])
    r1[3].metric("🟠 Altos S2 abertos", m["Altos S2 abertos"])
    r2 = st.columns(4)
    r2[0].metric("⏰ Vencidos", m["Vencidos"])
    r2[1].metric("RCA pendente", m["RCA Pendente"])
    r2[2].metric("MTTR", f"{m['MTTR (h)']:.1f} h", help="Tempo medio de resolucao dos incidentes com data de resolucao")
    r2[3].metric("Aging medio (abertos)", f"{m['Aging medio abertos (h)']:.1f} h")

    c1, c2, c3 = st.columns(3)
    for col, title, chart in [(c1, "Por status", chart_status), (c2, "Por severidade", chart_severidade), (c3, "Por tipo", chart_tipo)]:
        with col.container(border=True):
            st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
            st.altair_chart(chart(df), width="stretch")

    c4, c5 = st.columns([1, 1])
    with c4.container(border=True):
        st.markdown("<div class='section-title'>Heatmap Ambiente x Severidade</div>", unsafe_allow_html=True)
        st.altair_chart(chart_heatmap(df), width="stretch")
    with c5.container(border=True):
        st.markdown("<div class='section-title'>Abertos x Resolvidos por dia</div>", unsafe_allow_html=True)
        st.altair_chart(chart_timeline(df), width="stretch")

    atencao = df[overdue_mask(df) | (df["Status"].isin(OPEN_STATUS) & df["Severidade"].isin(SEVERIDADES[:2]))]
    with st.container(border=True):
        st.markdown("<div class='section-title'>⚠️ Requer atencao: vencidos e S1/S2 abertos</div>", unsafe_allow_html=True)
        if atencao.empty:
            st.success("Nenhum incidente vencido ou critico em aberto.", icon="✅")
        else:
            atencao = atencao.assign(_sev=atencao["Severidade"].map(lambda s: option_index(SEVERIDADES, s, 99)))
            atencao = atencao.sort_values(["_sev", "Aging Aberto (h)"], ascending=[True, False]).drop(columns="_sev")
            cols = ["ID", "Situacao", "Severidade", "Status", "Ambiente", "Sistema/Aplicacao", "Responsavel", "Prazo", "Aging Aberto (h)"]
            st.dataframe(decorate(atencao)[cols], hide_index=True, width="stretch", column_config=table_config())


def page_editar():
    conn = get_conn()
    df = load_data(conn)

    if "_goto_incidente" in st.session_state:
        st.session_state["sel_incidente"] = st.session_state.pop("_goto_incidente")
    options = [NOVO] + sorted(df["ID"].dropna().tolist(), reverse=True)
    if st.session_state.get("sel_incidente") not in options:
        st.session_state.pop("sel_incidente", None)
    labels = {r["ID"]: f"{r['ID']}  ·  {clean_text(r['Sistema/Aplicacao']) or 'sem sistema'}  ·  {r['Status']}" for _, r in df.iterrows()}
    labels[NOVO] = "➕ Novo incidente"

    selected = st.selectbox("Selecione um incidente para editar ou crie um novo", options,
                            format_func=lambda v: labels.get(v, v), key="sel_incidente")
    is_new = selected == NOVO
    current = {} if is_new else df.loc[df["ID"] == selected].iloc[0].to_dict()

    nonce = st.session_state.setdefault("_form_nonce", 0)

    def k(name):
        return f"form:{selected}:{nonce}:{name}"

    def txt(col):
        return clean_text(current.get(col))

    if is_new:
        incident_id = generate_id(conn)
        now_default = st.session_state.setdefault(k("_now"), datetime.now().replace(second=0, microsecond=0))
    else:
        incident_id = selected
        now_default = datetime.now().replace(second=0, microsecond=0)
        vencido = bool(overdue_mask(df.loc[df["ID"] == selected]).iloc[0])
        badges = [sev_badge(current.get("Severidade")), status_badge(current.get("Status"))]
        if vencido:
            badges.append(":red-badge[⏰ Vencido]")
        if current.get("RCA Necessario?") == "Sim" and current.get("RCA Entregue?") != "Sim":
            badges.append(":violet-badge[RCA pendente]")
        aging = current.get("Aging Aberto (h)")
        info = f"Aging: **{aging:.1f} h**" if current.get("Status") in OPEN_STATUS and pd.notna(aging) else ""
        upd = fmt_dt(current.get("Ultima Atualizacao"), DT_FMT_BR)
        st.markdown(" ".join(badges) + (f" &nbsp; {info}" if info else "") + (f" &nbsp; · Ultima atualizacao: {upd}" if upd else ""))

    # --- Identificacao ------------------------------------------------------
    with st.container(border=True):
        st.markdown("<div class='section-title'>🆔 Identificacao</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1, 1.3, 1, 1])
        c1.text_input("ID", value=incident_id, disabled=True, key=k("id"))
        abertura = c2.datetime_input("Data/Hora Abertura *", value=parse_dt(current.get("Data/Hora Abertura")) or now_default,
                                     format="DD/MM/YYYY", step=DT_STEP, key=k("abertura"))
        ambiente = c3.selectbox("Ambiente", AMBIENTES, index=option_index(AMBIENTES, current.get("Ambiente")), key=k("ambiente"))
        fase = c4.selectbox("Fase da Migracao", FASES, index=option_index(FASES, current.get("Fase da Migracao")), key=k("fase"))
        c1, c2 = st.columns(2)
        sistema = c1.text_input("Sistema/Aplicacao *", value=txt("Sistema/Aplicacao"), key=k("sistema"))
        componente = c2.text_input("Componente/Interface", value=txt("Componente/Interface"), key=k("componente"))

    # --- Classificacao ------------------------------------------------------
    with st.container(border=True):
        st.markdown("<div class='section-title'>🏷️ Classificacao</div>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        tipo = c1.selectbox("Tipo", TIPOS, index=option_index(TIPOS, current.get("Tipo")), key=k("tipo"))
        severidade = c2.selectbox("Severidade", SEVERIDADES, index=option_index(SEVERIDADES, current.get("Severidade"), 1),
                                  format_func=lambda s: f"{SEV_ICON[s]} {s}", key=k("severidade"))
        prioridade = c3.selectbox("Prioridade", PRIORIDADES, index=option_index(PRIORIDADES, current.get("Prioridade"), 1), key=k("prioridade"))
        impacto = c4.selectbox("Impacto", IMPACTOS, index=option_index(IMPACTOS, current.get("Impacto"), 2), key=k("impacto"))
        status = c5.selectbox("Status", STATUS, index=option_index(STATUS, current.get("Status")), key=k("status"))

    # --- Descricao e tratamento ---------------------------------------------
    with st.container(border=True):
        st.markdown("<div class='section-title'>🛠️ Descricao e tratamento</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        descricao = c1.text_area("Sintoma/Descricao *", value=txt("Sintoma/Descricao"), key=k("descricao"))
        causa = c2.text_area("Causa Provavel", value=txt("Causa Provavel"), key=k("causa"))
        c1, c2, c3 = st.columns(3)
        responsavel = c1.text_input("Responsavel", value=txt("Responsavel"), key=k("responsavel"))
        time_responsavel = c2.selectbox("Time Responsavel", TIMES, index=option_index(TIMES, current.get("Time Responsavel")), key=k("time"))
        fornecedor = c3.text_input("Fornecedor/Parceiro", value=txt("Fornecedor/Parceiro"), key=k("fornecedor"))
        c1, c2 = st.columns(2)
        mitigacao = c1.text_area("Acao Imediata/Mitigacao", value=txt("Acao Imediata/Mitigacao"), key=k("mitigacao"))
        proximos_passos = c2.text_area("Proximos Passos", value=txt("Proximos Passos"), key=k("proximos"))

    # --- Prazos e resolucao -------------------------------------------------
    with st.container(border=True):
        st.markdown("<div class='section-title'>⏱️ SLA, prazo e resolucao</div>", unsafe_allow_html=True)
        sla_atual = to_float(current.get("SLA Alvo (h)"), 4.0)
        prazo_atual = parse_dt(current.get("Prazo"))
        abertura_atual = parse_dt(current.get("Data/Hora Abertura"))
        prazo_auto_default = is_new or (prazo_atual is not None and abertura_atual is not None
                                        and abs(prazo_atual - (abertura_atual + timedelta(hours=sla_atual))) < timedelta(minutes=1))

        c1, c2, c3 = st.columns([1, 1.6, 1.6])
        sla = c1.number_input("SLA Alvo (h)", min_value=0.0, value=sla_atual, step=0.5, key=k("sla"))
        with c2:
            prazo_auto = st.toggle("Prazo = Abertura + SLA", value=prazo_auto_default, key=k("prazo_auto"))
            if prazo_auto:
                prazo = abertura + timedelta(hours=sla)
                st.text_input("Prazo", value=prazo.strftime(DT_FMT_BR), disabled=True, key=k(f"prazo_calc:{prazo.isoformat()}"))
            else:
                prazo = st.datetime_input("Prazo", value=prazo_atual or abertura + timedelta(hours=sla),
                                          format="DD/MM/YYYY", step=DT_STEP, key=k("prazo"))
        with c3:
            res_atual = parse_dt(current.get("Data/Hora Resolucao"))
            res_enabled = st.toggle("Informar Data/Hora Resolucao", value=res_atual is not None, key=k("res_enabled"))
            data_resolucao = st.datetime_input("Data/Hora Resolucao", value=res_atual or now_default, format="DD/MM/YYYY",
                                               step=DT_STEP, disabled=not res_enabled, key=k("resolucao"))
            if not res_enabled:
                data_resolucao = None

        fim = data_resolucao or (datetime.now() if status in OPEN_STATUS else None)
        if fim and fim >= abertura:
            st.caption(f"Duracao {'ate a resolucao' if data_resolucao else 'ate agora'}: **{(fim - abertura).total_seconds() / 3600:.1f} h**")
        if status in CLOSED_STATUS and not data_resolucao:
            st.caption(":orange[Status fechado exige a Data/Hora Resolucao.]")

    # --- RCA, comunicacao e licoes ------------------------------------------
    with st.container(border=True):
        st.markdown("<div class='section-title'>📣 RCA, comunicacao e evidencias</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        rca_necessario = c1.selectbox("RCA Necessario?", SIM_NAO, index=option_index(SIM_NAO, current.get("RCA Necessario?"), 1), key=k("rca_nec"))
        rca_entregue = c2.selectbox("RCA Entregue?", SIM_NAO, index=option_index(SIM_NAO, current.get("RCA Entregue?"), 1), key=k("rca_ent"))
        comunicacao = c3.selectbox("Comunicacao", COMUNICACOES, index=option_index(COMUNICACOES, current.get("Comunicacao")), key=k("comunicacao"))
        sugere_rca = severidade == "S1 - Critico" or ambiente == "PRD" or impacto in ("Risco de compliance", "Risco de seguranca") or tipo == "Seguranca"
        if sugere_rca and rca_necessario != "Sim":
            st.caption(":violet[O criterio sugere RCA: S1, producao, seguranca ou compliance.]")
        c1, c2 = st.columns(2)
        evidencia = c1.text_input("Evidencia/Link", value=txt("Evidencia/Link"), key=k("evidencia"))
        dependencias = c2.text_input("Dependencias", value=txt("Dependencias"), key=k("dependencias"))
        c1, c2 = st.columns(2)
        licoes = c1.text_area("Licoes Aprendidas", value=txt("Licoes Aprendidas"), key=k("licoes"))
        observacoes = c2.text_area("Observacoes", value=txt("Observacoes"), key=k("observacoes"))

    # --- Acoes --------------------------------------------------------------
    erros = []
    if not sistema.strip():
        erros.append("Informe o **Sistema/Aplicacao**.")
    if not descricao.strip():
        erros.append("Informe o **Sintoma/Descricao**.")
    if prazo < abertura:
        erros.append("O **Prazo** nao pode ser anterior a abertura.")
    if data_resolucao and data_resolucao < abertura:
        erros.append("A **Data/Hora Resolucao** nao pode ser anterior a abertura.")
    if status in CLOSED_STATUS and not data_resolucao:
        erros.append(f"Status **{status}** exige a Data/Hora Resolucao.")

    b1, b2, _ = st.columns([1, 1, 4])
    salvar = b1.button("💾 Salvar incidente", type="primary", width="stretch")
    if b2.button("↩️ Descartar alteracoes", width="stretch"):
        st.session_state["_form_nonce"] = nonce + 1
        st.rerun()

    if salvar:
        if erros:
            st.error("Nao foi possivel salvar:\n\n" + "\n".join(f"- {e}" for e in erros), icon="🚫")
        else:
            if is_new and incident_exists(conn, incident_id):
                incident_id = generate_id(conn)  # outro usuario usou o ID enquanto o formulario estava aberto
            save_record(conn, {
                "id": incident_id, "data_abertura": db_dt(abertura), "ambiente": ambiente, "sistema": sistema.strip(),
                "componente": componente.strip(), "fase": fase, "tipo": tipo, "severidade": severidade,
                "prioridade": prioridade, "status": status, "impacto": impacto, "descricao": descricao.strip(),
                "causa": causa.strip(), "responsavel": responsavel.strip(), "time_responsavel": time_responsavel,
                "fornecedor": fornecedor.strip(), "mitigacao": mitigacao.strip(), "proximos_passos": proximos_passos.strip(),
                "sla": sla, "prazo": db_dt(prazo), "data_resolucao": db_dt(data_resolucao), "evidencia": evidencia.strip(),
                "dependencias": dependencias.strip(), "comunicacao": comunicacao, "rca_necessario": rca_necessario,
                "rca_entregue": rca_entregue, "licoes": licoes.strip(), "ultima_atualizacao": db_dt(datetime.now()),
                "observacoes": observacoes.strip(),
            })
            flash(f"Incidente {incident_id} {'criado' if is_new else 'atualizado'} com sucesso.")
            st.session_state["_goto_incidente"] = incident_id
            st.session_state["_form_nonce"] = nonce + 1
            st.rerun()

    if not is_new:
        with st.expander("🗑️ Excluir incidente"):
            st.warning(f"A exclusao de **{selected}** remove o registro do banco SQLite local e nao pode ser desfeita.")
            confirmar = st.checkbox(f"Confirmo que desejo excluir o incidente {selected}", key=k("confirma_exclusao"))
            if st.button("Excluir definitivamente", disabled=not confirmar):
                delete_record(conn, selected)
                flash(f"Incidente {selected} excluido.", icon="🗑️")
                st.session_state["_goto_incidente"] = NOVO
                st.rerun()


def page_consulta():
    conn = get_conn()
    df = load_data(conn)
    if df.empty:
        st.info("Nenhum incidente registrado ainda.", icon="ℹ️")
        return

    with st.container(border=True):
        busca = st.text_input("🔎 Buscar", placeholder="ID, sistema, componente, descricao ou responsavel")
        c1, c2, c3, c4 = st.columns(4)
        f_amb = c1.multiselect("Ambiente", AMBIENTES)
        f_status = c2.multiselect("Status", STATUS)
        f_sev = c3.multiselect("Severidade", SEVERIDADES)
        f_tipo = c4.multiselect("Tipo", TIPOS)
        t1, t2, t3, _ = st.columns([1, 1, 1.3, 2])
        so_abertos = t1.toggle("Somente abertos")
        so_vencidos = t2.toggle("Somente vencidos")
        todas_colunas = t3.toggle("Mostrar todas as colunas")

    mask = pd.Series(True, index=df.index)
    if busca.strip():
        campos = ["ID", "Sistema/Aplicacao", "Componente/Interface", "Sintoma/Descricao", "Responsavel"]
        texto = df[campos].fillna("").astype(str).agg(" ".join, axis=1)
        mask &= texto.str.contains(busca.strip(), case=False, regex=False)
    for col, sel in [("Ambiente", f_amb), ("Status", f_status), ("Severidade", f_sev), ("Tipo", f_tipo)]:
        if sel:
            mask &= df[col].isin(sel)
    if so_abertos:
        mask &= df["Status"].isin(OPEN_STATUS)
    if so_vencidos:
        mask &= overdue_mask(df)
    filtered = df[mask].reset_index(drop=True)

    view = decorate(filtered)
    if not todas_colunas:
        view = view[["ID", "Situacao", "Data/Hora Abertura", "Ambiente", "Sistema/Aplicacao", "Severidade", "Status",
                     "Responsavel", "Prazo", "Duracao (h)", "Aging Aberto (h)", "Sintoma/Descricao"]]

    st.caption(f"{len(filtered)} de {len(df)} incidentes · selecione uma linha para abrir a edicao")
    event = st.dataframe(view, hide_index=True, width="stretch", column_config=table_config(),
                         on_select="rerun", selection_mode="single-row", key="tbl_consulta")

    c1, c2, _ = st.columns([1, 1, 3])
    rows = event.selection.rows
    if c1.button("✏️ Editar selecionado", disabled=not rows, width="stretch"):
        st.session_state["_goto_incidente"] = filtered.loc[rows[0], "ID"]
        st.switch_page(PAGE_EDITAR)
    c2.download_button("⬇️ Baixar filtro (Excel)", data=to_excel(filtered), width="stretch",
                       file_name=f"incidentes_filtrados_{datetime.now():%Y%m%d_%H%M}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def page_rca():
    conn = get_conn()
    df = load_data(conn)
    if df.empty:
        st.info("Nenhum incidente registrado ainda.", icon="ℹ️")
        return

    necessario = df["RCA Necessario?"].eq("Sim")
    entregue = necessario & df["RCA Entregue?"].eq("Sim")
    pendente = rca_pending_mask(df)
    conformidade = (entregue.sum() / necessario.sum() * 100) if necessario.sum() else 100.0

    c = st.columns(4)
    c[0].metric("RCA necessarios", int(necessario.sum()))
    c[1].metric("RCA entregues", int(entregue.sum()))
    c[2].metric("RCA pendentes", int(pendente.sum()))
    c[3].metric("Conformidade", f"{conformidade:.0f}%")
    st.progress(min(conformidade / 100, 1.0))

    cols = ["ID", "Severidade", "Ambiente", "Sistema/Aplicacao", "Status", "Responsavel", "Evidencia/Link", "Ultima Atualizacao", "Observacoes"]
    with st.container(border=True):
        st.markdown("<div class='section-title'>📋 RCA pendentes</div>", unsafe_allow_html=True)
        if pendente.any():
            st.dataframe(decorate(df[pendente])[cols], hide_index=True, width="stretch", column_config=table_config())
        else:
            st.success("Nenhum RCA pendente.", icon="✅")

    sugere = (df["Severidade"].eq("S1 - Critico") | df["Ambiente"].eq("PRD") | df["Tipo"].eq("Seguranca")
              | df["Impacto"].isin(["Risco de compliance", "Risco de seguranca"])) & ~necessario & ~df["Status"].eq("Cancelado")
    with st.container(border=True):
        st.markdown("<div class='section-title'>🔍 Auditoria: candidatos a RCA nao marcados</div>", unsafe_allow_html=True)
        st.caption("Incidentes S1, de producao, seguranca ou compliance com RCA Necessario diferente de Sim.")
        if sugere.any():
            st.dataframe(decorate(df[sugere])[["ID", "Severidade", "Ambiente", "Tipo", "Impacto", "Status", "RCA Necessario?"]],
                         hide_index=True, width="stretch", column_config=table_config())
        else:
            st.success("Todos os incidentes que atendem ao criterio estao com RCA marcado.", icon="✅")

    limite = datetime.now() - timedelta(hours=24)
    parados = df["Status"].isin(OPEN_STATUS) & (df["Ultima Atualizacao"].isna() | (df["Ultima Atualizacao"] < limite))
    with st.container(border=True):
        st.markdown("<div class='section-title'>💤 Abertos sem atualizacao ha mais de 24h</div>", unsafe_allow_html=True)
        if parados.any():
            st.dataframe(decorate(df[parados])[["ID", "Severidade", "Status", "Responsavel", "Ultima Atualizacao", "Aging Aberto (h)"]],
                         hide_index=True, width="stretch", column_config=table_config())
        else:
            st.success("Todos os incidentes abertos foram atualizados nas ultimas 24h.", icon="✅")

    st.caption("**Criterio sugerido:** marcar RCA como necessario para incidentes criticos, recorrentes, producao, compliance, seguranca ou acionamento executivo.")


def page_import_export():
    conn = get_conn()
    df = load_data(conn)
    c1, c2 = st.columns(2)

    with c1.container(border=True):
        st.markdown("<div class='section-title'>⬇️ Exportar</div>", unsafe_allow_html=True)
        st.caption("Excel com as abas Registro de Incidentes, Listas, Dashboard e Guia de Uso.")
        st.download_button("Baixar Excel completo", data=to_excel(df), type="primary", width="stretch",
                           file_name=f"Planilha_Acompanhamento_Incidentes_Migracao_{datetime.now():%Y%m%d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.download_button("Baixar CSV", data=df.to_csv(index=False, sep=";").encode("utf-8-sig"), width="stretch",
                           file_name=f"incidentes_migracao_{datetime.now():%Y%m%d}.csv", mime="text/csv")

    with c2.container(border=True):
        st.markdown("<div class='section-title'>⬆️ Importar</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Planilha original ou exportada por este app", type=["xlsx"])
        modo = st.radio("Quando o ID ja existir", ["Ignorar a linha", "Sobrescrever o registro"], horizontal=True)

    if uploaded is None:
        return
    try:
        sheet, imp = read_import_file(uploaded)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Nao foi possivel ler o arquivo: {exc}", icon="🚫")
        return

    faltando = [FIELD_MAP[f] for f in ("data_abertura", "sistema", "status") if f not in imp.columns]
    with st.container(border=True):
        st.markdown(f"<div class='section-title'>Previa · aba \"{sheet}\" · {len(imp)} linhas</div>", unsafe_allow_html=True)
        if faltando:
            st.warning("Colunas esperadas nao encontradas: " + ", ".join(faltando))
        if "id" in imp.columns:
            ids = imp["id"].map(clean_text)
            existentes = sum(incident_exists(conn, i) for i in ids if i)
            st.caption(f"{existentes} ID(s) ja existem no banco · {int((ids == '').sum())} linha(s) sem ID receberao um ID novo")
        st.dataframe(imp.rename(columns=FIELD_MAP).head(20), width="stretch", hide_index=True)
        if st.button("Importar registros", type="primary"):
            with st.spinner("Importando..."):
                ins, upd, ign, erros = import_rows(conn, imp, overwrite=modo.startswith("Sobrescrever"))
            msg = f"Importacao concluida: {ins} inserido(s), {upd} atualizado(s), {ign} ignorado(s)"
            if erros:
                st.error(msg + f", {len(erros)} com erro:\n\n" + "\n".join(f"- {e}" for e in erros[:20]), icon="⚠️")
            else:
                flash(msg + ".")
                st.rerun()


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
PAGE_DASHBOARD = st.Page(page_dashboard, title="Dashboard", icon=":material/dashboard:", url_path="dashboard", default=True)
PAGE_EDITAR = st.Page(page_editar, title="Novo/Editar Incidente", icon=":material/edit_note:", url_path="incidente")
PAGE_CONSULTA = st.Page(page_consulta, title="Consulta", icon=":material/search:", url_path="consulta")
PAGE_RCA = st.Page(page_rca, title="RCA e Auditoria", icon=":material/fact_check:", url_path="rca")
PAGE_IMPORT = st.Page(page_import_export, title="Importar/Exportar", icon=":material/swap_vert:", url_path="dados")

nav = st.navigation({
    "Acompanhamento": [PAGE_DASHBOARD, PAGE_EDITAR, PAGE_CONSULTA],
    "Governanca": [PAGE_RCA, PAGE_IMPORT],
})

st.markdown(CSS, unsafe_allow_html=True)
conn = get_conn()

with st.sidebar:
    total, abertos = conn.execute(
        f"SELECT COUNT(*), SUM(status IN ({', '.join('?' * len(OPEN_STATUS))})) FROM incidentes", OPEN_STATUS
    ).fetchone()
    st.caption(f"📦 {total} incidente(s) · {abertos or 0} aberto(s)")
    if total == 0 and st.button("Carregar exemplos da planilha", width="stretch"):
        seed_examples(conn)
        flash("Exemplos carregados.")
        st.rerun()
    st.caption(f"Banco: `{DB_PATH.name}`")

st.markdown(
    f"<div class='app-header'><h1>🚨 {APP_TITLE}</h1>"
    f"<p>{nav.title} · atualizado em {datetime.now():%d/%m/%Y %H:%M}</p></div>",
    unsafe_allow_html=True,
)
show_flash()
nav.run()
