import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

APP_TITLE = "Registro e Acompanhamento de Incidentes de Migração"
DB_PATH = Path("incidentes_migracao.db")

AMBIENTES = ["DEV", "QA", "HML", "PRD", "DR"]
FASES = ["Planejamento", "Pré-cutover", "Cutover", "Validação", "Hypercare", "Rollback", "Encerramento"]
TIPOS = ["Aplicação", "Banco de Dados", "Infraestrutura", "Rede/DNS", "Autenticação/Certificado", "Integração/API", "Batch/Job", "Performance", "Segurança", "Dados", "Comunicação", "Outro"]
SEVERIDADES = ["S1 - Crítico", "S2 - Alto", "S3 - Médio", "S4 - Baixo"]
PRIORIDADES = ["P1 - Imediata", "P2 - Alta", "P3 - Normal", "P4 - Baixa"]
STATUS = ["Novo", "Em análise", "Mitigado", "Em correção", "Aguardando terceiro", "Aguardando negócio", "Resolvido", "Encerrado", "Cancelado"]
IMPACTOS = ["Indisponibilidade total", "Indisponibilidade parcial", "Degradação", "Erro funcional", "Atraso operacional", "Sem impacto ao usuário", "Risco de compliance", "Risco de segurança"]
SIM_NAO = ["Sim", "Não", "N/A"]
COMUNICACOES = ["Não iniciado", "Comunicado inicial enviado", "Atualização enviada", "Comunicado de resolução enviado", "N/A"]
TIMES = ["Aplicação", "Infraestrutura", "Banco de Dados", "Redes", "Segurança", "AMS/Suporte", "Integração", "Negócio", "Fornecedor", "Projeto", "Outro"]
OPEN_STATUS = ["Novo", "Em análise", "Mitigado", "Em correção", "Aguardando terceiro", "Aguardando negócio"]

COLUMNS = [
    "ID", "Data/Hora Abertura", "Ambiente", "Sistema/Aplicação", "Componente/Interface",
    "Fase da Migração", "Tipo", "Severidade", "Prioridade", "Status", "Impacto", "Sintoma/Descrição",
    "Causa Provável", "Responsável", "Time Responsável", "Fornecedor/Parceiro", "Ação Imediata/Mitigação",
    "Próximos Passos", "SLA Alvo (h)", "Prazo", "Data/Hora Resolução", "Duração (h)", "Aging Aberto (h)",
    "Evidência/Link", "Dependências", "Comunicação", "RCA Necessário?", "RCA Entregue?", "Lições Aprendidas",
    "Última Atualização", "Observações"
]

