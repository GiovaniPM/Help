/*
 * TESTE.PRG - equivalente Clipper de python\Teste_F0005.py
 * Uso: TESTE <sy> <rt>      ex.: TESTE 57 US
 */
#include "oracle.ch"

// Main recebe os argumentos da linha de comando (cSy e cRt)
FUNCTION Main( cSy, cRt )
   IF cSy == NIL .OR. cRt == NIL
      ? "Uso: TESTE <sy> <rt>"
      QUIT
   ENDIF

   // Se o ORABRIDGE.EXE nao estiver na pasta atual, informe o caminho:
   // ORA_Config( "BRIDGE", "C:\CLIPPER\ORACLE\ORABRIDGE.PY" )

   // Troque pelos dados reais. O DSN pode ser "host:porta/servico" ou um
   // descritor completo (DESCRIPTION=...), como no script Python.
   IF !ORA_Connect( "usuario", "senha", "host:1544/servico" )
      ? "Erro na conexao:", ORA_Error()
      QUIT
   ENDIF

   // Usa a forma de funcao (e nao o comando ORA USE) para testar o retorno.
   // :1 e :2 sao preenchidos por { cSy, cRt }, nessa ordem.
   IF !ORA_Use( "SELECT DRSY, DRRT, DRKY, DRDL01, DRDL02, DRSPHD, DRHRDC " + ;
                "FROM PRODCTLXE.F0005 " + ;
                "WHERE RTRIM(LTRIM(DRSY,' '),' ') = :1 AND DRRT = :2 " + ;
                "ORDER BY DRSY, DRRT", "F0005", { cSy, cRt } )
      ? "Erro na consulta:", ORA_Error()
      ORA DISCONNECT
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
   IF ORA_Truncated()
      ? "Aviso: resultado truncado em MAXROWS"
   ENDIF

   // fecha a area e apaga o DBF temporario
   ORA CLOSE F0005
   ORA DISCONNECT
RETURN NIL
