import os
import json
import sqlite3
import datetime as dt
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple

import pandas as pd
import streamlit as st

# =============================
# Config
# =============================
st.set_page_config(page_title="Kanban - Gerenciamento de Projetos", layout="wide")

STATUSES: List[str] = [
    "roadmap", "escopo", "bbp", "estimativa", "sincronização", "proposta", "kick-off",
    "implementação", "SIT", "UAT", "cutover", "deploy", "hypercare", "done"
]

DB_PATH = "kanban_projects.db"

# =============================
# Utils
# =============================

def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_date(s: str) -> Optional[dt.date]:
    if not s:
        return None
    try:
        return dt.date.fromisoformat(s)
    except Exception:
        return None


def date_to_iso(d: Optional[dt.date]) -> str:
    return d.isoformat() if d else ""


def get_current_user() -> str:
    try:
        u = getattr(st, "experimental_user", None)
        if u and getattr(u, "email", None):
            return u.email
        if u and getattr(u, "name", None):
            return u.name
    except Exception:
        pass
    return os.getenv("USER") or os.getenv("USERNAME") or "unknown"


def json_dumps(data: Optional[Dict[str, Any]]) -> Optional[str]:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def json_loads(s: Optional[str]) -> Optional[Dict[str, Any]]:
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


# =============================
# Database helpers
# =============================

def _dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@st.cache_resource(show_spinner=False)
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = _dict_factory
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
    except Exception:
        pass
    return conn


@contextmanager
def db_cursor():
    conn = get_conn()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def init_db() -> None:
    with db_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id_planview   TEXT PRIMARY KEY,
                nome          TEXT NOT NULL,
                descricao     TEXT,
                gp            TEXT,
                recursos_iris TEXT,
                request       TEXT,
                change        TEXT,
                data_inicio   TEXT,
                data_fim      TEXT,
                status        TEXT NOT NULL
            )
            """
        )
        try:
            cur.execute("ALTER TABLE projects ADD COLUMN request TEXT;")
        except sqlite3.OperationalError:
            pass
        try:
            cur.execute("ALTER TABLE projects ADD COLUMN change TEXT;")
        except sqlite3.OperationalError:
            pass

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS project_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                id_planview  TEXT NOT NULL,
                action       TEXT NOT NULL,
                changed_at   TEXT NOT NULL,
                changed_by   TEXT NOT NULL,
                before_data  TEXT,
                after_data   TEXT
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_planview ON project_history(id_planview);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_changed_at ON project_history(changed_at);")


def log_history(id_planview: str, action: str, before: Optional[Dict[str, Any]], after: Optional[Dict[str, Any]]) -> None:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO project_history (id_planview, action, changed_at, changed_by, before_data, after_data)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (id_planview, action, now_iso(), get_current_user(), json_dumps(before), json_dumps(after)),
        )


def fetch_project(id_planview: str) -> Optional[Dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id_planview, nome, descricao, gp, recursos_iris, request, change, data_inicio, data_fim, status
            FROM projects
            WHERE id_planview = ?
            """,
            (id_planview,),
        )
        rows = cur.fetchall()
        return rows[0] if rows else None


