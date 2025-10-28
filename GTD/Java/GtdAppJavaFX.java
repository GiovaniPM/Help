import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import javafx.util.Pair;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Enum para representar o status/lista de uma tarefa no GTD.
 * O nome do enum é armazenado no banco de dados.
 */
enum TaskStatus {
    INBOX, // Caixa de Entrada
    NEXT_ACTION, // Próximas Ações
    PROJECT, // Projetos
    WAITING_FOR, // Esperando
    SOMEDAY_MAYBE, // Algum Dia/Talvez
    DONE // Concluído
}

/**
 * Representa uma única tarefa.
 * Esta classe é usada tanto para o modelo de dados quanto para exibição no ListView.
 */
class Task {
    private int id;
    private String description;
    private TaskStatus status;
    private String context;
    private String project;

    // Construtor para novas tarefas (sem ID ainda)
    public Task(String description) {
        this.description = description;
        this.status = TaskStatus.INBOX;
        this.context = "";
        this.project = "";
    }

    // Construtor para tarefas carregadas do banco de dados
    public Task(int id, String description, TaskStatus status, String context, String project) {
        this.id = id;
        this.description = description;
        this.status = status;
        this.context = context;
        this.project = project;
    }

    // Getters e Setters
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public TaskStatus getStatus() { return status; }
    public void setStatus(TaskStatus status) { this.status = status; }
    public String getContext() { return context; }
    public void setContext(String context) { this.context = context; }
    public String getProject() { return project; }
    public void setProject(String project) { this.project = project; }

    /**
     * Define como a tarefa será exibida no ListView.
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        if (context != null && !context.isEmpty()) {
            sb.append("[").append(context).append("] ");
        }
        sb.append(description);
        if (project != null && !project.isEmpty()) {
            sb.append(" (Projeto: ").append(project).append(")");
        }
        return sb.toString();
    }
}

/**
 * Classe auxiliar para interagir com o banco de dados SQLite.
 * Todas as operações de banco de dados são centralizadas aqui.
 */
class DatabaseHelper {

    private static final String DB_URL = "jdbc:sqlite:gtd_app.db";

    /**
     * Retorna uma conexão com o banco de dados.
     */
    private Connection connect() throws SQLException {
        return DriverManager.getConnection(DB_URL);
    }

    /**
     * Cria a tabela 'tasks' se ela não existir.
     * Deve ser chamado na inicialização do aplicativo.
     */
    public void createTables() {
        String sql = "CREATE TABLE IF NOT EXISTS tasks ("
                + " id INTEGER PRIMARY KEY AUTOINCREMENT,"
                + " description TEXT NOT NULL,"
                + " status TEXT NOT NULL,"
                + " context TEXT,"
                + " project TEXT"
                + ");";

        try (Connection conn = connect(); Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        } catch (SQLException e) {
            System.err.println("Erro ao criar tabela: " + e.getMessage());
        }
    }

    /**
     * Insere uma nova tarefa na Caixa de Entrada.
     * Retorna o objeto Task completo com o ID gerado.
     */
    public Task insertTask(String description) {
        String sql = "INSERT INTO tasks(description, status, context, project) VALUES(?,?,?,?)";
        Task newTask = null;

        try (Connection conn = connect();
             PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            
            pstmt.setString(1, description);
            pstmt.setString(2, TaskStatus.INBOX.name());
            pstmt.setString(3, "");
            pstmt.setString(4, "");
            pstmt.executeUpdate();

            ResultSet rs = pstmt.getGeneratedKeys();
            if (rs.next()) {
                newTask = new Task(rs.getInt(1), description, TaskStatus.INBOX, "", "");
            }
        } catch (SQLException e) {
            System.err.println("Erro ao inserir tarefa: " + e.getMessage());
        }
        return newTask;
    }

    /**
     * Atualiza uma tarefa existente no banco de dados.
     */
    public void updateTask(Task task) {
        String sql = "UPDATE tasks SET description = ?, status = ?, context = ?, project = ? WHERE id = ?";

        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, task.getDescription());
            pstmt.setString(2, task.getStatus().name());
            pstmt.setString(3, task.getContext());
            pstmt.setString(4, task.getProject());
            pstmt.setInt(5, task.getId());
            pstmt.executeUpdate();
        } catch (SQLException e) {
            System.err.println("Erro ao atualizar tarefa: " + e.getMessage());
        }
    }

    /**
     * Exclui uma tarefa do banco de dados pelo ID.
     */
    public void deleteTask(int id) {
        String sql = "DELETE FROM tasks WHERE id = ?";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            pstmt.executeUpdate();
        } catch (SQLException e) {
            System.err.println("Erro ao excluir tarefa: " + e.getMessage());
        }
    }

    /**
     * Busca todas as tarefas com um status específico.
     */
    public List<Task> getTasksByStatus(TaskStatus status) {
        String sql = "SELECT * FROM tasks WHERE status = ?";
        List<Task> tasks = new ArrayList<>();

        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, status.name());
            ResultSet rs = pstmt.executeQuery();

            while (rs.next()) {
                tasks.add(new Task(
                        rs.getInt("id"),
                        rs.getString("description"),
                        TaskStatus.valueOf(rs.getString("status")),
                        rs.getString("context"),
                        rs.getString("project")
                ));
            }
        } catch (SQLException e) {
            System.err.println("Erro ao buscar tarefas: " + e.getMessage());
        }
        return tasks;
    }
}

