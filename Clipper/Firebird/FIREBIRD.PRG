/*
 * FIREBIRD.PRG - consulta ao Firebird a partir do Clipper 5.2
 *
 * Cada consulta e executada pela ponte FBBRIDGE.EXE (C + API classica do Firebird,
 * ibase.h/fbclient, ver bridge), que grava o resultado em um DBF temporario. A
 * biblioteca abre esse DBF com dbUseArea(), entao todos os comandos tradicionais
 * (GO TOP, SKIP, SEEK apos INDEX, BROWSE...) funcionam sobre o resultado.
 *
 * Fluxo de uma chamada (ver RunBridge):
 *
 *    Clipper                                   C (FBBRIDGE.EXE)
 *    -------                                   ---------------------
 *    grava FBnnnnn.SQL e FBnnnnn.REQ  --->
 *    RUN FBBRIDGE.EXE FBnnnnn.REQ  ------->  le o .REQ, conecta, executa
 *                                              grava FBnnnnn.DBF (QUERY)
 *    le FBnnnnn.RSP  <-----------------------  grava FBnnnnn.RSP (OK ou ERR)
 *    apaga .REQ/.SQL/.RSP e abre o .DBF
 *
 * Nomes de arquivo seguem o padrao 8.3 do DOS (FB + 5 digitos).
 *
 * Observacao de sintaxe: no Clipper 5.2 o ";" so serve como continuacao de
 * linha (nao separa instrucoes), por isso cada instrucao fica em sua linha.
 *
 * Compilar: clipper firebird /n /w   (ver BUILD.BAT)
 */

/*
 * Estado da biblioteca. Variaveis STATIC no nivel do arquivo sao visiveis
 * apenas neste .PRG e mantem o valor entre as chamadas.
 */

// credenciais da conexao (a senha e apagada se o teste de conexao falhar)
STATIC s_cUser := "", s_cPass := "", s_cDsn := "", s_lConn := .F.

// configuracao (ver FB_Config)
STATIC s_cBridge := "FBBRIDGE.EXE", s_cWork := ""
STATIC s_cCodePage := "cp850", s_nMaxRows := 65000

// s_nSeq: contador dos nomes temporarios; s_cError/s_lTrunc: resultado da ultima
// chamada; s_aOpen: {{ alias, arquivo DBF }, ...} das consultas abertas
STATIC s_nSeq := 0, s_cError := "", s_lTrunc := .F., s_aOpen := {}

/*
 * Testa a conexao e guarda as credenciais para as proximas chamadas.
 * Nao existe conexao persistente: o teste roda um "SELECT 1 FROM RDB$DATABASE"
 * e as demais chamadas reconectam usando as credenciais guardadas aqui.
 */
FUNCTION FB_Connect( cUser, cPass, cDsn )
   LOCAL aResp
   s_lConn := .F.
   s_cUser := cUser
   s_cPass := cPass
   s_cDsn  := cDsn
   s_lConn := RunBridge( "PING", NIL, NIL, NIL, @aResp )
   IF !s_lConn
      // nao deixa a senha na memoria se a conexao nao foi aceita
      s_cPass := ""
   ENDIF
RETURN s_lConn

/* Fecha todas as consultas abertas e esquece as credenciais. */
FUNCTION FB_Disconnect()
   FB_Close()
   s_cUser := ""
   s_cPass := ""
   s_cDsn  := ""
   s_lConn := .F.
RETURN .T.

/*
 * Executa um SELECT e abre o resultado numa nova area de trabalho, que fica
 * selecionada. Retorna .T. se deu certo; em caso de erro use FB_Error().
 *
 *   cSql    o SELECT (pode ter varias linhas; ";" no final e ignorado)
 *   cAlias  alias da area de trabalho (padrao FBQRY1, FBQRY2...)
 *   aBind   valores para os "?" do SELECT, na ordem em que aparecem (C, N, D, L ou NIL)
 */
