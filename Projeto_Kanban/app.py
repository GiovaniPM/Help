import os
import json
import sqlite3
from io import BytesIO
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Tuple

import pandas as pd
import streamlit as st


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Kanban - Gerenciamento de Projetos", layout="wide")

DB_PATH = os.getenv("KANBAN_DB_PATH", "kanban.db")

STATUSES = [
    "roadmap", "escopo", "bbp", "estimativa", "sincronização", "proposta", "kick-off",
    "implementação", "SIT", "UAT", "cutover", "deploy", "hypercare", "done"
]

# Colunas esperadas nas métricas (evita KeyError em DF vazio)
METRICS_COLUMNS = [
    "id_planview", "nome", "status",
    "create_ts", "done_entry_ts", "current_status_entry_ts",
    "lead_time_days", "aging_days"
]


# =========================================================
# DB HELPERS
# =========================================================
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Mantém compatibilidade com schema existente e cria auditoria.
    Não faz breaking changes na tabela projects.
    """
    ddl_projects = """
    CREATE TABLE IF NOT EXISTS projects (
      id_planview TEXT PRIMARY KEY,
      nome        TEXT NOT NULL,
      descricao   TEXT,
      gp          TEXT,
      recursos    TEXT,
      data_inicio TEXT,
      data_fim    TEXT,
      status      TEXT,
      request     TEXT,
      change      TEXT
    );
    """

    ddl_history = """
    CREATE TABLE IF NOT EXISTS project_history (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      id_planview TEXT NOT NULL,
      action      TEXT NOT NULL,
      changed_at  TEXT NOT NULL,
      changed_by  TEXT NOT NULL,
      before_data TEXT,
      after_data  TEXT
    );
    """

    ddl_idx1 = "CREATE INDEX IF NOT EXISTS idx_hist_planview ON project_history (id_planview);"
    ddl_idx2 = "CREATE INDEX IF NOT EXISTS idx_hist_changed_at ON project_history (changed_at);"

    cur = conn.cursor()
    cur.execute(ddl_projects)
    cur.execute(ddl_history)
    cur.execute(ddl_idx1)
    cur.execute(ddl_idx2)
    conn.commit()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def get_changed_by() -> str:
    """
    best-effort:
    - tenta Streamlit: st.experimental_user.email (se existir)
    - env USER/USERNAME
    - fallback: "unknown"
    """
    try:
        u = getattr(st, "experimental_user", None)
        if u is not None:
            email = getattr(u, "email", None)
            if email:
                return str(email)
    except Exception:
        pass

    for k in ("USER", "USERNAME"):
        v = os.getenv(k)
        if v:
            return v

    return "unknown"


def row_to_project_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id_planview": row["id_planview"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "gp": row["gp"],
        "recursos": row["recursos"],
        "data_inicio": row["data_inicio"],
        "data_fim": row["data_fim"],
        "status": row["status"],
        "request": row["request"],
        "change": row["change"],
    }


def normalize_date_str(d: Optional[date]) -> Optional[str]:
    if d is None:
        return None
    return d.isoformat()


def parse_date_str(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


def safe_json_dumps(obj: Optional[dict]) -> Optional[str]:
    if obj is None:
        return None
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)


def safe_json_loads(s: Optional[str]) -> Optional[dict]:
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def execute_write(conn: sqlite3.Connection, fn):
    """
    Executa uma função de escrita em transação.
    Em falha: rollback + re-raise.
    """
    try:
        conn.execute("BEGIN")
        result = fn()
        conn.commit()
        return result
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise


# =========================================================
# AUDIT HELPERS
# =========================================================
def insert_history(
    conn: sqlite3.Connection,
    id_planview: str,
    action: str,
    before_data: Optional[Dict[str, Any]],
    after_data: Optional[Dict[str, Any]],
) -> None:
    conn.execute(
        """
        INSERT INTO project_history (id_planview, action, changed_at, changed_by, before_data, after_data)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            id_planview,
            action,
            now_iso(),
            get_changed_by(),
            safe_json_dumps(before_data),
            safe_json_dumps(after_data),
        ),
    )