/**
 * Classe principal do aplicativo JavaFX.
 */
public class GtdAppJavaFX extends Application {

    private DatabaseHelper dbHelper;

    // Listas observáveis para atualizar a UI automaticamente
    private ObservableList<Task> inboxTasks;
    private ObservableList<Task> nextActionsTasks;
    private ObservableList<Task> projectsTasks;
    private ObservableList<Task> waitingForTasks;
    private ObservableList<Task> somedayMaybeTasks;

    // Componentes da UI
    private ListView<Task> inboxListView;
    private ListView<Task> nextActionsListView;
    private ListView<Task> projectsListView;
    private ListView<Task> waitingForListView;
    private ListView<Task> somedayMaybeListView;
    
    private TextField captureField;

    public static void main(String[] args) {
        launch(args);
    }

    /**
     * Método de inicialização (antes do start)
     * Usado para configurar o banco de dados.
     */
    @Override
    public void init() {
        // Garante que o driver JDBC do SQLite seja carregado
        try {
            Class.forName("org.sqlite.JDBC");
        } catch (ClassNotFoundException e) {
            System.err.println("Erro: Driver JDBC do SQLite não encontrado.");
            System.err.println("Certifique-se de que o arquivo .jar do sqlite-jdbc está no classpath.");
            System.exit(1);
        }
        
        dbHelper = new DatabaseHelper();
        dbHelper.createTables();
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("Aplicativo GTD (JavaFX + SQLite)");
        primaryStage.setMinWidth(700);
        primaryStage.setMinHeight(500);

        BorderPane root = new BorderPane();
        
        // 1. Área de Captura (Topo)
        HBox captureBox = createCaptureBox();
        root.setTop(captureBox);

        // 2. Abas com as Listas (Centro)
        TabPane tabPane = createTabPane();
        root.setCenter(tabPane);
        
        // 3. Carregar dados iniciais
        loadAllListsFromDatabase();

        // 4. Configurar a Cena
        Scene scene = new Scene(root, 800, 600);
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    /**
     * Cria a barra superior para capturar novas tarefas.
     */
    private HBox createCaptureBox() {
        HBox hbox = new HBox(10);
        hbox.setPadding(new Insets(10));
        
        Label captureLabel = new Label("Capturar:");
        captureField = new TextField();
        HBox.setHgrow(captureField, Priority.ALWAYS); // Faz o campo de texto crescer
        
        Button captureButton = new Button("Adicionar à Caixa de Entrada");
        captureButton.setOnAction(e -> captureTask());
        
        hbox.getChildren().addAll(captureLabel, captureField, captureButton);
        return hbox;
    }

    /**
     * Cria o painel de abas com todas as listas do GTD.
     */
    private TabPane createTabPane() {
        TabPane tabPane = new TabPane();
        tabPane.setTabClosingPolicy(TabPane.TabClosingPolicy.UNAVAILABLE);

        // Inicializa as listas observáveis
        inboxTasks = FXCollections.observableArrayList();
        nextActionsTasks = FXCollections.observableArrayList();
        projectsTasks = FXCollections.observableArrayList();
        waitingForTasks = FXCollections.observableArrayList();
        somedayMaybeTasks = FXCollections.observableArrayList();

        // Configura os ListViews
        inboxListView = new ListView<>(inboxTasks);
        nextActionsListView = new ListView<>(nextActionsTasks);
        projectsListView = new ListView<>(projectsTasks);
        waitingForListView = new ListView<>(waitingForTasks);
        somedayMaybeListView = new ListView<>(somedayMaybeTasks);

        // Configura o menu de contexto (processamento) para a Caixa de Entrada
        inboxListView.setContextMenu(createInboxContextMenu());

        // Cria as Abas
        tabPane.getTabs().add(new Tab("Caixa de Entrada", inboxListView));
        tabPane.getTabs().add(new Tab("Próximas Ações", nextActionsListView));
        tabPane.getTabs().add(new Tab("Projetos", projectsListView));
        tabPane.getTabs().add(new Tab("Esperando", waitingForListView));
        tabPane.getTabs().add(new Tab("Algum Dia/Talvez", somedayMaybeListView));

        return tabPane;
    }

    /**
     * Carrega (ou recarrega) todas as listas do banco de dados.
     */
    private void loadAllListsFromDatabase() {
        inboxTasks.setAll(dbHelper.getTasksByStatus(TaskStatus.INBOX));
        nextActionsTasks.setAll(dbHelper.getTasksByStatus(TaskStatus.NEXT_ACTION));
        projectsTasks.setAll(dbHelper.getTasksByStatus(TaskStatus.PROJECT));
        waitingForTasks.setAll(dbHelper.getTasksByStatus(TaskStatus.WAITING_FOR));
        somedayMaybeTasks.setAll(dbHelper.getTasksByStatus(TaskStatus.SOMEDAY_MAYBE));
    }

    /**
     * (Etapa 1: Capturar) Pega o texto do campo e salva no DB.
     */
    private void captureTask() {
        String description = captureField.getText().trim();
        if (description.isEmpty()) {
            showAlert("Erro", "A descrição não pode estar vazia.");
            return;
        }

        Task newTask = dbHelper.insertTask(description);
        if (newTask != null) {
            inboxTasks.add(newTask); // Adiciona na lista da UI
            captureField.clear();
        } else {
            showAlert("Erro de Banco de Dados", "Não foi possível salvar a tarefa.");
        }
    }

    /**
     * Cria o menu de clique com o botão direito para a Caixa de Entrada.
     * (Etapas 2 e 3: Processar e Organizar)
     */
    private ContextMenu createInboxContextMenu() {
        ContextMenu contextMenu = new ContextMenu();
        
        MenuItem nextActionItem = new MenuItem("Mover para Próximas Ações");
        nextActionItem.setOnAction(e -> processTask(TaskStatus.NEXT_ACTION));

        MenuItem projectItem = new MenuItem("Mover para Projetos");
        projectItem.setOnAction(e -> processTask(TaskStatus.PROJECT));

        MenuItem waitingForItem = new MenuItem("Mover para Esperando");
        waitingForItem.setOnAction(e -> processTask(TaskStatus.WAITING_FOR));

        MenuItem somedayItem = new MenuItem("Mover para Algum Dia/Talvez");
        somedayItem.setOnAction(e -> processTask(TaskStatus.SOMEDAY_MAYBE));

        MenuItem deleteItem = new MenuItem("Excluir (Lixo)");
        deleteItem.setOnAction(e -> {
            Task selected = inboxListView.getSelectionModel().getSelectedItem();
            if (selected != null) {
                dbHelper.deleteTask(selected.getId());
                inboxTasks.remove(selected);
            }
        });

        contextMenu.getItems().addAll(nextActionItem, projectItem, waitingForItem, somedayItem, new SeparatorMenuItem(), deleteItem);
        return contextMenu;
    }

    /**
     * Lógica principal para processar um item da Caixa de Entrada.
     */
    private void processTask(TaskStatus newStatus) {
        Task selected = inboxListView.getSelectionModel().getSelectedItem();
        if (selected == null) return;

        // Para Próximas Ações, perguntamos o Contexto.
        // Para Projetos, perguntamos o nome do Projeto.
        String context = selected.getContext();
        String project = selected.getProject();

        if (newStatus == TaskStatus.NEXT_ACTION) {
            context = showTextInputDialog("Contexto", "Digite o contexto (ex: @casa, @rua):", context);
        } else if (newStatus == TaskStatus.PROJECT) {
            project = showTextInputDialog("Projeto", "Digite o nome do projeto:", selected.getDescription());
        }

        // Atualiza o objeto Task
        selected.setStatus(newStatus);
        selected.setContext(context);
        selected.setProject(project);

        // Salva no DB
        dbHelper.updateTask(selected);

        // Move entre as listas da UI
        inboxTasks.remove(selected);
        switch (newStatus) {
            case NEXT_ACTION:
                nextActionsTasks.add(selected);
                break;
            case PROJECT:
                projectsTasks.add(selected);
                break;
            case WAITING_FOR:
                waitingForTasks.add(selected);
                break;
            case SOMEDAY_MAYBE:
                somedayMaybeTasks.add(selected);
                break;
            // Outros casos não são destinos diretos do processamento
        }
    }

    /**
     * Exibe um alerta simples.
     */
    private void showAlert(String title, String content) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }

    /**
     * Exibe um diálogo para pedir um texto ao usuário.
     */
    private String showTextInputDialog(String title, String header, String defaultValue) {
        TextInputDialog dialog = new TextInputDialog(defaultValue);
        dialog.setTitle(title);
        dialog.setHeaderText(header);
        dialog.setContentText("Valor:");

        Optional<String> result = dialog.showAndWait();
        return result.orElse(defaultValue); // Retorna o valor antigo se o usuário cancelar
    }
}
