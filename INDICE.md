# Índice do repositório Help

Catálogo do conteúdo deste repositório: guias, configurações de ambiente, scripts utilitários e projetos pessoais.

> Para os links de referência (Bash, ANSI, Git, cURL etc.), veja o [README](./README.md).

## Sumário

- [Documentação e guias](#documentação-e-guias)
- [Projetos](#projetos)
  - [Clipper: pontes para Firebird e Oracle](#clipper-pontes-para-firebird-e-oracle)
  - [IRIS: InterSystems IRIS em Docker e Kubernetes](#iris-intersystems-iris-em-docker-e-kubernetes)
  - [JIRA: automação de sprints](#jira-automação-de-sprints)
  - [Aplicações Streamlit](#aplicações-streamlit)
  - [GTD: gerenciador de tarefas](#gtd-gerenciador-de-tarefas)
  - [Go: wiki de exemplo](#go-wiki-de-exemplo)
- [Docker](#docker)
- [Scripts](#scripts)
- [Configurações](#configurações)
- [Python: estudos e utilitários](#python-estudos-e-utilitários)
- [Arquivos na raiz](#arquivos-na-raiz)

---

## Documentação e guias

| Arquivo | Conteúdo |
|---|---|
| [README.md](./README.md) | Página inicial com links de referência (Bash, ANSI escape codes, cURL, emojis, bookmarks) |
| [git help.md](./git%20help.md) | Guia de comandos Git, com diagrama da arquitetura ([GitArchitecture01.jpg](./GitArchitecture01.jpg)) |
| [How to Install.md](./How%20to%20Install.md) | Como instalar o ambiente: estrutura de diretórios e scripts `setup`, `download` e `upload` |
| [docker/README.md](./docker/README.md) | Catálogo das imagens Docker, com link, comando de pull e script de empacotamento de cada uma |

## Projetos

### Clipper: pontes para Firebird e Oracle

Bibliotecas que permitem ao **Clipper 5.2 (DOS, 16 bits)** consultar bancos modernos. Uma ponte em C executa a consulta e grava o resultado em um **DBF temporário**, que o Clipper abre com `dbUseArea()`. A partir daí funcionam os comandos de sempre (`SKIP`, `SEEK`, `INDEX ON`, `BROWSE`...).

| Pasta | Descrição |
|---|---|
| [Clipper/Firebird](./Clipper/Firebird/README.md) | `FIREBIRD.LIB` + `FBBRIDGE.EXE` (API `ibase.h`/`fbclient`) |
| [Clipper/Oracle](./Clipper/Oracle/README.md) | `ORACLE.LIB` + ponte baseada em ODPI-C |

Cada pasta contém a biblioteca Clipper (`.PRG`/`.CH`), o `BUILD.BAT`, o programa de teste `TESTE.PRG` e a pasta `bridge/` com o código C, os testes (`test_bridge.c`) e o `CMakeLists.txt`.

### IRIS: InterSystems IRIS em Docker e Kubernetes

Documentos de arquitetura de solução (em Markdown e PDF) para subir o InterSystems IRIS localmente:

| Rota | Documento | Status |
|---|---|---|
| Docker (container único) | [IRIS-Docker-Local-Arquitetura-Solucao.md](./IRIS/Docker/IRIS-Docker-Local-Arquitetura-Solucao.md) | Validado |
| Kubernetes, Rota 1 (manifests nativos) | [IRIS-Kubernetes-Local-Arquitetura-Solucao.md](./IRIS/Kubernets/Rota%201/IRIS-Kubernetes-Local-Arquitetura-Solucao.md) | — |
| Kubernetes, Rota 2 (operador IKO via Helm) | [IRIS-Kubernetes-IKO-Arquitetura-Solucao.md](./IRIS/Kubernets/Rota%202/IRIS-Kubernetes-IKO-Arquitetura-Solucao.md) | Proposto |

As pastas trazem também os manifests (`iris-deployment.yaml`, `iris-pvc.yaml`, `iris-service.yaml`, `iris-cluster.yaml`, `iris-operator-values.yaml`) e os diagramas em SVG.

### JIRA: automação de sprints

Automação da gestão de sprints no Jira a partir de uma planilha Excel de acompanhamento.

- [JIRA/Python](./JIRA/Python/): `processa_refatorado.py` lê a planilha e cria Épicos, Estórias e Tarefas no Jira, depois grava na planilha os IDs gerados. Usa a biblioteca própria `jiralib.py` e as credenciais do `setup.json`. Inclui manuais (`.docx`), planilhas de sprint, a pasta `old/` com versões anteriores e o [TODO.md](./JIRA/Python/TODO.md).
- [JIRA/Jira Cloud](./JIRA/Jira%20Cloud/): prompt que substitui o script Python na criação de cards a partir da planilha.
- [Timeline.txt](./JIRA/Timeline.txt) / [Timeline.svg](./JIRA/Timeline.svg): motivações e linha do tempo da iniciativa, de 2025 a 2026 (planilha, Copilot, Python, Jira Cloud + Rovo).
- [Problemas.txt](./JIRA/Problemas.txt): diagnóstico do processo ágil, com pontos de atenção e recomendações.
- [arquitetura_excel_jira.svg](./JIRA/arquitetura_excel_jira.svg): diagrama da integração Excel → Jira.

### Aplicações Streamlit

Todas usam SQLite e rodam com:

```bash
pip install -r requirements.txt
streamlit run app.py
```

| Pasta | Descrição |
|---|---|
| [Projeto_Kanban](./Projeto_Kanban/) | Kanban para gerenciamento de projetos |
| [kanban_streamlit_sqlite_plus](./kanban_streamlit_sqlite_plus/) | Kanban "Plus": trilha de auditoria, edição em modal, filtros, métricas de aging e lead time |
| [migracao](./migracao/README.md) | Registro e acompanhamento de incidentes de migração: dashboard, heatmap, RCA e importação/exportação em Excel |
| [Torrent](./Torrent/) | Cliente de torrent com interface Streamlit sobre `libtorrent` |

### GTD: gerenciador de tarefas

Aplicação no método *Getting Things Done*, em duas versões:

- [GTD/Python](./GTD/Python/): Tkinter + SQLite (`gtd_app.py`).
- [GTD/Java](./GTD/Java/): JavaFX + SQLite JDBC (`GtdAppJavaFX.java`), com `compila.bat` e `executa.bat`.

### Go: wiki de exemplo

[go/](./go/): wiki simples (`wiki.go`, baseada no tutorial oficial do Go) com templates `edit.html`/`view.html` e páginas `.txt`, além de testes com JSON.

## Docker

A pasta [docker/](./docker/) tem um `Dockerfile`/`build.bat` por imagem:

| Categoria | Imagens |
|---|---|
| Bancos de dados | DB2, Elasticsearch, Firebird, IRIS, MariaDB, MongoDB, Oracle, Postgres, Redis, SQL Server |
| Mensageria e cache | Memcached, RabbitMQ, ZeroMQ |
| Aplicações | ADEmpire, BookStack, Camunda, Compiere, SickRage |
| Sistemas e desktops | Debian RDP, Win95 |
| Desenvolvimento | Python basic, Python Win, python-flask, nginx test, composetest, dv, home |

Os arquivos `*Connection.png` mostram as configurações de conexão de cada banco, e o [runbuild.bat](./docker/runbuild.bat) automatiza os builds.

## Scripts

| Pasta | Conteúdo |
|---|---|
| [scripts/git](./scripts/git/) | Scripts Bash de `setup`, `download`, `upload`, `deploy`, `build`, sincronização, histórico e backup (repositórios, gists, Docker) |
| [scripts/docker](./scripts/docker/) | Menu de manutenção (`docker-menu.bat`) e backup de containers |
| [scripts/WindowsTerminal](./scripts/WindowsTerminal/) | `settings.json` do Windows Terminal, ícones e atalhos `docker*.cmd` (exec, logs, IP, inspect, network) |
| [scripts/vscode](./scripts/vscode/) / [scripts/codium](./scripts/codium/) | Backup da lista de extensões por máquina |
| [scripts/Install Tools](./scripts/Install%20Tools/) | Instaladores (Chocolatey, GanttPlanner, SQL Power Architect, Yaoqiang, ARIS etc.) |
| [scripts/misc](./scripts/misc/) | Utilitários de terminal: tabela de 256 cores, tabela ASCII, desenho de caixas |
| [scripts/Rexx](./scripts/Rexx/) | Exemplos em REXX (`HelloWorld.rex`, `Menu.rex`) |
| [scripts/dos](./scripts/dos/) | Configuração do DOSBox e utilitários diversos |
| [scripts/ShoutCast](./scripts/ShoutCast/) | Configuração de servidor SHOUTcast |
| [scripts/chocolatey](./scripts/chocolatey/) | Lista de pacotes do Chocolatey |

## Configurações

| Pasta | Conteúdo |
|---|---|
| [config/bash windows](./config/bash%20windows/) | Dotfiles do Git Bash no Windows (`.bashrc`, `.bash_aliases`, `.gitconfig`, `.wslconfig` etc.) |
| [config/ubuntu](./config/ubuntu/) | Dotfiles do Ubuntu/WSL |
| [config/JDE](./config/JDE/) | Arquivos `jde.ini`/`jas.ini` do JD Edwards |
| [config/BD](./config/BD/) / [config/docker](./config/docker/) | Scripts para iniciar serviços de banco e montar volumes |
| [.devcontainer](./.devcontainer/) / [.vscode](./.vscode/) | Configuração do Dev Container e do VS Code |

## Python: estudos e utilitários

A pasta [python/](./python/) reúne exemplos e ferramentas avulsas:

- **IA:** `copilot_prompt.py` (Azure OpenAI) e `gemini_prompt.py` (Google Gemini) enviam um prompt e salvam a resposta em `.txt`; `instalar_dependencias.py` instala os pacotes necessários.
- **Utilitários:** `file_crypto.py` (criptografia de arquivos com AES/Fernet), `split.py` + `Split.bat`/`Split.ps1` (divide arquivos grandes), `extract-url.py` (baixa arquivos linkados em uma página), `relatorio1.py` (relatório do Jira).
- **APIs públicas:** `cep.py` / `consulta_cep.py` (CEP), `cnpj.py` (CNPJ), `exchangerate.py` (câmbio).
- **Oracle / JDE:** `Teste_F0005.py` (consulta de UDC), `Teste_F00092.py`, `importcx_Oracle.py`.
- **Gráficos:** `grafico*.py` (Bokeh) e `plotly*.py` (Plotly).
- **Interfaces:** `login.py` e `rb2.py` (CustomTkinter), `rb.py` (Tkinter), `input.py` (curses), `hello.py` (Flask); inclui uma cópia do [CustomTkinter](./python/CustomTkinter-master/).
- **Estudos:** orientação a objetos (`funcionario.py`, `gerente.py`, `obj1.py`, `example01.py`), `primo.py` (threads), `estimate_pi.py` (Monte Carlo), `testeml1.py` (TensorFlow), `WordsInString.py`.

## Arquivos na raiz

| Arquivo | Descrição |
|---|---|
| `Comenta JDE.bat` | Gera um bloco de comentário padronizado (usuário, máquina, data) para código JDE, usando `boxes` |
| `bookmarks 20190919.html` | Exportação de favoritos do navegador |
| `git.set` | Configuração do Git |
| `teste.py` | Busca de raiz pelo método da bisseção |
| `saida.json`, `sample.txt`, `emails.txt`, `download.per`, `upload.per` | Arquivos auxiliares e de teste |
| `c/hello.c` | Hello world em C |
| `build/` | Saída de build do CMake (ponte Oracle/ODPI-C) |