def get_project(conn: sqlite3.Connection, id_planview: str) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT * FROM projects WHERE id_planview = ?", (id_planview,)).fetchone()
    if not row:
        return None
    return row_to_project_dict(row)


def get_all_projects(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute("SELECT * FROM projects").fetchall()
    return [row_to_project_dict(r) for r in rows]


def get_recent_history(conn: sqlite3.Connection, id_planview: str, limit: int = 5) -> List[sqlite3.Row]:
    return conn.execute(
        """
        SELECT * FROM project_history
        WHERE id_planview = ?
        ORDER BY changed_at DESC
        LIMIT ?
        """,
        (id_planview, limit),
    ).fetchall()


# =========================================================
# CRUD (with audit)
# =========================================================
def create_project(conn: sqlite3.Connection, data: Dict[str, Any]) -> None:
    def _tx():
        conn.execute(
            """
            INSERT INTO projects (id_planview, nome, descricao, gp, recursos, data_inicio, data_fim, status, request, change)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id_planview"],
                data["nome"],
                data.get("descricao"),
                data.get("gp"),
                data.get("recursos"),
                data.get("data_inicio"),
                data.get("data_fim"),
                data.get("status"),
                data.get("request"),
                data.get("change"),
            ),
        )
        insert_history(conn, data["id_planview"], "CREATE", None, data)

    execute_write(conn, _tx)


def update_project_full(
    conn: sqlite3.Connection,
    id_planview: str,
    new_data: Dict[str, Any],
    action: str,
    before_snapshot: Dict[str, Any],
) -> None:
    def _tx():
        conn.execute(
            """
            UPDATE projects
            SET nome = ?, descricao = ?, gp = ?, recursos = ?, data_inicio = ?, data_fim = ?, status = ?, request = ?, change = ?
            WHERE id_planview = ?
            """,
            (
                new_data["nome"],
                new_data.get("descricao"),
                new_data.get("gp"),
                new_data.get("recursos"),
                new_data.get("data_inicio"),
                new_data.get("data_fim"),
                new_data.get("status"),
                new_data.get("request"),
                new_data.get("change"),
                id_planview,
            ),
        )
        insert_history(conn, id_planview, action, before_snapshot, new_data)

    execute_write(conn, _tx)


def update_status_only(conn: sqlite3.Connection, id_planview: str, new_status: str) -> None:
    before = get_project(conn, id_planview)
    if not before:
        return
    after = dict(before)
    after["status"] = new_status

    def _tx():
        conn.execute("UPDATE projects SET status = ? WHERE id_planview = ?", (new_status, id_planview))
        insert_history(conn, id_planview, "STATUS_CHANGE", before, after)

    execute_write(conn, _tx)


def delete_project(conn: sqlite3.Connection, id_planview: str) -> None:
    before = get_project(conn, id_planview)
    if not before:
        return

    def _tx():
        conn.execute("DELETE FROM projects WHERE id_planview = ?", (id_planview,))
        insert_history(conn, id_planview, "DELETE", before, None)

    execute_write(conn, _tx)


# =========================================================
# FILTERS
# =========================================================
def project_matches_text(p: Dict[str, Any], q: str) -> bool:
    if not q:
        return True
    ql = q.strip().lower()
    if not ql:
        return True
    for field in ("id_planview", "nome", "descricao"):
        v = p.get(field)
        if v and ql in str(v).lower():
            return True
    return False


def project_overlaps_period(p: Dict[str, Any], start: Optional[date], end: Optional[date]) -> bool:
    if start is None and end is None:
        return True

    p_start = parse_date_str(p.get("data_inicio"))
    p_end = parse_date_str(p.get("data_fim"))

    # sem datas => inclui
    if p_start is None and p_end is None:
        return True

    # excluir apenas se claramente fora
    if start is not None:
        if p_end is not None and p_end < start:
            return False
    if end is not None:
        if p_start is not None and p_start > end:
            return False

    return True


def apply_filters(
    projects: List[Dict[str, Any]],
    text_q: str,
    status_sel: List[str],
    gp_sel: List[str],
    start: Optional[date],
    end: Optional[date],
) -> List[Dict[str, Any]]:
    status_set = set(status_sel) if status_sel else set(STATUSES)
    gp_set = set(gp_sel) if gp_sel else None

    out = []
    for p in projects:
        if (p.get("status") or "") not in status_set:
            continue
        if gp_set is not None:
            gp_val = (p.get("gp") or "").strip()
            if gp_val not in gp_set:
                continue
        if not project_matches_text(p, text_q):
            continue
        if not project_overlaps_period(p, start, end):
            continue
        out.append(p)
    return out


# =========================================================
# METRICS (history-driven)
# =========================================================
def parse_iso_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
        return dt
    except Exception:
        return None


def load_history_for_ids(conn: sqlite3.Connection, ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    if not ids:
        return {}

    placeholders = ",".join(["?"] * len(ids))
    rows = conn.execute(
        f"""
        SELECT * FROM project_history
        WHERE id_planview IN ({placeholders})
        ORDER BY changed_at ASC
        """,
        tuple(ids),
    ).fetchall()

    hist_map: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        pid = r["id_planview"]
        ev = {
            "id": r["id"],
            "id_planview": pid,
            "action": r["action"],
            "changed_at": r["changed_at"],
            "changed_at_dt": parse_iso_dt(r["changed_at"]),
            "changed_by": r["changed_by"],
            "before_data": safe_json_loads(r["before_data"]),
            "after_data": safe_json_loads(r["after_data"]),
        }
        hist_map.setdefault(pid, []).append(ev)

    return hist_map


def get_create_ts(events: List[Dict[str, Any]]) -> Optional[datetime]:
    for ev in events:
        if ev.get("action") == "CREATE":
            return ev.get("changed_at_dt")
    if events:
        return events[0].get("changed_at_dt")
    return None


def get_first_done_entry_ts(events: List[Dict[str, Any]]) -> Optional[datetime]:
    for ev in events:
        after = ev.get("after_data") or {}
        before = ev.get("before_data")
        after_status = (after.get("status") or "").strip().lower()
        before_status = None
        if before:
            before_status = (before.get("status") or "").strip().lower()

        if after_status == "done":
            if before is None or before_status != "done":
                return ev.get("changed_at_dt")
    return None


def get_current_status_entry_ts(events: List[Dict[str, Any]], current_status: str) -> Optional[datetime]:
    cur = (current_status or "").strip().lower()
    candidates: List[datetime] = []

    for ev in events:
        after = ev.get("after_data") or {}
        before = ev.get("before_data")
        after_status = (after.get("status") or "").strip().lower()
        before_status = None
        if before:
            before_status = (before.get("status") or "").strip().lower()

        if after_status == cur and cur:
            if before is None or before_status != cur:
                dt = ev.get("changed_at_dt")
                if dt:
                    candidates.append(dt)

    if candidates:
        return max(candidates)

    return get_create_ts(events)


def days_between(a: Optional[datetime], b: Optional[datetime]) -> Optional[float]:
    if not a or not b:
        return None
    delta = b - a
    return delta.total_seconds() / 86400.0


def compute_metrics(conn: sqlite3.Connection, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    ✅ CORREÇÃO DO KeyError:
    - Se projects estiver vazio, cria DF vazio COM COLUNAS.
    - Garante existência da coluna 'status' antes de acessar df['status'].
    """
    if not projects:
        df = pd.DataFrame(columns=METRICS_COLUMNS)
        hist = {}
    else:
        ids = [p["id_planview"] for p in projects if p.get("id_planview")]
        hist = load_history_for_ids(conn, ids)
        now_dt = datetime.now().astimezone()

        rows = []
        for p in projects:
            pid = p.get("id_planview")
            if not pid:
                continue

            events = hist.get(pid, [])
            create_ts = get_create_ts(events)
            done_ts = get_first_done_entry_ts(events)
            current_status = p.get("status") or "roadmap"
            current_entry_ts = get_current_status_entry_ts(events, current_status)

            lead_time_days = days_between(create_ts, done_ts) if done_ts else None
            aging_days = days_between(current_entry_ts, now_dt) if current_entry_ts else None

            rows.append({
                "id_planview": pid,
                "nome": p.get("nome"),
                "status": p.get("status", "") or "",  # ✅ garante
                "create_ts": create_ts,
                "done_entry_ts": done_ts,
                "current_status_entry_ts": current_entry_ts,
                "lead_time_days": lead_time_days,
                "aging_days": aging_days,
            })

        df = pd.DataFrame(rows)

    # ✅ blindagem extra
    for col in METRICS_COLUMNS:
        if col not in df.columns:
            df[col] = pd.Series(dtype="object")

    total = len(projects)
    total_done = int((df["status"] == "done").sum()) if total else 0
    total_wip = total - total_done

    lead_done = df[df["status"] == "done"].copy()
    lead_avg = float(lead_done["lead_time_days"].dropna().mean()) if not lead_done.empty else None

    wip_df = df[df["status"] != "done"].copy()
    aging_avg_wip = float(wip_df["aging_days"].dropna().mean()) if not wip_df.empty else None

    aging_by_status = (
        df.dropna(subset=["aging_days"])
        .groupby("status")["aging_days"]
        .mean()
        .reindex(STATUSES)
    )

    return {
        "df": df,
        "total": total,
        "total_wip": total_wip,
        "total_done": total_done,
        "lead_avg": lead_avg,
        "aging_avg_wip": aging_avg_wip,
        "aging_by_status": aging_by_status,
        "lead_done_df": lead_done.sort_values("lead_time_days", ascending=False) if not lead_done.empty else lead_done,
    }


# =========================================================
# UI: DIALOG (edit)
# =========================================================
def _dialog_decorator(title: str):
    if hasattr(st, "dialog"):
        return st.dialog(title, width="large", dismissible=False)
    if hasattr(st, "experimental_dialog"):
        return st.experimental_dialog(title, width="large")
    return None


_dialog = _dialog_decorator("Editar projeto")
if _dialog is None:
    def edit_project_dialog():
        st.warning("Seu Streamlit não suporta dialogs. Atualize o Streamlit para usar modal.")
else:
    @_dialog
    def edit_project_dialog():
        pid = st.session_state.get("edit_project_id")
        if not pid:
            st.info("Nenhum projeto selecionado.")
            if st.button("Fechar"):
                st.rerun()
            return

        conn = get_conn()
        init_db(conn)

        p = get_project(conn, pid)
        if not p:
            st.error("Projeto não encontrado (pode ter sido removido).")
            if st.button("Fechar"):
                st.session_state["edit_project_id"] = None
                st.rerun()
            return

        before = dict(p)

        st.caption(f"ID Planview (somente leitura): **{pid}**")

        with st.form(f"edit_form_{pid}", clear_on_submit=False):
            nome = st.text_input("Nome *", value=p.get("nome") or "")
            descricao = st.text_area("Descrição", value=p.get("descricao") or "", height=120)

            c1, c2 = st.columns(2)
            with c1:
                gp = st.text_input("GP", value=p.get("gp") or "")
                request = st.text_input("Request", value=p.get("request") or "")
                change = st.text_input("Change", value=p.get("change") or "")
            with c2:
                recursos = st.text_area("Recursos", value=p.get("recursos") or "", height=120)
                cur_status = p.get("status") or "roadmap"
                if cur_status not in STATUSES:
                    cur_status = "roadmap"
                status = st.selectbox("Status", options=STATUSES, index=STATUSES.index(cur_status))

            c3, c4 = st.columns(2)
            with c3:
                di = parse_date_str(p.get("data_inicio"))
                data_inicio = st.date_input("Data início", value=di)
                limpar_di = st.checkbox("Sem data início", value=(di is None), key=f"clear_di_{pid}")
            with c4:
                dfim = parse_date_str(p.get("data_fim"))
                data_fim = st.date_input("Data fim", value=dfim)
                limpar_df = st.checkbox("Sem data fim", value=(dfim is None), key=f"clear_df_{pid}")

            submitted = st.form_submit_button("Salvar")

        colb1, colb2 = st.columns([1, 1])
        with colb1:
            if st.button("Cancelar"):
                st.session_state["edit_project_id"] = None
                st.rerun()
        with colb2:
            st.write("")

        if submitted:
            if not nome.strip():
                st.warning("O campo **Nome** é obrigatório. Não foi salvo.")
                return

            new_data = {
                "id_planview": pid,
                "nome": nome.strip(),
                "descricao": descricao.strip() if descricao else None,
                "gp": gp.strip() if gp else None,
                "recursos": recursos.strip() if recursos else None,
                "data_inicio": None if limpar_di else normalize_date_str(data_inicio),
                "data_fim": None if limpar_df else normalize_date_str(data_fim),
                "status": status,
                "request": request.strip() if request else None,
                "change": change.strip() if change else None,
            }

            changed_fields = []
            for k in ("nome", "descricao", "gp", "recursos", "data_inicio", "data_fim", "status", "request", "change"):
                if (before.get(k) or None) != (new_data.get(k) or None):
                    changed_fields.append(k)

            if not changed_fields:
                st.info("Nenhuma alteração detectada.")
                st.session_state["edit_project_id"] = None
                st.rerun()
                return

            action = "STATUS_CHANGE" if changed_fields == ["status"] else "UPDATE"

            try:
                update_project_full(conn, pid, new_data, action=action, before_snapshot=before)
                st.success("Projeto atualizado com sucesso.")
                st.session_state["edit_project_id"] = None
                st.rerun()
            except sqlite3.IntegrityError as e:
                st.error(f"Erro de integridade ao salvar: {e}")
            except sqlite3.OperationalError as e:
                st.error(f"Erro operacional no banco: {e}")
            except Exception as e:
                st.error(f"Falha ao salvar: {e}")


def open_edit_dialog(pid: str):
    st.session_state["edit_project_id"] = pid
    edit_project_dialog()


# =========================================================
# SIDEBAR: CREATE (compatível)
# =========================================================
def sidebar_create(conn: sqlite3.Connection):
    st.sidebar.header("Cadastrar Projeto")

    id_planview = st.sidebar.text_input("ID Planview *")
    nome = st.sidebar.text_input("Nome *")
    descricao = st.sidebar.text_area("Descrição")
    gp = st.sidebar.text_input("GP")
    recursos = st.sidebar.text_area("Recursos")
    request = st.sidebar.text_input("Request")
    change = st.sidebar.text_input("Change")

    st.sidebar.markdown("---")
    st.sidebar.caption("Datas (opcionais)")
    di = st.sidebar.date_input("Data início", value=None)
    dfim = st.sidebar.date_input("Data fim", value=None)
    limpar_di = st.sidebar.checkbox("Sem data início", value=(di is None))
    limpar_df = st.sidebar.checkbox("Sem data fim", value=(dfim is None))

    status = st.sidebar.selectbox("Status inicial", options=STATUSES, index=0)

    if st.sidebar.button("Salvar"):
        if not id_planview.strip():
            st.warning("O campo **ID Planview** é obrigatório. Não foi salvo.")
            return
        if not nome.strip():
            st.warning("O campo **Nome** é obrigatório. Não foi salvo.")
            return

        data = {
            "id_planview": id_planview.strip(),
            "nome": nome.strip(),
            "descricao": descricao.strip() if descricao else None,
            "gp": gp.strip() if gp else None,
            "recursos": recursos.strip() if recursos else None,
            "data_inicio": None if limpar_di else normalize_date_str(di),
            "data_fim": None if limpar_df else normalize_date_str(dfim),
            "status": status,
            "request": request.strip() if request else None,
            "change": change.strip() if change else None,
        }

        try:
            create_project(conn, data)
            st.sidebar.success("Projeto criado.")
            st.rerun()
        except sqlite3.IntegrityError:
            st.sidebar.error("Já existe um projeto com este ID Planview (duplicidade).")
        except sqlite3.OperationalError as e:
            st.sidebar.error(f"Erro operacional no banco: {e}")
        except Exception as e:
            st.sidebar.error(f"Falha ao salvar: {e}")


# =========================================================
# MAIN UI
# =========================================================
def render_filters(all_projects: List[Dict[str, Any]]) -> Tuple[str, List[str], List[str], Optional[date], Optional[date]]:
    with st.expander("🔎 Filtros e busca", expanded=False):
        text_q = st.text_input("Busca textual (id_planview, nome, descrição)", value="")

        c1, c2 = st.columns([2, 2])
        with c1:
            status_sel = st.multiselect("Status", options=STATUSES, default=STATUSES)

        gps = sorted({(p.get("gp") or "").strip() for p in all_projects})
        with c2:
            gp_sel = st.multiselect("GP", options=gps, default=gps)

        c3, c4 = st.columns([1, 1])
        with c3:
            start = st.date_input("Período - início (opcional)", value=None)
        with c4:
            end = st.date_input("Período - fim (opcional)", value=None)

    return text_q, status_sel, gp_sel, start, end


def render_metrics(conn: sqlite3.Connection, projects_filtered: List[Dict[str, Any]]):
    st.subheader("📊 Métricas")

    m = compute_metrics(conn, projects_filtered)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de projetos", m["total"])
    c2.metric("Total WIP", m["total_wip"])
    c3.metric("Total Done", m["total_done"])
    c4.metric("Lead time médio (dias) - Done", "-" if m["lead_avg"] is None else f"{m['lead_avg']:.1f}")

    c5, c6 = st.columns([1, 2])
    with c5:
        st.metric("Aging médio (dias) - WIP", "-" if m["aging_avg_wip"] is None else f"{m['aging_avg_wip']:.1f}")

    with c6:
        series = m["aging_by_status"].dropna()
        if series.empty:
            st.info("Sem dados de histórico suficientes para calcular aging por coluna.")
        else:
            st.bar_chart(series)

    with st.expander("📈 Lead time por projeto (Done)", expanded=False):
        lead_df = m["lead_done_df"].copy()
        if lead_df.empty:
            st.write("Nenhum projeto em **done** com histórico suficiente.")
        else:
            show = lead_df[["id_planview", "nome", "lead_time_days", "create_ts", "done_entry_ts"]].copy()
            show["lead_time_days"] = show["lead_time_days"].round(1)
            st.dataframe(show, use_container_width=True, hide_index=True)


def render_project_card(conn: sqlite3.Connection, p: Dict[str, Any]):
    pid = p["id_planview"]
    nome = p.get("nome") or ""
    status = p.get("status") or "roadmap"
    if status not in STATUSES:
        status = "roadmap"

    top = st.container(border=True)
    with top:
        c1, c2, c3 = st.columns([6, 1, 1])
        with c1:
            st.markdown(f"**{pid} — {nome}**")
        with c2:
            if st.button("✏️", key=f"edit_{pid}", help="Editar"):
                open_edit_dialog(pid)
                st.stop()
        with c3:
            if st.button("🗑️", key=f"del_{pid}", help="Excluir definitivamente"):
                try:
                    delete_project(conn, pid)
                    st.success(f"Projeto {pid} excluído.")
                    st.rerun()
                except sqlite3.OperationalError as e:
                    st.error(f"Erro operacional no banco: {e}")
                except Exception as e:
                    st.error(f"Falha ao excluir: {e}")

        sel = st.selectbox(
            "Mover status",
            options=STATUSES,
            index=STATUSES.index(status),
            key=f"status_{pid}",
            label_visibility="collapsed"
        )
        if sel != status:
            try:
                update_status_only(conn, pid, sel)
                st.rerun()
            except sqlite3.OperationalError as e:
                st.error(f"Erro operacional no banco: {e}")
            except Exception as e:
                st.error(f"Falha ao mover status: {e}")

        with st.expander("Detalhes", expanded=False):
            st.write(f"**Descrição:** {p.get('descricao') or '-'}")
            st.write(f"**GP:** {p.get('gp') or '-'}")
            st.write(f"**Request:** {p.get('request') or '-'}")
            st.write(f"**Change:** {p.get('change') or '-'}")
            st.write(f"**Recursos:** {p.get('recursos') or '-'}")
            st.write(f"**Data início:** {p.get('data_inicio') or '-'}")
            st.write(f"**Data fim:** {p.get('data_fim') or '-'}")
            st.write(f"**Status:** {p.get('status') or '-'}")

            hist_rows = get_recent_history(conn, pid, limit=5)
            if hist_rows:
                st.markdown("**Últimos 5 eventos (auditoria)**")
                view = []
                for r in hist_rows:
                    b = safe_json_loads(r["before_data"])
                    a = safe_json_loads(r["after_data"])
                    b_status = (b or {}).get("status")
                    a_status = (a or {}).get("status")
                    view.append({
                        "quando": r["changed_at"],
                        "ação": r["action"],
                        "por": r["changed_by"],
                        "status antes": b_status,
                        "status depois": a_status,
                    })
                st.dataframe(pd.DataFrame(view), use_container_width=True, hide_index=True)
            else:
                st.caption("Sem eventos de histórico para este projeto (ainda).")


def chunked(lst: List[str], n: int) -> List[List[str]]:
    return [lst[i:i+n] for i in range(0, len(lst), n)]


def render_board(conn: sqlite3.Connection, projects_filtered: List[Dict[str, Any]]):
    st.subheader("🧩 Kanban")

    by_status: Dict[str, List[Dict[str, Any]]] = {s: [] for s in STATUSES}
    for p in projects_filtered:
        s = p.get("status") or "roadmap"
        if s not in by_status:
            s = "roadmap"
        by_status[s].append(p)

    for row_statuses in chunked(STATUSES, 4):
        cols = st.columns(len(row_statuses))
        for i, s in enumerate(row_statuses):
            with cols[i]:
                st.markdown(f"### {s}")
                items = by_status.get(s, [])
                if not items:
                    st.caption("—")
                else:
                    items_sorted = sorted(items, key=lambda x: (x.get("data_inicio") or "", x["id_planview"]))
                    for p in items_sorted:
                        render_project_card(conn, p)


def render_list_and_export(projects_filtered: List[Dict[str, Any]]):
    st.subheader("📋 Lista")

    if not projects_filtered:
        st.info("Nenhum projeto para exibir com os filtros atuais.")
        return

    df = pd.DataFrame(projects_filtered)
    sort_cols = [c for c in ["status", "gp", "data_inicio", "id_planview"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols, ascending=True, na_position="last")

    st.dataframe(df, use_container_width=True, hide_index=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="projetos")
    output.seek(0)

    st.download_button(
        "⬇️ Exportar para Excel",
        data=output,
        file_name="projetos_kanban.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================================================
# APP
# =========================================================
def main():
    st.title("Gerenciamento de Projetos - Kanban (Streamlit + SQLite)")

    conn = get_conn()
    init_db(conn)

    sidebar_create(conn)

    all_projects = get_all_projects(conn)

    text_q, status_sel, gp_sel, start, end = render_filters(all_projects)

    projects_filtered = apply_filters(
        all_projects,
        text_q=text_q,
        status_sel=status_sel,
        gp_sel=gp_sel,
        start=start,
        end=end
    )

    st.caption(f"Exibindo **{len(projects_filtered)}** projeto(s) (com filtros aplicados).")

    render_metrics(conn, projects_filtered)

    st.divider()

    render_board(conn, projects_filtered)

    st.divider()

    render_list_and_export(projects_filtered)


if __name__ == "__main__":
    main()