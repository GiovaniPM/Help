# App Streamlit - Registro e Acompanhamento de Incidentes de Migração

Aplicação criada para implementar a lógica da planilha **Planilha_Acompanhamento_Incidentes_Migracao.xlsx**.

## Funcionalidades

- Cadastro e edição de incidentes no padrão `INC-IRIS-0001`.
- Listas controladas para ambiente, fase, tipo, severidade, prioridade, status, impacto, comunicação e time responsável.
- Cálculo automático de:
  - Duração em horas.
  - Aging aberto em horas.
  - Incidentes vencidos pelo prazo.
  - RCA pendente.
- Dashboard executivo com indicadores principais.
- Gráficos por status, severidade e tipo.
- Heatmap Ambiente x Severidade.
- Consulta com filtros.
- Tela de RCA e Auditoria.
- Importação/Exportação em Excel.
- Persistência local em SQLite.

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Observações

- O banco SQLite `incidentes_migracao.db` será criado automaticamente na primeira execução.
- Para popular exemplos semelhantes aos da planilha, marque a opção **Carregar exemplos da planilha** no menu lateral.
- A exportação gera um Excel com as abas: Registro de Incidentes, Listas, Dashboard e Guia de Uso.
