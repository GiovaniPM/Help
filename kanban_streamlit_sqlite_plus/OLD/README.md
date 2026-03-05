# Kanban de Projetos (Streamlit + SQLite) — PLUS

Esta versão inclui:
- **Trilha de auditoria** em `project_history` (antes/depois, timestamp, usuário)
- **Edição completa** via **modal** (`st.dialog`) a partir de cada card
- **Filtros e busca** por texto (ID/nome/descrição), GP, status e período
- **Métricas**: Aging por coluna e Lead Time (do CREATE até `done`)

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Banco

- `projects`: dados dos projetos
- `project_history`: trilha de auditoria

O arquivo `kanban_projects.db` é criado automaticamente.