FUNCTION FB_Use( cSql, cAlias, aBind )
   LOCAL cDbf, aResp, lOk := .F., bOld, oErr
   s_cError := ""
   s_lTrunc := .F.
   IF cAlias == NIL .OR. Empty( cAlias )
      cAlias := "FBQRY" + LTrim( Str( Len( s_aOpen ) + 1 ) )
   ENDIF
   cAlias := Upper( AllTrim( cAlias ) )

   // Select() devolve 0 quando nao existe area com esse alias
   IF Select( cAlias ) > 0
      s_cError := "Alias ja esta em uso: " + cAlias
      RETURN .F.
   ENDIF

   // reserva o nome do DBF que a ponte vai gerar
   cDbf := NextBase() + ".DBF"
   IF !RunBridge( "QUERY", cSql, aBind, cDbf, @aResp )
      FErase( cDbf )
      RETURN .F.
   ENDIF

   // 3a linha da resposta: "1" quando o resultado foi cortado em MAXROWS
   s_lTrunc := ( Len( aResp ) >= 3 .AND. aResp[ 3 ] == "1" )

   // dbUseArea() gera um erro de execucao se o DBF estiver invalido; captura
   // com BEGIN SEQUENCE para devolver .F. em vez de derrubar o programa
   bOld := ErrorBlock( { |e| Break( e ) } )
   BEGIN SEQUENCE
      // (novaArea, driver padrao, arquivo, alias, exclusivo, somente leitura)
      dbUseArea( .T., NIL, cDbf, cAlias, .F., .F. )
      lOk := .T.
   RECOVER USING oErr
      s_cError := "Falha ao abrir o resultado: " + oErr:description
   END SEQUENCE
   ErrorBlock( bOld )

   IF lOk
      AAdd( s_aOpen, { cAlias, cDbf } )
   ELSE
      FErase( cDbf )
   ENDIF
RETURN lOk

/*
 * Executa INSERT/UPDATE/DELETE/DDL/PSQL e confirma (COMMIT) ao final.
 * Retorna o numero de linhas afetadas, ou -1 em caso de erro (FB_Error()).
 */
FUNCTION FB_Exec( cSql, aBind )
   LOCAL aResp
   s_cError := ""
   IF !RunBridge( "EXEC", cSql, aBind, NIL, @aResp )
      RETURN -1
   ENDIF
RETURN Val( aResp[ 2 ] )

/*
 * Fecha o alias informado (ou todos, sem parametro) e apaga o DBF temporario.
 * Percorre o vetor de tras para frente porque remove elementos durante o laco.
 */
FUNCTION FB_Close( cAlias )
   LOCAL n
   IF cAlias != NIL
      cAlias := Upper( AllTrim( cAlias ) )
   ENDIF
   FOR n := Len( s_aOpen ) TO 1 STEP -1
      IF cAlias == NIL .OR. s_aOpen[ n, 1 ] == cAlias
         IF Select( s_aOpen[ n, 1 ] ) > 0
            // (alias)->( ... ) executa a expressao naquela area sem trocar a atual
            ( s_aOpen[ n, 1 ] )->( dbCloseArea() )
         ENDIF
         FErase( s_aOpen[ n, 2 ] )
         ADel( s_aOpen, n )
         ASize( s_aOpen, Len( s_aOpen ) - 1 )
      ENDIF
   NEXT
RETURN NIL

/* Mensagem do ultimo erro ("" quando a ultima chamada deu certo). */
FUNCTION FB_Error()
RETURN s_cError

/* .T. se o ultimo FB USE parou em MAXROWS (ha mais linhas no banco). */
FUNCTION FB_Truncated()
RETURN s_lTrunc

/*
 * Ajusta a biblioteca; retorna o valor anterior.
 *   BRIDGE   caminho do FBBRIDGE.EXE   (padrao "FBBRIDGE.EXE")
 *   WORKDIR  pasta dos arquivos temporarios (padrao %TEMP%)
 *   CODEPAGE pagina de codigo do DOS: cp850, cp437 ou cp1252 (padrao cp850)
 *   MAXROWS  maximo de linhas por consulta, 0 = sem limite (padrao 65000)
 */