st.set_page_config(page_title=APP_TITLE, page_icon="🚨", layout="wide")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidentes (
            id TEXT PRIMARY KEY,
            data_abertura TEXT NOT NULL,
            ambiente TEXT,
            sistema TEXT,
            componente TEXT,
            fase TEXT,
            tipo TEXT,
            severidade TEXT,
            prioridade TEXT,
            status TEXT,
            impacto TEXT,
            descricao TEXT,
            causa TEXT,
            responsavel TEXT,
            time_responsavel TEXT,
            fornecedor TEXT,
            mitigacao TEXT,
            proximos_passos TEXT,
            sla REAL,
            prazo TEXT,
            data_resolucao TEXT,
            evidencia TEXT,
            dependencias TEXT,
            comunicacao TEXT,
            rca_necessario TEXT,
            rca_entregue TEXT,
            licoes TEXT,
            ultima_atualizacao TEXT,
            observacoes TEXT
        )
    """)
    return conn


def parse_dt(value):
    if value in [None, "", pd.NaT]:
        return None
    try:
        return pd.to_datetime(value, dayfirst=True, errors="coerce")
    except Exception:
        return None


def fmt_dt(value):
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, str):
        value = parse_dt(value)
    if value is None or pd.isna(value):
        return ""
    return pd.Timestamp(value).strftime("%d/%m/%Y %H:%M:%S")


def generate_id(conn):
    rows = conn.execute("SELECT id FROM incidentes WHERE id LIKE 'INC-IRIS-%'").fetchall()
    max_n = 0
    for (inc_id,) in rows:
        try:
            max_n = max(max_n, int(str(inc_id).split("-")[-1]))
        except Exception:
            pass
    return f"INC-IRIS-{max_n + 1:04d}"


def load_data(conn):
    df = pd.read_sql_query("SELECT * FROM incidentes", conn)
    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    now = pd.Timestamp.now()
    out = pd.DataFrame()
    out["ID"] = df["id"]
    out["Data/Hora Abertura"] = pd.to_datetime(df["data_abertura"], errors="coerce")
    out["Ambiente"] = df["ambiente"]
    out["Sistema/Aplicação"] = df["sistema"]
    out["Componente/Interface"] = df["componente"]
    out["Fase da Migração"] = df["fase"]
    out["Tipo"] = df["tipo"]
    out["Severidade"] = df["severidade"]
    out["Prioridade"] = df["prioridade"]
    out["Status"] = df["status"]
    out["Impacto"] = df["impacto"]
    out["Sintoma/Descrição"] = df["descricao"]
    out["Causa Provável"] = df["causa"]
    out["Responsável"] = df["responsavel"]
    out["Time Responsável"] = df["time_responsavel"]
    out["Fornecedor/Parceiro"] = df["fornecedor"]
    out["Ação Imediata/Mitigação"] = df["mitigacao"]
    out["Próximos Passos"] = df["proximos_passos"]
    out["SLA Alvo (h)"] = pd.to_numeric(df["sla"], errors="coerce")
    out["Prazo"] = pd.to_datetime(df["prazo"], errors="coerce")
    out["Data/Hora Resolução"] = pd.to_datetime(df["data_resolucao"], errors="coerce")

    abertura = out["Data/Hora Abertura"]
    resolucao = out["Data/Hora Resolução"]
    status = out["Status"].fillna("")
    is_open = status.isin(OPEN_STATUS)

    end_for_duration = resolucao.where(resolucao.notna(), now)
    out["Duração (h)"] = ((end_for_duration - abertura).dt.total_seconds() / 3600).round(2)
    out["Aging Aberto (h)"] = (((now - abertura).dt.total_seconds() / 3600).round(2)).where(is_open, 0)
    out["Evidência/Link"] = df["evidencia"]
    out["Dependências"] = df["dependencias"]
    out["Comunicação"] = df["comunicacao"]
    out["RCA Necessário?"] = df["rca_necessario"]
    out["RCA Entregue?"] = df["rca_entregue"]
    out["Lições Aprendidas"] = df["licoes"]
    out["Última Atualização"] = pd.to_datetime(df["ultima_atualizacao"], errors="coerce")
    out["Observações"] = df["observacoes"]
    return out[COLUMNS]


def save_record(conn, record):
    conn.execute("""
        INSERT OR REPLACE INTO incidentes (
            id, data_abertura, ambiente, sistema, componente, fase, tipo, severidade, prioridade, status, impacto,
            descricao, causa, responsavel, time_responsavel, fornecedor, mitigacao, proximos_passos, sla, prazo,
            data_resolucao, evidencia, dependencias, comunicacao, rca_necessario, rca_entregue, licoes,
            ultima_atualizacao, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, record)
    conn.commit()


def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df = df.copy()
        for col in ["Data/Hora Abertura", "Prazo", "Data/Hora Resolução", "Última Atualização"]:
            if col in export_df.columns:
                export_df[col] = export_df[col].apply(fmt_dt)
        export_df.to_excel(writer, index=False, sheet_name="Registro de Incidentes")

        listas = pd.DataFrame({
            "Ambiente": pd.Series(AMBIENTES),
            "Fase da Migração": pd.Series(FASES),
            "Tipo de Incidente": pd.Series(TIPOS),
            "Severidade": pd.Series(SEVERIDADES),
            "Prioridade": pd.Series(PRIORIDADES),
            "Status": pd.Series(STATUS),
            "Impacto": pd.Series(IMPACTOS),
            "Sim/Não": pd.Series(SIM_NAO),
            "Comunicação": pd.Series(COMUNICACOES),
            "Time Responsável": pd.Series(TIMES)
        })
        listas.to_excel(writer, index=False, sheet_name="Listas")

        dashboard = build_dashboard_table(df)
        dashboard.to_excel(writer, index=False, sheet_name="Dashboard")

        guia = pd.DataFrame({"Guia de Uso": [
            "Objetivo: centralizar registro, priorização, acompanhamento, evidências, comunicação e lições aprendidas de incidentes de migração.",
            "Como usar: registre cada incidente, acompanhe status, SLA, RCA e evidências, e utilize o dashboard para governança executiva e operacional.",
            "RCA: marque Sim para incidentes críticos, recorrentes, produção, compliance, segurança ou impacto executivo."
        ]})
        guia.to_excel(writer, index=False, sheet_name="Guia de Uso")
    return output.getvalue()


