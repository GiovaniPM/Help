import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sqlite3
from enum import Enum
import os
import logging
from typing import List, Dict, Optional, Tuple

# --- 0. Configuracao do Logging ---
# Configura o logging para ser mais profissional que 'print()'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- 1. Modelo de Dados e Enum ---

class TaskStatus(Enum):
    """
    Enum para representar o status/lista de uma tarefa no GTD.
    """
    INBOX = "Caixa de Entrada"
    NEXT_ACTION = "Proximas Acoes"
    PROJECT = "Projetos"
    WAITING_FOR = "Esperando"
    SOMEDAY_MAYBE = "Algum Dia/Talvez"
    DONE = "Concluido" # Nao usado nas abas, mas util para o DB

class Task:
    """
    Representa uma unica tarefa (Modelo de Dados).
    """
    def __init__(self, id: int, description: str, status: TaskStatus, context: str, project: str) -> None:
        self.id = id
        self.description = description
        self.status = status
        self.context = context
        self.project = project

    def __str__(self) -> str:
        """
        Define como a tarefa sera exibida no Listbox.
        """
        parts: List[str] = []
        if self.context:
            parts.append(f"[{self.context}]")
        
        parts.append(self.description)
        
        if self.project:
            parts.append(f"(Projeto: {self.project})")
            
        return " ".join(parts)

    def __repr__(self) -> str:
        """ Representacao para debugging. """
        return f"<Task(id={self.id}, status='{self.status.name}', desc='{self.description[:20]}...')>"

# --- 2. Acesso ao Banco de Dados ---