def fetch_projects() -> List[Dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id_planview, nome, descricao, gp, recursos_iris, request, change, data_inicio, data_fim, status
            FROM projects
            ORDER BY
                CASE WHEN data_inicio IS NULL OR data_inicio = '' THEN 1 ELSE 0 END,
                data_inicio,
                nome
            """
        )
        return cur.fetchall()


def fetch_history(id_planview: str, limit: int = 50) -> List[Dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id, id_planview, action, changed_at, changed_by, before_data, after_data
            FROM project_history
            WHERE id_planview = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (id_planview, limit),
        )
        return cur.fetchall()


def insert_project(p: Dict[str, Any]) -> Optional[str]:
    try:
        with db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO projects (
                    id_planview, nome, descricao, gp, recursos_iris, request, change, data_inicio, data_fim, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p["id_planview"], p["nome"], p.get("descricao"), p.get("gp"), p.get("recursos_iris"),
                    p.get("request"), p.get("change"), p.get("data_inicio"), p.get("data_fim"), p.get("status", "roadmap"),
                ),
            )
        log_history(p["id_planview"], "CREATE", None, p)
        return None
    except sqlite3.IntegrityError as e:
        return f"ID duplicado: {e}"
    except Exception as e:
        return f"Erro inesperado ao salvar: {e}"


def update_project(id_planview: str, payload: Dict[str, Any]) -> Optional[str]:
    try:
        before = fetch_project(id_planview)
        if not before:
            return "Projeto não encontrado."

        with db_cursor() as cur:
            cur.execute(
                """
                UPDATE projects
                SET nome = ?, descricao = ?, gp = ?, recursos_iris = ?, request = ?, change = ?, 
                    data_inicio = ?, data_fim = ?, status = ?
                WHERE id_planview = ?
                """,
                (
                    payload.get("nome"), payload.get("descricao"), payload.get("gp"), payload.get("recursos_iris"),
                    payload.get("request"), payload.get("change"), payload.get("data_inicio"), 
                    payload.get("data_fim"), payload.get("status"), id_planview,
                ),
            )

        after = fetch_project(id_planview)
        action = "STATUS_CHANGE" if before.get("status") != after.get("status") else "UPDATE"
        log_history(id_planview, action, before, after)
        return None
    except Exception as e:
        return f"Erro ao atualizar: {e}"


def update_status(id_planview: str, new_status: str) -> Optional[str]:
    try:
        before = fetch_project(id_planview)
        if not before: return "Projeto não encontrado."
        with db_cursor() as cur:
            cur.execute("UPDATE projects SET status = ? WHERE id_planview = ?", (new_status, id_planview))
        after = fetch_project(id_planview)
        log_history(id_planview, "STATUS_CHANGE", before, after)
        return None
    except Exception as e:
        return f"Erro: {e}"


def delete_project(id_planview: str) -> Optional[str]:
    try:
        before = fetch_project(id_planview)
        if not before: return "Projeto não encontrado."
        with db_cursor() as cur:
            cur.execute("DELETE FROM projects WHERE id_planview = ?", (id_planview,))
        log_history(id_planview, "DELETE", before, None)
        return None
    except Exception as e:
        return f"Erro: {e}"


# =============================
# Metrics & Helpers
# =============================

def status_entered_at(id_planview: str, current_status: str) -> Optional[dt.datetime]:
    hist = fetch_history(id_planview, limit=200)
    for h in hist:
        after = json_loads(h.get("after_data")) or {}
        before = json_loads(h.get("before_data"))
        if after.get("status") == current_status:
            if before is None or before.get("status") != current_status:
                try: return dt.datetime.fromisoformat(h["changed_at"])
                except: return None
    for h in reversed(hist):
        if h.get("action") == "CREATE":
            try: return dt.datetime.fromisoformat(h["changed_at"])
            except: return None
    return None


def lead_time_days(id_planview: str) -> Optional[int]:
    hist = fetch_history(id_planview, limit=500)
    if not hist: return None
    created_at = None
    done_at = None
    for h in reversed(hist):
        if h.get("action") == "CREATE":
            try: created_at = dt.datetime.fromisoformat(h["changed_at"])
            except: pass
            break
    for h in reversed(hist):
        after = json_loads(h.get("after_data")) or {}
        before = json_loads(h.get("before_data"))
        if after.get("status") == "done" and (before is None or before.get("status") != "done"):
            try: done_at = dt.datetime.fromisoformat(h["changed_at"])
            except: pass
            break
    if created_at and done_at:
        return max(0, (done_at.date() - created_at.date()).days)
    return None


# =============================
# Dialog (Modal) - Edit
# =============================

@st.dialog("Editar projeto", width="large", dismissible=True)
def edit_dialog(id_planview: str):
    proj = fetch_project(id_planview)
    if not proj:
        st.error("Projeto não encontrado.")
        if st.button("Fechar"):
            st.session_state.pop("edit_id", None)
            st.rerun()
        return

    st.caption(f"ID PlanView (não editável): {id_planview}")

    with st.form("form_edit", clear_on_submit=False):
        nome = st.text_input("Nome do Projeto *", value=proj.get("nome") or "")
        descricao = st.text_area("Descrição do projeto", value=proj.get("descricao") or "", height=100)
        
        c_infra = st.columns(2)
        with c_infra[0]:
            request = st.text_input("Request", value=proj.get("request") or "")
        with c_infra[1]:
            change = st.text_input("Change", value=proj.get("change") or "")
            
        gp = st.text_input("Nome do GP", value=proj.get("gp") or "")
        recursos_iris = st.text_input("Recursos", value=proj.get("recursos_iris") or "")

        dcols = st.columns(2)
        with dcols[0]:
            di0 = parse_date(proj.get("data_inicio") or "")
            data_inicio = st.date_input("Data de Inicio", value=di0 if di0 else None)
        with dcols[1]:
            df0 = parse_date(proj.get("data_fim") or "")
            data_fim = st.date_input("Data de Fim", value=df0 if df0 else None)

        st0 = proj.get("status") or "roadmap"
        status = st.selectbox("Etapa atual (Status)", options=STATUSES, index=STATUSES.index(st0) if st0 in STATUSES else 0)

        c1, c2 = st.columns([1, 1])
        with c1:
            save = st.form_submit_button("Salvar alterações", type="primary")
        with c2:
            cancel = st.form_submit_button("Cancelar", type="secondary")

        if cancel:
            st.session_state.pop("edit_id", None)
            st.rerun()

        if save:
            if not nome.strip():
                st.warning("O campo **Nome do Projeto** é obrigatório.")
                st.stop()

            payload = {
                "id_planview": id_planview,
                "nome": nome.strip(),
                "descricao": descricao.strip(),
                "gp": gp.strip(),
                "recursos_iris": recursos_iris.strip(),
                "request": request.strip(),
                "change": change.strip(),
                "data_inicio": date_to_iso(data_inicio),
                "data_fim": date_to_iso(data_fim),
                "status": status,
            }
            err = update_project(id_planview, payload)
            if err: st.error(err)
            else:
                st.success("Projeto atualizado!")
                st.session_state.pop("edit_id", None)
                st.rerun()


# =============================
# UI components
# =============================

def render_filters(projects: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    gps = sorted({(p.get("gp") or "").strip() for p in projects if (p.get("gp") or "").strip()})
    st.session_state.setdefault("f_text", "")
    st.session_state.setdefault("f_status", STATUSES.copy())
    st.session_state.setdefault("f_gp", [])
    st.session_state.setdefault("f_start", None)
    st.session_state.setdefault("f_end", None)

    with st.expander("🔎 Filtros e busca", expanded=False):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
        with c1:
            st.session_state.f_text = st.text_input("Buscar (ID/Nome/Desc/Req/CHG)", value=st.session_state.f_text)
        with c2:
            st.session_state.f_status = st.multiselect("Status", options=STATUSES, default=st.session_state.f_status)
        with c3:
            st.session_state.f_gp = st.multiselect("Nome do GP", options=gps, default=st.session_state.f_gp)
        with c4:
            dc1, dc2 = st.columns(2)
            with dc1: st.session_state.f_start = st.date_input("Data Inicio (Filtro)", value=st.session_state.f_start)
            with dc2: st.session_state.f_end = st.date_input("Data Fim (Filtro)", value=st.session_state.f_end)

    def match_text(p: Dict[str, Any]) -> bool:
        t = (st.session_state.f_text or "").strip().lower()
        if not t: return True
        blob = " ".join([
            (p.get("id_planview") or ""), (p.get("nome") or ""), (p.get("descricao") or ""),
            (p.get("request") or ""), (p.get("change") or "")
        ]).lower()
        return t in blob

    filtered = [p for p in projects if match_text(p) and 
                ((p.get("status") or "roadmap") in (st.session_state.f_status or STATUSES)) and
                (not st.session_state.f_gp or (p.get("gp") or "").strip() in st.session_state.f_gp)]
    
    return filtered, {}


def render_metrics(projects: List[Dict[str, Any]]):
    today = dt.date.today()
    rows = []
    for p in projects:
        pid = p["id_planview"]
        stt = p.get("status") or "roadmap"
        entered = status_entered_at(pid, stt)
        aging = max(0, (today - entered.date()).days) if entered else None
        rows.append({"status": stt, "aging_dias": aging, "lead_time_dias": lead_time_days(pid)})

    df = pd.DataFrame(rows)
    total = len(df)
    done = int((df["status"] == "done").sum()) if total else 0
    
    st.subheader("📈 Métricas")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", str(total))
    c2.metric("WIP", str(total - done))
    c3.metric("Done", str(done))
    
    if total:
        aging_by_status = df.dropna(subset=["aging_dias"]).groupby("status")["aging_dias"].mean()
        aging_by_status = pd.DataFrame({"status": STATUSES}).merge(aging_by_status, on="status", how="left").fillna(0)
        st.bar_chart(aging_by_status.set_index("status"))


def card(project: Dict[str, Any]):
    pid = project["id_planview"]
    nome = project.get("nome", "")
    status_atual = project.get("status") or "roadmap"

    with st.container(border=True):
        cols = st.columns([6, 3, 1, 1])
        with cols[0]:
            st.markdown(f"**{nome}**")
            st.caption(f"ID PlanView: `{pid}`")
            req, chg = project.get("request"), project.get("change")
            if req or chg:
                st.caption(f"Request: {req or '—'} | Change: {chg or '—'}")
        
        with cols[1]:
            new_status = st.selectbox("Mover", options=STATUSES, index=STATUSES.index(status_atual) if status_atual in STATUSES else 0,
                                     key=f"mv_{pid}", label_visibility="collapsed")
        with cols[2]:
            if st.button("✏️", key=f"edit_{pid}"):
                st.session_state["edit_id"] = pid
                st.rerun()
        with cols[3]:
            if st.button("🗑️", key=f"del_{pid}"):
                delete_project(pid)
                st.rerun()

        if new_status != status_atual:
            update_status(pid, new_status)
            st.rerun()

        with st.expander("Detalhes"):
            st.write(f"**Nome do GP:** {project.get('gp') or '—'}")
            st.write(f"**Request:** {project.get('request') or '—'}")
            st.write(f"**Change:** {project.get('change') or '—'}")
            st.write(f"**Recursos:** {project.get('recursos_iris') or '—'}")
            st.write(f"**Data de Inicio:** {project.get('data_inicio') or '—'}")
            st.write(f"**Data de Fim:** {project.get('data_fim') or '—'}")
            
            entered = status_entered_at(pid, status_atual)
            if entered:
                st.markdown(f"**Aging:** {max(0, (dt.date.today() - entered.date()).days)} dia(s)")
            
            if project.get("descricao"):
                st.markdown("**Descrição do projeto:**")
                st.write(project["descricao"])


def main():
    init_db()
    st.title("📌 Kanban - Gerenciamento de Projetos")

    # ---------- Sidebar: Cadastro ----------
    st.sidebar.header("Cadastrar projeto")
    with st.sidebar.form("form_cadastro", clear_on_submit=True):
        id_planview = st.text_input("ID PlanView *")
        nome = st.text_input("Nome do Projeto *")
        descricao = st.text_area("Descrição do projeto")
        
        c_infra = st.columns(2)
        with c_infra[0]: request = st.text_input("Request")
        with c_infra[1]: change = st.text_input("Change")
            
        gp = st.text_input("Nome do GP")
        recursos_iris = st.text_input("Recursos")
        
        dcols = st.columns(2)
        with dcols[0]: data_inicio = st.date_input("Data de Inicio", value=None)
        with dcols[1]: data_fim = st.date_input("Data de Fim", value=None)
        
        status = st.selectbox("Etapa atual (Status)", options=STATUSES)
        if st.form_submit_button("Salvar", type="primary"):
            if not id_planview.strip() or not nome.strip():
                st.warning("Preencha os campos obrigatórios (ID PlanView e Nome do Projeto).")
            else:
                err = insert_project({
                    "id_planview": id_planview.strip(), "nome": nome.strip(), "descricao": descricao.strip(),
                    "gp": gp.strip(), "recursos_iris": recursos_iris.strip(), 
                    "request": request.strip(), "change": change.strip(),
                    "data_inicio": date_to_iso(data_inicio), "data_fim": date_to_iso(data_fim), "status": status
                })
                if err: st.error(err)
                else: st.rerun()

    if st.session_state.get("edit_id"):
        edit_dialog(st.session_state["edit_id"])

    projects_all = fetch_projects()
    projects, _ = render_filters(projects_all)
    render_metrics(projects)
    st.divider()

    # ---------- Board ----------
    by_status = {s: [] for s in STATUSES}
    for p in projects:
        by_status[p.get("status", "roadmap")].append(p)

    rows = [STATUSES[:7], STATUSES[7:]]
    for row in rows:
        cols = st.columns(len(row))
        for idx, status in enumerate(row):
            with cols[idx]:
                st.subheader(f"{status} ({len(by_status[status])})")
                for p in by_status[status]:
                    card(p)

if __name__ == "__main__":
    main()