FUNCTION FB_Config( cKey, xValue )
   LOCAL xOld
   cKey := Upper( AllTrim( cKey ) )
   DO CASE
   CASE cKey == "BRIDGE"
      xOld := s_cBridge
      IF xValue != NIL
         s_cBridge := xValue
      ENDIF
   CASE cKey == "WORKDIR"
      xOld := s_cWork
      IF xValue != NIL
         s_cWork := xValue
      ENDIF
   CASE cKey == "CODEPAGE"
      xOld := s_cCodePage
      IF xValue != NIL
         s_cCodePage := Lower( xValue )
      ENDIF
   CASE cKey == "MAXROWS"
      xOld := s_nMaxRows
      IF xValue != NIL
         s_nMaxRows := xValue
      ENDIF
   ENDCASE
RETURN xOld

/* ------------------------------------------------------------------------- */
/* Funcoes internas                                                          */
/* ------------------------------------------------------------------------- */

/*
 * Grava a requisicao, roda a ponte e le a resposta. Retorna .T. se a ponte
 * respondeu "OK"; caso contrario s_cError recebe a mensagem.
 *
 *   cAction  "PING", "QUERY" ou "EXEC"
 *   cSql     comando SQL (NIL no PING)
 *   aBind    valores dos binds (ou NIL)
 *   cOut     (QUERY) nome do DBF que a ponte deve gerar
 *   aResp    (por referencia) linhas da resposta: { "OK", linhas, truncou }
 */
STATIC FUNCTION RunBridge( cAction, cSql, aBind, cOut, aResp )
   LOCAL cBase, cReq, cRsp, cSqlFile, cText, cCmd, n
   LOCAL lOk := .F.

   // so o PING pode rodar antes de estar conectado
   IF cAction != "PING" .AND. !s_lConn
      s_cError := "Nao conectado. Use FB CONNECT."
      RETURN .F.
   ENDIF

   cBase    := NextBase()
   cReq     := cBase + ".REQ"
   cRsp     := cBase + ".RSP"
   cSqlFile := cBase + ".SQL"

   // Requisicao: uma linha CHAVE=VALOR por item, terminada em CR+LF
   cText := "ACTION=" + cAction + Chr( 13 ) + Chr( 10 ) + ;
            "USER="     + s_cUser     + Chr( 13 ) + Chr( 10 ) + ;
            "PASS="     + s_cPass     + Chr( 13 ) + Chr( 10 ) + ;
            "DSN="      + s_cDsn      + Chr( 13 ) + Chr( 10 ) + ;
            "CODEPAGE=" + s_cCodePage + Chr( 13 ) + Chr( 10 ) + ;
            "MAXROWS="  + LTrim( Str( s_nMaxRows ) ) + Chr( 13 ) + Chr( 10 ) + ;
            "RSP="      + cRsp        + Chr( 13 ) + Chr( 10 )
   IF cOut != NIL
      cText += "OUT=" + cOut + Chr( 13 ) + Chr( 10 )
   ENDIF
   IF cSql != NIL
      // o SQL vai em arquivo proprio para poder ter varias linhas
      MemoWrit( cSqlFile, cSql )
      cText += "SQLFILE=" + cSqlFile + Chr( 13 ) + Chr( 10 )
   ENDIF
   IF aBind != NIL
      FOR n := 1 TO Len( aBind )
         cText += "BIND=" + BindItem( aBind[ n ] ) + Chr( 13 ) + Chr( 10 )
      NEXT
   ENDIF
   MemoWrit( cReq, cText )

   // apaga resposta antiga para nao confundir com a desta chamada
   FErase( cRsp )
   cCmd := s_cBridge + " " + cReq
   // RUN &cmd: o operador & (macro) executa o texto da variavel; RUN nao
   // devolve codigo de saida, por isso o resultado vem pelo arquivo .RSP
   RUN &cCmd

   IF File( cRsp )
      aResp := SplitLines( MemoRead( cRsp ) )
      IF Len( aResp ) >= 1 .AND. aResp[ 1 ] == "OK" .AND. Len( aResp ) >= 2
         lOk := .T.
      ELSEIF Len( aResp ) >= 2
         // "ERR" + mensagem
         s_cError := aResp[ 2 ]
      ELSE
         s_cError := "Resposta invalida da ponte."
      ENDIF
   ELSE
      // sem .RSP a ponte nem chegou a rodar (FBBRIDGE.EXE ausente, caminho errado...)
      s_cError := "A ponte nao respondeu. Verifique FB_Config(BRIDGE) e o cliente do Firebird (fbclient)."
   ENDIF

   /* o REQ contem a senha: sempre apagar */
   FErase( cReq )
   FErase( cSqlFile )
   FErase( cRsp )
