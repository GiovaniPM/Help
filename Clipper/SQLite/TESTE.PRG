/*
 * TESTE.PRG - exemplo de uso da SQLITE.LIB
 * Uso: TESTE [codigo]      ex.: TESTE       (lista tudo)
 *            TESTE 2       (filtra pelo codigo)
 */
#include "sqlite.ch"

// Main recebe o argumento opcional da linha de comando (cCod)
FUNCTION Main( cCod )
   LOCAL cDesc, nAfetadas

   // Se o SQLITEBRIDGE.EXE nao estiver na pasta atual, informe o caminho:
   // SQLITE_Config( "BRIDGE", "C:\CLIPPER\SQLITE\SQLITEBRIDGE.EXE" )

   // O arquivo e criado automaticamente se ainda nao existir.
   IF !SQLITE_Connect( "TESTE.DB" )
      ? "Erro ao abrir o banco:", SQLITE_Error()
      QUIT
   ENDIF

   // Cria a tabela na primeira vez que o programa roda
   SQLITE_Exec( "CREATE TABLE IF NOT EXISTS PRODUTO ( " + ;
                "CODIGO INTEGER PRIMARY KEY, DESCRICAO TEXT, PRECO REAL, DATA_CAD DATE )" )

   // Semeia alguns registros na primeira execucao
   IF Empty( ProdutoCount() )
      SQLITE_Exec( "INSERT INTO PRODUTO (CODIGO, DESCRICAO, PRECO, DATA_CAD) VALUES (:1, :2, :3, :4)", ;
                   { 1, "Parafuso", 0.75, SToD( "20260101" ) } )
      SQLITE_Exec( "INSERT INTO PRODUTO (CODIGO, DESCRICAO, PRECO, DATA_CAD) VALUES (:1, :2, :3, :4)", ;
                   { 2, "Porca", 0.30, SToD( "20260102" ) } )
      SQLITE_Exec( "INSERT INTO PRODUTO (CODIGO, DESCRICAO, PRECO, DATA_CAD) VALUES (:1, :2, :3, :4)", ;
                   { 3, "Arruela", 0.10, SToD( "20260103" ) } )
   ENDIF

   // Usa a forma de funcao (e nao o comando SQLITE USE) para testar o retorno.
   IF Empty( cCod )
      IF !SQLITE_Use( "SELECT CODIGO, DESCRICAO, PRECO, DATA_CAD FROM PRODUTO ORDER BY CODIGO", "PRODUTO" )
         ? "Erro na consulta:", SQLITE_Error()
         SQLITE DISCONNECT
         QUIT
      ENDIF
   ELSE
      // :1 e preenchido por { cCod }
      IF !SQLITE_Use( "SELECT CODIGO, DESCRICAO, PRECO, DATA_CAD FROM PRODUTO WHERE CODIGO = :1", ;
                      "PRODUTO", { Val( cCod ) } )
         ? "Erro na consulta:", SQLITE_Error()
         SQLITE DISCONNECT
         QUIT
      ENDIF
   ENDIF

   // A partir daqui e Clipper tradicional sobre a area PRODUTO (ja selecionada);
   // as colunas do SELECT sao campos do DBF (PRODUTO->CODIGO etc.)
   GO TOP
   DO WHILE !Eof()
      ? PRODUTO->CODIGO, PRODUTO->DESCRICAO, PRODUTO->PRECO, PRODUTO->DATA_CAD
      SKIP
   ENDDO
   ? LTrim( Str( RecCount() ) ) + " registro(s)"

   // avisa se o banco tinha mais linhas que o limite MAXROWS
   IF SQLITE_Truncated()
      ? "Aviso: resultado truncado em MAXROWS"
   ENDIF

   SQLITE CLOSE PRODUTO

   // Exemplo de alteracao: reajusta o preco do produto 1 em 10%
   nAfetadas := SQLITE_Exec( "UPDATE PRODUTO SET PRECO = PRECO * 1.1 WHERE CODIGO = :1", { 1 } )
   IF nAfetadas == -1
      ? "Falha no UPDATE:", SQLITE_Error()
   ELSE
      ? nAfetadas, "registro(s) atualizado(s)."
   ENDIF

   SQLITE DISCONNECT
RETURN NIL

/* Numero de produtos ja cadastrados (0 se a tabela ainda estiver vazia). */
STATIC FUNCTION ProdutoCount()
   LOCAL nQtd := 0
   IF SQLITE_Use( "SELECT COUNT(*) AS QTD FROM PRODUTO", "CONTAGEM" )
      nQtd := CONTAGEM->QTD
      SQLITE CLOSE CONTAGEM
   ENDIF
RETURN nQtd
