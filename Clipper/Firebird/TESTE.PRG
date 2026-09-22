/*
 * TESTE.PRG - equivalente Clipper de python\Teste_F0005.py
 * Uso: TESTE <sy> <rt>      ex.: TESTE 57 US
 */
#include "firebird.ch"

// Main recebe os argumentos da linha de comando (cSy e cRt)
FUNCTION Main( cSy, cRt )
   IF cSy == NIL .OR. cRt == NIL
      ? "Uso: TESTE <sy> <rt>"
      QUIT
   ENDIF

   // Se o FBBRIDGE.EXE nao estiver na pasta atual, informe o caminho:
   // FB_Config( "BRIDGE", "C:\CLIPPER\FIREBIRD\FBBRIDGE.EXE" )

   // Troque pelos dados reais. O DSN e "host/porta:caminho\banco.fdb"
   // (porta e opcional; padrao 3050), ex.: "localhost/3050:C:\BANCOS\PRODCTL.FDB"
   IF !FB_Connect( "usuario", "senha", "localhost/3050:C:\BANCOS\PRODCTL.FDB" )
      ? "Erro na conexao:", FB_Error()
      QUIT
   ENDIF

   // Usa a forma de funcao (e nao o comando FB USE) para testar o retorno.
   // as interrogacoes sao preenchidas por { cSy, cRt }, nessa ordem.
   IF !FB_Use( "SELECT DRSY, DRRT, DRKY, DRDL01, DRDL02, DRSPHD, DRHRDC " + ;
               "FROM F0005 " + ;
               "WHERE TRIM(DRSY) = ? AND DRRT = ? " + ;
               "ORDER BY DRSY, DRRT", "F0005", { cSy, cRt } )
      ? "Erro na consulta:", FB_Error()
      FB DISCONNECT
      QUIT
   ENDIF

   // A partir daqui e Clipper tradicional sobre a area F0005 (ja selecionada);
   // as colunas do SELECT sao campos do DBF (F0005->DRSY etc.)
   GO TOP
   DO WHILE !Eof()
      ? F0005->DRSY, F0005->DRRT, F0005->DRKY, F0005->DRDL01, ;
        F0005->DRDL02, F0005->DRSPHD, F0005->DRHRDC
      SKIP
   ENDDO
   ? LTrim( Str( RecCount() ) ) + " registro(s)"

   // avisa se o banco tinha mais linhas que o limite MAXROWS
   IF FB_Truncated()
      ? "Aviso: resultado truncado em MAXROWS"
   ENDIF

   // fecha a area e apaga o DBF temporario
   FB CLOSE F0005
   FB DISCONNECT
RETURN NIL