def build_dashboard_table(df):
    if df.empty:
        return pd.DataFrame({"Indicador": [], "Quantidade": []})
    now = pd.Timestamp.now()
    open_mask = df["Status"].isin(OPEN_STATUS)
    prazo = pd.to_datetime(df["Prazo"], errors="coerce")
    vencidos = open_mask & prazo.notna() & (prazo < now)
    rca_pendente = (df["RCA Necessário?"].eq("Sim")) & (~df["RCA Entregue?"].eq("Sim"))
    data = [
        ("Total de Incidentes", len(df)),
        ("Abertos", int(open_mask.sum())),
        ("Críticos S1", int(df["Severidade"].eq("S1 - Crítico").sum())),
        ("Altos S2", int(df["Severidade"].eq("S2 - Alto").sum())),
        ("Vencidos", int(vencidos.sum())),
        ("RCA Pendente", int(rca_pendente.sum())),
    ]
    return pd.DataFrame(data, columns=["Indicador", "Quantidade"])


def seed_examples(conn):
    if conn.execute("SELECT COUNT(*) FROM incidentes").fetchone()[0] > 0:
        return
    examples = [
        ("INC-IRIS-0001", "2026-07-10 09:00:00", "PRD", "<Sistema>", "<Interface/Componente>", "Cutover", "Integração/API", "S2 - Alto", "P2 - Alta", "Em correção", "Degradação", "Exemplo: falha intermitente durante validação pós-cutover.", "Em investigação", "<Nome>", "Aplicação", "<Fornecedor>", "Mitigação temporária aplicada/pendente", "Executar análise técnica e atualizar stakeholders", 4, "2026-07-10 13:00:00", None, "<Link evidência>", "<Dependências>", "Comunicado inicial enviado", "Sim", "Não", "", "2026-07-10 10:00:00", "Linha de exemplo - substituir ou remover"),
        ("INC-IRIS-0002", "2026-07-10 10:30:00", "QA", "<Sistema>", "<Job/Batch>", "Validação", "Batch/Job", "S3 - Médio", "P3 - Normal", "Mitigado", "Atraso operacional", "Exemplo: job de validação executou com atraso após alteração de agendamento.", "Dependência de janela de execução", "<Nome>", "AMS/Suporte", "N/A", "Reexecução manual realizada", "Monitorar próxima execução", 8, "2026-07-10 18:30:00", "2026-07-10 12:00:00", "<Link evidência>", "<Dependências>", "Atualização enviada", "Não", "N/A", "Registrar janela recomendada para próximos cutovers", "2026-07-10 12:05:00", "Linha de exemplo - substituir ou remover")
    ]
    for rec in examples:
        save_record(conn, rec)


conn = get_conn()

st.sidebar.title("Menu")
seed = st.sidebar.checkbox("Carregar exemplos da planilha", value=False)
if seed:
    seed_examples(conn)

page = st.sidebar.radio("Navegação", ["Dashboard", "Novo/Editar Incidente", "Consulta", "RCA e Auditoria", "Importar/Exportar"])
df = load_data(conn)

st.title("🚨 " + APP_TITLE)
st.caption("Aplicação Streamlit baseada na lógica da planilha de acompanhamento de incidentes de migração.")

if page == "Dashboard":
    st.subheader("Dashboard Executivo")
    dashboard = build_dashboard_table(df)
    metrics = dict(zip(dashboard.get("Indicador", []), dashboard.get("Quantidade", [])))
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total", metrics.get("Total de Incidentes", 0))
    c2.metric("Abertos", metrics.get("Abertos", 0))
    c3.metric("Críticos S1", metrics.get("Críticos S1", 0))
    c4.metric("Altos S2", metrics.get("Altos S2", 0))
    c5.metric("Vencidos", metrics.get("Vencidos", 0))
    c6.metric("RCA Pendente", metrics.get("RCA Pendente", 0))

    if df.empty:
        st.info("Nenhum incidente registrado ainda.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Incidentes por Status**")
            st.bar_chart(df["Status"].value_counts())
        with col2:
            st.write("**Incidentes por Severidade**")
            st.bar_chart(df["Severidade"].value_counts())
        with col3:
            st.write("**Incidentes por Tipo**")
            st.bar_chart(df["Tipo"].value_counts())

        st.write("**Heatmap Ambiente x Severidade**")
        heat = pd.crosstab(df["Ambiente"], df["Severidade"]).reindex(index=AMBIENTES, columns=SEVERIDADES, fill_value=0)
        st.dataframe(heat.style.background_gradient(cmap="Reds"), use_container_width=True)