class DatabaseHelper:
    """
    Classe auxiliar para interagir com o banco de dados SQLite.
    Centraliza toda a logica de SQL.
    """
    DB_NAME = "gtd_app_py.db"
    
    # Constantes SQL para melhor legibilidade e manutencao
    SQL_CREATE_TABLES = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        context TEXT,
        project TEXT
    );
    """
    SQL_INSERT_TASK = "INSERT INTO tasks(description, status, context, project) VALUES(?,?,?,?)"
    SQL_UPDATE_TASK = "UPDATE tasks SET description = ?, status = ?, context = ?, project = ? WHERE id = ?"
    SQL_DELETE_TASK = "DELETE FROM tasks WHERE id = ?"
    SQL_GET_BY_STATUS = "SELECT * FROM tasks WHERE status = ?"


    def __init__(self) -> None:
        """ Inicializa o helper e garante que a tabela exista. """
        self.create_tables()

    def connect(self) -> sqlite3.Connection:
        """ Retorna uma conexao com o banco de dados. """
        return sqlite3.connect(self.DB_NAME)

    def create_tables(self) -> None:
        """ Cria a tabela 'tasks' se ela nao existir. """
        try:
            with self.connect() as conn:
                conn.execute(self.SQL_CREATE_TABLES)
        except sqlite3.Error as e:
            logging.error(f"Erro ao criar tabela: {e}")

    def insert_task(self, description: str) -> Optional[Task]:
        """ Insere uma nova tarefa na Caixa de Entrada. Retorna o objeto Task. """
        status = TaskStatus.INBOX.name # Salva o nome do enum (ex: "INBOX")
        
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(self.SQL_INSERT_TASK, (description, status, "", ""))
                conn.commit()
                new_id = cursor.lastrowid
                if new_id:
                    return Task(new_id, description, TaskStatus.INBOX, "", "")
                return None
        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir tarefa: {e}")
            return None

    def update_task(self, task: Task) -> None:
        """ Atualiza uma tarefa existente no banco de dados. """
        params = (task.description, task.status.name, task.context, task.project, task.id)
        
        try:
            with self.connect() as conn:
                conn.execute(self.SQL_UPDATE_TASK, params)
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar tarefa: {e}")

    def delete_task(self, task_id: int) -> None:
        """ Exclui uma tarefa do banco de dados pelo ID. """
        try:
            with self.connect() as conn:
                conn.execute(self.SQL_DELETE_TASK, (task_id,))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao excluir tarefa: {e}")

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """ Busca todas as tarefas com um status especifico. """
        tasks: List[Task] = []
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                rows = cursor.execute(self.SQL_GET_BY_STATUS, (status.name,)).fetchall()
                
                for row in rows:
                    tasks.append(Task(
                        id=row[0], 
                        description=row[1], 
                        status=TaskStatus[row[2]], # Converte string de volta para Enum
                        context=row[3], 
                        project=row[4]
                    ))
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar tarefas: {e}")
        return tasks

# --- 3. Aplicativo Principal (GUI com Tkinter) ---

class GtdApp(tk.Tk):
    """
    Classe principal da aplicacao GUI.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.title("Aplicativo GTD (Python + Tkinter)")
        self.minsize(700, 500)
        
        self.db_helper: DatabaseHelper = DatabaseHelper()
        
        # Dicionarios para guardar widgets e dados
        self.list_widgets: Dict[TaskStatus, tk.Listbox] = {}
        self.tasks_data: Dict[TaskStatus, List[Task]] = {}

        # Referencias de widgets que precisamos acessar
        self.capture_entry: ttk.Entry
        self.notebook: ttk.Notebook
        self.inbox_context_menu: tk.Menu
        self.list_context_menu: tk.Menu # Menu para as outras listas
        self.last_clicked_listbox: Optional[tk.Listbox] = None # Para saber qual listbox foi clicado

        # Inicializa a UI
        self._create_widgets()
        self._create_inbox_context_menu()
        self._create_list_context_menu() # Novo menu
        self.load_all_lists()
        
        logging.info("Aplicativo GTD iniciado com sucesso.")

    def _create_widgets(self) -> None:
        """Cria os componentes principais da UI."""
        
        # 1. Area de Captura (Topo)
        capture_frame = ttk.Frame(self, padding="10")
        capture_frame.pack(side=tk.TOP, fill=tk.X)
        
        capture_label = ttk.Label(capture_frame, text="Capturar:")
        capture_label.pack(side=tk.LEFT)
        
        self.capture_entry = ttk.Entry(capture_frame)
        self.capture_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # Binda a tecla Enter para capturar a tarefa
        self.capture_entry.bind("<Return>", lambda event: self.capture_task())
        
        capture_button = ttk.Button(capture_frame, text="Adicionar a Caixa de Entrada", command=self.capture_task)
        capture_button.pack(side=tk.LEFT)

        # 2. Abas com as Listas (Centro)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5, padx=5)

        for status in TaskStatus:
            if status == TaskStatus.DONE:
                continue
                
            tab_frame = ttk.Frame(self.notebook, padding="5")
            self.notebook.add(tab_frame, text=status.value)
            
            # Adiciona Scrollbar
            scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL)
            listbox = tk.Listbox(tab_frame, yscrollcommand=scrollbar.set, height=15, exportselection=False)
            scrollbar.config(command=listbox.yview)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Guarda os widgets e inicializa os dados
            self.list_widgets[status] = listbox
            self.tasks_data[status] = []

            # Adiciona o menu de contexto apropriado
            if status == TaskStatus.INBOX:
                listbox.bind("<Button-3>", self._show_inbox_context_menu) # Windows/Linux
                listbox.bind("<Button-2>", self._show_inbox_context_menu) # macOS
            else:
                listbox.bind("<Button-3>", self._show_list_context_menu) # Windows/Linux
                listbox.bind("<Button-2>", self._show_list_context_menu) # macOS

    def _create_inbox_context_menu(self) -> None:
        """ Cria o menu de clique com o botao direito para a Caixa de Entrada. """
        self.inbox_context_menu = tk.Menu(self, tearoff=0)
        
        self.inbox_context_menu.add_command(
            label="Mover para Proximas Acoes",
            command=lambda: self.process_task(TaskStatus.NEXT_ACTION)
        )
        self.inbox_context_menu.add_command(
            label="Mover para Projetos",
            command=lambda: self.process_task(TaskStatus.PROJECT)
        )
        self.inbox_context_menu.add_command(
            label="Mover para Esperando",
            command=lambda: self.process_task(TaskStatus.WAITING_FOR)
        )
        self.inbox_context_menu.add_command(
            label="Mover para Algum Dia/Talvez",
            command=lambda: self.process_task(TaskStatus.SOMEDAY_MAYBE)
        )
        self.inbox_context_menu.add_separator()
        self.inbox_context_menu.add_command(
            label="Excluir (Lixo)",
            command=self.delete_task
        )
        
        # A associacao (bind) foi movida para _create_widgets()

    def _show_inbox_context_menu(self, event: tk.Event) -> None:
        """ Exibe o menu de contexto da Caixa de Entrada na posicao do clique. """

    def _show_inbox_context_menu(self, event: tk.Event) -> None:
        """ Exibe o menu de contexto na posicao do clique. """
        listbox = self.list_widgets[TaskStatus.INBOX]
        
        # Seleciona o item sob o cursor antes de mostrar o menu
        listbox.select_clear(0, tk.END)
        index = listbox.nearest(event.y)
        if index != -1:
            listbox.select_set(index)
            listbox.activate(index)
            self.inbox_context_menu.post(event.x_root, event.y_root)

    def _create_list_context_menu(self) -> None:
        """ Cria o menu de clique com o botao direito para as listas padrao (Nao-Inbox). """
        self.list_context_menu = tk.Menu(self, tearoff=0)
        
        self.list_context_menu.add_command(
            label="Marcar como Concluido",
            # Usamos lambda para passar o listbox que foi clicado
            command=lambda: self._mark_task_as_done(self.last_clicked_listbox)
        )
        self.list_context_menu.add_separator()
        self.list_context_menu.add_command(
            label="Excluir Tarefa",
            command=lambda: self._delete_task_from_list(self.last_clicked_listbox)
        )

    def _show_list_context_menu(self, event: tk.Event) -> None:
        """ Exibe o menu de contexto padrao na posicao do clique. """
        # Identifica qual listbox foi clicado
        listbox = event.widget
        self.last_clicked_listbox = listbox # Armazena para os comandos do menu
        
        # Seleciona o item sob o cursor
        listbox.select_clear(0, tk.END)
        index = listbox.nearest(event.y)
        if index != -1:
            listbox.select_set(index)
            listbox.activate(index)
            self.list_context_menu.post(event.x_root, event.y_root)

    # --- Metodos de Logica de Negocio e UI ---

    def load_all_lists(self) -> None:
        """ Carrega (ou recarrega) todas as listas do banco de dados para a UI. """
        logging.info("Carregando tarefas do banco de dados...")
        for status in self.list_widgets.keys():
            listbox = self.list_widgets[status]
            
            # Limpa a UI e os dados locais
            listbox.delete(0, tk.END)
            self.tasks_data[status] = []
            
            # Busca tarefas do DB
            tasks = self.db_helper.get_tasks_by_status(status)
            
            # Preenche a UI
            for task in tasks:
                self._add_task_to_ui(task)

    def capture_task(self) -> None:
        """ (Etapa 1: Capturar) Pega o texto do campo e salva no DB. """
        description = self.capture_entry.get().strip()
        if not description:
            messagebox.showwarning("Descricao Vazia", "A descricao nao pode estar vazia.", parent=self)
            return

        new_task = self.db_helper.insert_task(description)
        if new_task:
            self._add_task_to_ui(new_task)
            self.capture_entry.delete(0, tk.END)
            logging.info(f"Tarefa capturada: '{description}'")
        else:
            messagebox.showerror("Erro de Banco de Dados", "Nao foi possivel salvar a tarefa.", parent=self)

    def process_task(self, new_status: TaskStatus) -> None:
        """ Logica principal para processar um item da Caixa de Entrada. """
        task = self._get_selected_inbox_task()
        if not task:
            return

        context = task.context
        project = task.project
        original_status = task.status # Guardamos para saber de onde remover (INBOX)
        
        if new_status == TaskStatus.NEXT_ACTION:
            context = simpledialog.askstring("Contexto", 
                                             "Digite o contexto (ex: @casa, @rua):",
                                             initialvalue=context, parent=self) or context
        elif new_status == TaskStatus.PROJECT:
            project = simpledialog.askstring("Projeto", 
                                             "Digite o nome do projeto:",
                                             initialvalue=task.description, parent=self) or task.description

        # Atualiza o objeto Task
        task.status = new_status
        task.context = context
        task.project = project
        
        # Salva no DB
        self.db_helper.update_task(task)

        # Move entre as listas da UI de forma atomica
        self._remove_task_from_ui(task, original_status)
        self._add_task_to_ui(task)
        logging.info(f"Tarefa {task.id} processada para {new_status.name}")

    def delete_task(self) -> None:
        """ Exclui a tarefa selecionada da Caixa de Entrada. """
        task = self._get_selected_inbox_task()
        if not task:
            return

        # Confirma exclusao
        if messagebox.askyesno("Excluir Tarefa", 
                               f"Tem certeza que deseja excluir?\n\n'{task.description}'",
                               parent=self):
            
            # Exclui do DB
            self.db_helper.delete_task(task.id)
            
            # Remove da UI
            self._remove_task_from_ui(task, TaskStatus.INBOX)
            logging.info(f"Tarefa {task.id} excluida.")

    def _mark_task_as_done(self, listbox: Optional[tk.Listbox]) -> None:
        """ Marca a tarefa selecionada no listbox fornecido como CONCLUIDO. """
        if not listbox:
            return
            
        result = self._get_selected_task_from_listbox(listbox)
        if not result:
            return

        task, original_status = result
        
        # Atualiza o objeto Task
        task.status = TaskStatus.DONE
        
        # Salva no DB
        self.db_helper.update_task(task)

        # Remove da UI
        self._remove_task_from_ui(task, original_status)
        logging.info(f"Tarefa {task.id} marcada como concluida.")

    def _delete_task_from_list(self, listbox: Optional[tk.Listbox]) -> None:
        """ Exclui a tarefa selecionada do listbox fornecido (Nao-Inbox). """
        if not listbox:
            return
            
        result = self._get_selected_task_from_listbox(listbox)
        if not result:
            return

        task, original_status = result

        if messagebox.askyesno("Excluir Tarefa", 
                               f"Tem certeza que deseja excluir?\n\n'{task.description}'",
                               parent=self):
            
            # Exclui do DB
            self.db_helper.delete_task(task.id)
            
            # Remove da UI
            self._remove_task_from_ui(task, original_status)
            logging.info(f"Tarefa {task.id} excluida de {original_status.name}.")

    # --- Metodos Auxiliares de UI ---

    def _add_task_to_ui(self, task: Task) -> None:
        """Adiciona uma tarefa a lista e ao widget da UI corretos."""
        status = task.status
        if status == TaskStatus.DONE or status not in self.list_widgets:
            return
        
        self.tasks_data[status].append(task)
        self.list_widgets[status].insert(tk.END, task)

    def _remove_task_from_ui(self, task: Task, from_status: TaskStatus) -> None:
        """Remove uma tarefa de uma lista e widget da UI especificos."""
        if from_status not in self.tasks_data:
            return
            
        try:
            # Encontra o indice pelo objeto, e mais robusto
            task_index = self.tasks_data[from_status].index(task)
            self.tasks_data[from_status].pop(task_index)
            self.list_widgets[from_status].delete(task_index)
        except ValueError:
            # Isso pode acontecer se as listas estiverem dessincronizadas
            logging.warning(f"Tentativa de remover tarefa nao encontrada na UI: {task.id}")
            # Tenta recarregar tudo para corrigir
            self.load_all_lists()

    def _get_selected_task_from_listbox(self, listbox: tk.Listbox) -> Optional[Tuple[Task, TaskStatus]]:
        """ Retorna a tarefa e o status com base no widget Listbox fornecido. """
        for status, widget in self.list_widgets.items():
            if widget == listbox:
                try:
                    selected_indices = listbox.curselection()
                    if not selected_indices:
                        return None
                    selected_index = selected_indices[0]
                    task = self.tasks_data[status][selected_index]
                    return task, status
                except IndexError:
                    logging.warning(f"Erro de indice ao pegar tarefa de {status.name}")
                    return None
        return None

    def _get_selected_inbox_task(self) -> Optional[Task]:
        """Retorna a tarefa selecionada na Caixa de Entrada."""
        inbox_list = self.list_widgets[TaskStatus.INBOX]
        try:
            selected_indices = inbox_list.curselection()
            if not selected_indices:
                return None
            selected_index = selected_indices[0]
            return self.tasks_data[TaskStatus.INBOX][selected_index]
        except IndexError:
            logging.warning("Erro ao tentar pegar tarefa selecionada (IndexError).")
            return None


# --- 4. Ponto de Entrada ---

if __name__ == "__main__":
    app = GtdApp()
    app.mainloop()


