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
    """Best-effort user detection.

    - In Streamlit Cloud / some enterprise deployments, st.experimental_user may exist.
    - Fallback to OS username.
    """
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
                data_inicio   TEXT,
                data_fim      TEXT,
                status        TEXT NOT NULL
            )
            """
        )
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
            SELECT id_planview, nome, descricao, gp, recursos_iris, data_inicio, data_fim, status
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
            SELECT id_planview, nome, descricao, gp, recursos_iris, data_inicio, data_fim, status
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
                    id_planview, nome, descricao, gp, recursos_iris, data_inicio, data_fim, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    p["id_planview"], p["nome"], p.get("descricao"), p.get("gp"), p.get("recursos_iris"),
                    p.get("data_inicio"), p.get("data_fim"), p.get("status", "roadmap"),
                ),
            )
        # Audit
        log_history(p["id_planview"], "CREATE", None, p)
        return None
    except sqlite3.IntegrityError as e:
        return f"ID duplicado (id_planview já existe): {e}"
    except sqlite3.OperationalError as e:
        return f"Falha operacional/conexão com o banco: {e}"
    except Exception as e:
        return f"Erro inesperado ao salvar: {e}"


def update_project(id_planview: str, payload: Dict[str, Any]) -> Optional[str]:
    try:
        before = fetch_project(id_planview)
        if not before:
            return "Projeto não encontrado para atualização."

        with db_cursor() as cur:
            cur.execute(
                """
                UPDATE projects
                SET nome = ?, descricao = ?, gp = ?, recursos_iris = ?, data_inicio = ?, data_fim = ?, status = ?
                WHERE id_planview = ?
                """,
                (
                    payload.get("nome"), payload.get("descricao"), payload.get("gp"), payload.get("recursos_iris"),
                    payload.get("data_inicio"), payload.get("data_fim"), payload.get("status"), id_planview,
                ),
            )

        after = fetch_project(id_planview)
        # Audit action type
        action = "UPDATE"
        try:
            if before.get("status") != after.get("status"):
                action = "STATUS_CHANGE"
        except Exception:
            pass
        log_history(id_planview, action, before, after)
        return None
    except sqlite3.OperationalError as e:
        return f"Falha operacional/conexão com o banco: {e}"
    except Exception as e:
        return f"Erro inesperado ao atualizar: {e}"


def update_status(id_planview: str, new_status: str) -> Optional[str]:
    try:
        before = fetch_project(id_planview)
        if not before:
            return "Projeto não encontrado para atualizar status."

        with db_cursor() as cur:
            cur.execute(
                "UPDATE projects SET status = ? WHERE id_planview = ?",
                (new_status, id_planview),
            )
        after = fetch_project(id_planview)
        log_history(id_planview, "STATUS_CHANGE", before, after)
        return None
    except sqlite3.OperationalError as e:
        return f"Falha operacional/conexão com o banco: {e}"
    except Exception as e:
        return f"Erro inesperado ao atualizar status: {e}"


def delete_project(id_planview: str) -> Optional[str]:
    try:
        before = fetch_project(id_planview)
        if not before:
            return "Projeto não encontrado para exclusão."

        with db_cursor() as cur:
            cur.execute("DELETE FROM projects WHERE id_planview = ?", (id_planview,))

        log_history(id_planview, "DELETE", before, None)
        return None
    except sqlite3.OperationalError as e:
        return f"Falha operacional/conexão com o banco: {e}"
    except Exception as e:
        return f"Erro inesperado ao excluir: {e}"


# =============================
# Metrics
# =============================

def status_entered_at(id_planview: str, current_status: str) -> Optional[dt.datetime]:
    """Return datetime when the project entered its current status (best-effort).

    We look at history rows (newest->oldest) and find the first row where:
      - after_data.status == current_status
      - and (before_data is None or before_data.status != current_status)

    That row's changed_at is considered the entry moment.
    """
    hist = fetch_history(id_planview, limit=200)
    for h in hist:
        after = json_loads(h.get("after_data")) or {}
        before = json_loads(h.get("before_data"))
        if after.get("status") == current_status:
            if before is None or before.get("status") != current_status:
                try:
                    return dt.datetime.fromisoformat(h["changed_at"])
                except Exception:
                    return None
    # Fallback: creation timestamp
    for h in reversed(hist):
        if h.get("action") == "CREATE":
            try:
                return dt.datetime.fromisoformat(h["changed_at"])
            except Exception:
                return None
    return None


def lead_time_days(id_planview: str) -> Optional[int]:
    """Lead time = from CREATE to first entry into 'done'."""
    hist = fetch_history(id_planview, limit=500)
    if not hist:
        return None

    created_at = None
    done_at = None

    # Find earliest CREATE
    for h in reversed(hist):
        if h.get("action") == "CREATE":
            try:
                created_at = dt.datetime.fromisoformat(h["changed_at"])
            except Exception:
                created_at = None
            break

    # Find first time status became done
    for h in reversed(hist):
        after = json_loads(h.get("after_data")) or {}
        before = json_loads(h.get("before_data"))
        if after.get("status") == "done" and (before is None or before.get("status") != "done"):
            try:
                done_at = dt.datetime.fromisoformat(h["changed_at"])
            except Exception:
                done_at = None
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

    st.caption(f"ID (não editável): {id_planview}")

    # Defaults
    nome0 = proj.get("nome") or ""
    desc0 = proj.get("descricao") or ""
    gp0 = proj.get("gp") or ""
    rec0 = proj.get("recursos_iris") or ""
    di0 = parse_date(proj.get("data_inicio") or "")
    df0 = parse_date(proj.get("data_fim") or "")
    st0 = proj.get("status") or "roadmap"

    with st.form("form_edit", clear_on_submit=False):
        nome = st.text_input("nome *", value=nome0)
        descricao = st.text_area("descricao", value=desc0, height=140)
        gp = st.text_input("gp", value=gp0)
        recursos_iris = st.text_input("recursos_iris", value=rec0)

        dcols = st.columns(2)
        with dcols[0]:
            data_inicio = st.date_input("data_inicio", value=di0 if di0 else None)
        with dcols[1]:
            data_fim = st.date_input("data_fim", value=df0 if df0 else None)

        status = st.selectbox("status", options=STATUSES, index=STATUSES.index(st0) if st0 in STATUSES else 0)

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
                st.warning("O campo **nome** é obrigatório.")
                st.stop()

            payload = {
                "id_planview": id_planview,
                "nome": nome.strip(),
                "descricao": descricao.strip(),
                "gp": gp.strip(),
                "recursos_iris": recursos_iris.strip(),
                "data_inicio": date_to_iso(data_inicio),
                "data_fim": date_to_iso(data_fim),
                "status": status,
            }
            err = update_project(id_planview, payload)
            if err:
                st.error(err)
            else:
                st.success("Projeto atualizado!")
                st.session_state.pop("edit_id", None)
                st.rerun()


# =============================
# UI components
# =============================

def render_filters(projects: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Render filter UI and return filtered projects and filter state."""
    gps = sorted({(p.get("gp") or "").strip() for p in projects if (p.get("gp") or "").strip()})

    # Initialize defaults
    st.session_state.setdefault("f_text", "")
    st.session_state.setdefault("f_status", STATUSES.copy())
    st.session_state.setdefault("f_gp", [])
    st.session_state.setdefault("f_start", None)
    st.session_state.setdefault("f_end", None)

    with st.expander("🔎 Filtros e busca", expanded=False):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
        with c1:
            st.session_state.f_text = st.text_input("Buscar (ID/nome/descrição)", value=st.session_state.f_text)
        with c2:
            st.session_state.f_status = st.multiselect("Status", options=STATUSES, default=st.session_state.f_status)
        with c3:
            st.session_state.f_gp = st.multiselect("GP", options=gps, default=st.session_state.f_gp)
        with c4:
            dc1, dc2 = st.columns(2)
            with dc1:
                st.session_state.f_start = st.date_input("Período (início)", value=st.session_state.f_start)
            with dc2:
                st.session_state.f_end = st.date_input("Período (fim)", value=st.session_state.f_end)

        st.caption("Filtro de período usa sobreposição (projetos sem data são mantidos por padrão).")

    def match_text(p: Dict[str, Any]) -> bool:
        t = (st.session_state.f_text or "").strip().lower()
        if not t:
            return True
        blob = " ".join([
            (p.get("id_planview") or ""),
            (p.get("nome") or ""),
            (p.get("descricao") or ""),
        ]).lower()
        return t in blob

    def match_status(p: Dict[str, Any]) -> bool:
        selected = st.session_state.f_status or []
        if not selected:
            return True
        return (p.get("status") or "roadmap") in selected

    def match_gp(p: Dict[str, Any]) -> bool:
        selected = st.session_state.f_gp or []
        if not selected:
            return True
        return ((p.get("gp") or "").strip() in selected)

    def match_period(p: Dict[str, Any]) -> bool:
        fs: Optional[dt.date] = st.session_state.f_start
        fe: Optional[dt.date] = st.session_state.f_end
        if not fs and not fe:
            return True
        ps = parse_date(p.get("data_inicio") or "")
        pe = parse_date(p.get("data_fim") or "")

        # Keep items with missing dates unless they clearly fall outside
        if fs and pe and pe < fs:
            return False
        if fe and ps and ps > fe:
            return False
        return True

    filtered = [p for p in projects if match_text(p) and match_status(p) and match_gp(p) and match_period(p)]

    filter_state = {
        "text": st.session_state.f_text,
        "status": st.session_state.f_status,
        "gp": st.session_state.f_gp,
        "start": st.session_state.f_start,
        "end": st.session_state.f_end,
    }
    return filtered, filter_state