elif page == "Novo/Editar Incidente":
    st.subheader("Novo/Editar Incidente")
    ids = ["Novo"] + df["ID"].dropna().tolist()
    selected = st.selectbox("Selecione um incidente para editar ou crie um novo", ids)
    current = {}
    if selected != "Novo" and not df.empty:
        row = df[df["ID"] == selected].iloc[0]
        current = row.to_dict()

    with st.form("form_incidente"):
        incident_id = current.get("ID", generate_id(conn))
        st.text_input("ID", value=incident_id, disabled=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            data_abertura = st.datetime_input("Data/Hora Abertura", value=parse_dt(current.get("Data/Hora Abertura")) or datetime.now())
            ambiente = st.selectbox("Ambiente", AMBIENTES, index=AMBIENTES.index(current.get("Ambiente")) if current.get("Ambiente") in AMBIENTES else 0)
            fase = st.selectbox("Fase da Migração", FASES, index=FASES.index(current.get("Fase da Migração")) if current.get("Fase da Migração") in FASES else 0)
            tipo = st.selectbox("Tipo", TIPOS, index=TIPOS.index(current.get("Tipo")) if current.get("Tipo") in TIPOS else 0)
        with c2:
            severidade = st.selectbox("Severidade", SEVERIDADES, index=SEVERIDADES.index(current.get("Severidade")) if current.get("Severidade") in SEVERIDADES else 1)
            prioridade = st.selectbox("Prioridade", PRIORIDADES, index=PRIORIDADES.index(current.get("Prioridade")) if current.get("Prioridade") in PRIORIDADES else 1)
            status = st.selectbox("Status", STATUS, index=STATUS.index(current.get("Status")) if current.get("Status") in STATUS else 0)
            impacto = st.selectbox("Impacto", IMPACTOS, index=IMPACTOS.index(current.get("Impacto")) if current.get("Impacto") in IMPACTOS else 2)
        with c3:
            sla = st.number_input("SLA Alvo (h)", min_value=0.0, value=float(current.get("SLA Alvo (h)") or 4), step=1.0)
            prazo_default = parse_dt(current.get("Prazo")) or (data_abertura + timedelta(hours=sla))
            prazo = st.datetime_input("Prazo", value=prazo_default)
            rca_necessario = st.selectbox("RCA Necessário?", SIM_NAO, index=SIM_NAO.index(current.get("RCA Necessário?")) if current.get("RCA Necessário?") in SIM_NAO else 1)
            rca_entregue = st.selectbox("RCA Entregue?", SIM_NAO, index=SIM_NAO.index(current.get("RCA Entregue?")) if current.get("RCA Entregue?") in SIM_NAO else 1)

        sistema = st.text_input("Sistema/Aplicação", value=current.get("Sistema/Aplicação", ""))
        componente = st.text_input("Componente/Interface", value=current.get("Componente/Interface", ""))
        descricao = st.text_area("Sintoma/Descrição", value=current.get("Sintoma/Descrição", ""))
        causa = st.text_area("Causa Provável", value=current.get("Causa Provável", ""))
        responsavel = st.text_input("Responsável", value=current.get("Responsável", ""))
        time_responsavel = st.selectbox("Time Responsável", TIMES, index=TIMES.index(current.get("Time Responsável")) if current.get("Time Responsável") in TIMES else 0)
        fornecedor = st.text_input("Fornecedor/Parceiro", value=current.get("Fornecedor/Parceiro", ""))
        mitigacao = st.text_area("Ação Imediata/Mitigação", value=current.get("Ação Imediata/Mitigação", ""))
        proximos_passos = st.text_area("Próximos Passos", value=current.get("Próximos Passos", ""))
        data_resolucao_enabled = st.checkbox("Informar Data/Hora Resolução", value=pd.notna(current.get("Data/Hora Resolução")) if current else False)
        data_resolucao = st.datetime_input("Data/Hora Resolução", value=parse_dt(current.get("Data/Hora Resolução")) or datetime.now(), disabled=not data_resolucao_enabled)
        evidencia = st.text_input("Evidência/Link", value=current.get("Evidência/Link", ""))
        dependencias = st.text_input("Dependências", value=current.get("Dependências", ""))
        comunicacao = st.selectbox("Comunicação", COMUNICACOES, index=COMUNICACOES.index(current.get("Comunicação")) if current.get("Comunicação") in COMUNICACOES else 0)
        licoes = st.text_area("Lições Aprendidas", value=current.get("Lições Aprendidas", ""))
        observacoes = st.text_area("Observações", value=current.get("Observações", ""))

        submitted = st.form_submit_button("Salvar Incidente")
        if submitted:
            rec = (
                incident_id, data_abertura.strftime("%Y-%m-%d %H:%M:%S"), ambiente, sistema, componente, fase, tipo,
                severidade, prioridade, status, impacto, descricao, causa, responsavel, time_responsavel, fornecedor,
                mitigacao, proximos_passos, sla, prazo.strftime("%Y-%m-%d %H:%M:%S"),
                data_resolucao.strftime("%Y-%m-%d %H:%M:%S") if data_resolucao_enabled else None,
                evidencia, dependencias, comunicacao, rca_necessario, rca_entregue, licoes,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), observacoes
            )
            save_record(conn, rec)
            st.success(f"Incidente {incident_id} salvo com sucesso.")
            st.rerun()