RETURN lOk

/*
 * Converte um valor Clipper para a linha de bind "<tipo>|<valor escapado>".
 * Tipos: C texto, N numero, D data (AAAAMMDD), L logico (T/F), Z nulo.
 * Barra invertida, CR e LF sao escapados (\\, \r, \n) para nao quebrar a
 * requisicao, que e lida linha a linha.
 */
STATIC FUNCTION BindItem( xVal )
   LOCAL cType := ValType( xVal ), cTxt := ""
   DO CASE
   CASE cType == "C"
      cTxt := xVal
   CASE cType == "N"
      // largura 30 e 10 decimais evitam arredondar o valor; os zeros a direita
      // sao inofensivos porque a ponte converte para o tipo do parametro
      cTxt := LTrim( Str( xVal, 30, 10 ) )
   CASE cType == "D"
      cTxt := DtoS( xVal )
   CASE cType == "L"
      cTxt := IIf( xVal, "T", "F" )
   OTHERWISE
      // NIL (ou tipo nao suportado) vai como NULL
      cType := "Z"
   ENDCASE
   // a barra invertida deve ser escapada primeiro, senao dobraria as demais
   cTxt := StrTran( cTxt, "\", "\\" )
   cTxt := StrTran( cTxt, Chr( 13 ), "\r" )
   cTxt := StrTran( cTxt, Chr( 10 ), "\n" )
RETURN cType + "|" + cTxt

/*
 * Devolve um nome base livre (pasta de trabalho + "FB" + 5 digitos). Os
 * arquivos da chamada usam esse nome com extensoes .REQ, .SQL, .RSP e .DBF.
 * Confere os quatro para nao pisar em arquivo de outra estacao que use a
 * mesma pasta (rede).
 */
STATIC FUNCTION NextBase()
   LOCAL cBase
   IF s_nSeq == 0
      // ponto de partida diferente a cada execucao (segundos desde a meia-noite)
      s_nSeq := Int( Seconds() ) % 100000
   ENDIF
   DO WHILE .T.
      s_nSeq := ( s_nSeq + 1 ) % 100000
      cBase := WorkDir() + "FB" + StrZero( s_nSeq, 5 )
      IF !File( cBase + ".REQ" ) .AND. !File( cBase + ".RSP" ) .AND. ;
         !File( cBase + ".SQL" ) .AND. !File( cBase + ".DBF" )
         EXIT
      ENDIF
   ENDDO
RETURN cBase

/* Pasta dos temporarios: FB_Config("WORKDIR"), senao %TEMP%, senao %TMP%. */
STATIC FUNCTION WorkDir()
   IF Empty( s_cWork )
      s_cWork := GetEnv( "TEMP" )
      IF Empty( s_cWork )
         s_cWork := GetEnv( "TMP" )
      ENDIF
   ENDIF
   // garante a barra final para poder concatenar o nome do arquivo
   IF !Empty( s_cWork ) .AND. !( Right( s_cWork, 1 ) $ "\:" )
      s_cWork += "\"
   ENDIF
RETURN s_cWork

/*
 * Quebra um texto em linhas (vetor). Remove CR e o Ctrl-Z (fim de arquivo do
 * DOS) que alguns arquivos texto carregam. Usado para ler o .RSP.
 */
STATIC FUNCTION SplitLines( cText )
   LOCAL aLin := {}, nPos
   cText := StrTran( StrTran( cText, Chr( 13 ), "" ), Chr( 26 ), "" )
   DO WHILE Len( cText ) > 0
      nPos := At( Chr( 10 ), cText )
      IF nPos == 0
         // ultima linha, sem LF no final
         AAdd( aLin, cText )
         cText := ""
      ELSE
         AAdd( aLin, Left( cText, nPos - 1 ) )
         cText := SubStr( cText, nPos + 1 )
      ENDIF
   ENDDO
RETURN aLin