def render_metrics(projects: List[Dict[str, Any]]):
    """Show Aging per column and Lead Time metrics."""
    today = dt.date.today()

    # Compute per-project metrics
    rows = []
    for p in projects:
        pid = p["id_planview"]
        stt = p.get("status") or "roadmap"
        entered = status_entered_at(pid, stt)
        aging = None
        if entered:
            aging = max(0, (today - entered.date()).days)
        lt = lead_time_days(pid)
        rows.append({
            "id_planview": pid,
            "nome": p.get("nome"),
            "status": stt,
            "aging_dias": aging,
            "lead_time_dias": lt,
            "gp": p.get("gp") or "",
        })

    df = pd.DataFrame(rows)
    total = len(df)
    done = int((df["status"] == "done").sum()) if total else 0
    wip = total - done

    avg_lead_done = None
    if total and done:
        avg_lead_done = float(df.loc[df["status"] == "done", "lead_time_dias"].dropna().mean())

    avg_aging_wip = None
    if total and wip:
        avg_aging_wip = float(df.loc[df["status"] != "done", "aging_dias"].dropna().mean())

    st.subheader("📈 Métricas")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", str(total))
    c2.metric("WIP (≠ done)", str(wip))
    c3.metric("Done", str(done))
    c4.metric("Lead time médio (done, dias)", "—" if avg_lead_done is None else f"{avg_lead_done:.1f}")

    c5, c6 = st.columns(2)
    c5.metric("Aging médio (WIP, dias)", "—" if avg_aging_wip is None else f"{avg_aging_wip:.1f}")

    # Aging by status
    if total:
        aging_by_status = (
            df.dropna(subset=["aging_dias"])
              .groupby("status", as_index=False)["aging_dias"].mean()
        )
        # Ensure all statuses appear
        aging_by_status = pd.DataFrame({"status": STATUSES}).merge(aging_by_status, on="status", how="left")
        aging_by_status["aging_dias"] = aging_by_status["aging_dias"].fillna(0)

        st.caption("Aging (dias) = dias desde a entrada no status atual (com base no histórico).")
        st.bar_chart(aging_by_status.set_index("status"))

    # Lead time table for done
    if done:
        st.caption("Lead time (dias) = do CREATE até a primeira entrada em 'done'.")
        st.dataframe(
            df.loc[df["status"] == "done", ["id_planview", "nome", "gp", "lead_time_dias"]]
              .sort_values("lead_time_dias", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


def card(project: Dict[str, Any]):
    pid = project["id_planview"]
    nome = project.get("nome", "")
    descricao = project.get("descricao") or ""
    status_atual = project.get("status") or "roadmap"

    with st.container(border=True):
        cols = st.columns([6, 3, 1, 1])
        with cols[0]:
            st.markdown(f"**{nome}**")
            st.caption(f"ID: `{pid}`")
        with cols[1]:
            new_status = st.selectbox(
                "Mover para",
                options=STATUSES,
                index=STATUSES.index(status_atual) if status_atual in STATUSES else 0,
                key=f"mv_{pid}",
                label_visibility="collapsed",
            )
        with cols[2]:
            if st.button("✏️", key=f"edit_{pid}", type="secondary", help="Editar projeto"):
                st.session_state["edit_id"] = pid
                st.rerun()
        with cols[3]:
            if st.button("🗑️", key=f"del_{pid}", type="secondary", help="Excluir Projeto"):
                err = delete_project(pid)
                if err:
                    st.error(err)
                else:
                    st.toast("Projeto excluído", icon="🗑️")
                    st.rerun()

        # Status change
        if new_status != status_atual:
            err = update_status(pid, new_status)
            if err:
                st.error(err)
            else:
                st.rerun()

        # Main content (clean board)
        if descricao.strip():
            st.write(descricao if len(descricao) <= 180 else (descricao[:177] + "..."))

        with st.expander("Detalhes"):
            gp = project.get("gp") or ""
            recursos = project.get("recursos_iris") or ""
            di = project.get("data_inicio") or ""
            df = project.get("data_fim") or ""

            if gp:
                st.markdown(f"**GP:** {gp}")
            if recursos:
                st.markdown(f"**Recursos IRIS:** {recursos}")

            if di or df:
                st.markdown("**Cronograma:**")
                st.write(f"Início: {di or '—'}")
                st.write(f"Fim: {df or '—'}")

            # Status aging (per card)
            entered = status_entered_at(pid, status_atual)
            if entered:
                aging_days = max(0, (dt.date.today() - entered.date()).days)
                st.markdown(f"**Aging no status atual:** {aging_days} dia(s)")

            # Optional: show last history items
            hist = fetch_history(pid, limit=8)
            if hist:
                st.markdown("**Últimos eventos (auditoria):**")
                view = []
                for h in hist:
                    view.append({
                        "ação": h.get("action"),
                        "quando": h.get("changed_at"),
                        "usuário": h.get("changed_by"),
                    })
                st.dataframe(pd.DataFrame(view), use_container_width=True, hide_index=True)

            if descricao.strip():
                st.markdown("**Descrição completa:**")
                st.write(descricao)


# =============================
# App
# =============================

def main():
    init_db()

    st.title("📌 Kanban - Gerenciamento de Projetos")

    # ---------- Sidebar: Cadastro ----------
    st.sidebar.header("Cadastrar projeto")

    with st.sidebar.form("form_cadastro", clear_on_submit=True):
        id_planview = st.text_input("id_planview *", placeholder="Ex.: PV-12345")
        nome = st.text_input("nome *", placeholder="Nome do projeto")
        descricao = st.text_area("descricao", placeholder="Descrição do projeto", height=110)
        gp = st.text_input("gp", placeholder="Gestor do projeto")
        recursos_iris = st.text_input("recursos_iris", placeholder="Ex.: Dev1; Dev2; QA")

        dcols = st.columns(2)
        with dcols[0]:
            data_inicio = st.date_input("data_inicio", value=None)
        with dcols[1]:
            data_fim = st.date_input("data_fim", value=None)

        status = st.selectbox("status", options=STATUSES, index=0)

        submitted = st.form_submit_button("Salvar", type="primary")

        if submitted:
            if not id_planview.strip() or not nome.strip():
                st.warning("Os campos **id_planview** e **nome** são obrigatórios. Preencha-os para salvar.")
            else:
                payload = {
                    "id_planview": id_planview.strip(),
                    "nome": nome.strip(),
                    "descricao": descricao.strip(),
                    "gp": gp.strip(),
                    "recursos_iris": recursos_iris.strip(),
                    "data_inicio": date_to_iso(data_inicio),
                    "data_fim": date_to_iso(data_fim),
                    "status": status,
                }
                err = insert_project(payload)
                if err:
                    st.error(err)
                else:
                    st.success("Projeto salvo com sucesso!")
                    st.rerun()

    st.divider()

    # ---------- Open edit modal if requested ----------
    if st.session_state.get("edit_id"):
        edit_dialog(st.session_state["edit_id"])

    # ---------- Data load + filters ----------
    projects_all = fetch_projects()
    projects, _ = render_filters(projects_all)

    # ---------- Metrics ----------
    render_metrics(projects)
    st.divider()

    # ---------- Board ----------
    by_status: Dict[str, List[Dict[str, Any]]] = {s: [] for s in STATUSES}
    for p in projects:
        s = p.get("status") or "roadmap"
        if s not in by_status:
            s = "roadmap"
        by_status[s].append(p)

    # 14 colunas -> 2 linhas de 7
    rows = [STATUSES[:7], STATUSES[7:]]

    for row in rows:
        cols = st.columns(len(row))
        for idx, status in enumerate(row):
            with cols[idx]:
                count = len(by_status.get(status, []))
                st.subheader(f"{status} ({count})")
                for p in by_status.get(status, []):
                    card(p)


if __name__ == "__main__":
    main()