elif page == "Consulta":
    st.subheader("Consulta e Acompanhamento")
    if df.empty:
        st.info("Nenhum incidente registrado ainda.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        f_amb = c1.multiselect("Ambiente", AMBIENTES)
        f_status = c2.multiselect("Status", STATUS)
        f_sev = c3.multiselect("Severidade", SEVERIDADES)
        f_tipo = c4.multiselect("Tipo", TIPOS)
        filtered = df.copy()
        if f_amb: filtered = filtered[filtered["Ambiente"].isin(f_amb)]
        if f_status: filtered = filtered[filtered["Status"].isin(f_status)]
        if f_sev: filtered = filtered[filtered["Severidade"].isin(f_sev)]
        if f_tipo: filtered = filtered[filtered["Tipo"].isin(f_tipo)]
        st.dataframe(filtered, use_container_width=True, hide_index=True)

elif page == "RCA e Auditoria":
    st.subheader("RCA e Auditoria")
    if df.empty:
        st.info("Nenhum incidente registrado ainda.")
    else:
        rca = df[(df["RCA Necessário?"].eq("Sim")) & (~df["RCA Entregue?"].eq("Sim"))]
        st.metric("RCA Pendente", len(rca))
        st.dataframe(rca[["ID", "Ambiente", "Sistema/Aplicação", "Severidade", "Status", "Responsável", "Evidência/Link", "Última Atualização", "Observações"]], use_container_width=True, hide_index=True)
        st.markdown("""
        **Critério sugerido:** marcar RCA como necessário para incidentes críticos, recorrentes, produção, compliance, segurança ou acionamento executivo.
        """)

elif page == "Importar/Exportar":
    st.subheader("Importar/Exportar")
    st.download_button(
        "Baixar Excel com registros, listas e dashboard",
        data=to_excel(df),
        file_name="Planilha_Acompanhamento_Incidentes_Migracao_Streamlit.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    uploaded = st.file_uploader("Importar Excel da planilha original", type=["xlsx"])
    if uploaded is not None:
        imp = pd.read_excel(uploaded, sheet_name="Registro de Incidentes", engine="openpyxl")
        st.write("Prévia do arquivo importado:")
        st.dataframe(imp.head(20), use_container_width=True)
        if st.button("Importar registros"):
            for _, row in imp.iterrows():
                inc_id = str(row.get("ID") or generate_id(conn))
                data_abertura = parse_dt(row.get("Data/Hora Abertura")) or datetime.now()
                sla = float(row.get("SLA Alvo (h)") or 0)
                prazo = parse_dt(row.get("Prazo")) or (data_abertura + timedelta(hours=sla))
                data_res = parse_dt(row.get("Data/Hora Resolução"))
                rec = (
                    inc_id, data_abertura.strftime("%Y-%m-%d %H:%M:%S"), row.get("Ambiente", ""), row.get("Sistema/Aplicação", ""),
                    row.get("Componente/Interface", ""), row.get("Fase da Migração", ""), row.get("Tipo", ""), row.get("Severidade", ""),
                    row.get("Prioridade", ""), row.get("Status", ""), row.get("Impacto", ""), row.get("Sintoma/Descrição", ""),
                    row.get("Causa Provável", ""), row.get("Responsável", ""), row.get("Time Responsável", ""), row.get("Fornecedor/Parceiro", ""),
                    row.get("Ação Imediata/Mitigação", ""), row.get("Próximos Passos", ""), sla, prazo.strftime("%Y-%m-%d %H:%M:%S"),
                    data_res.strftime("%Y-%m-%d %H:%M:%S") if data_res is not None and not pd.isna(data_res) else None,
                    row.get("Evidência/Link", ""), row.get("Dependências", ""), row.get("Comunicação", ""), row.get("RCA Necessário?", ""),
                    row.get("RCA Entregue?", ""), row.get("Lições Aprendidas", ""), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row.get("Observações", "")
                )
                save_record(conn, rec)
            st.success("Registros importados com sucesso.")
            st.rerun()
