/*
 * ORACLE.CH - comandos da biblioteca ORACLE.LIB (Clipper 5.2)
 *
 * Inclua no programa com:  #include "oracle.ch"
 *
 * ORA CONNECT USER <usuario> PASSWORD <senha> DSN <dsn>
 * ORA USE <select> [ALIAS <alias>] [BIND <v1>, <v2>, ...]
 * ORA EXEC <dml/ddl/plsql> [BIND <v1>, <v2>, ...]
 * ORA CLOSE [<alias>]
 * ORA DISCONNECT
 *
 * Depois de ORA USE a area de trabalho fica aberta e selecionada: GO TOP, SKIP,
 * EOF(), FIELD->, INDEX ON, SET FILTER, BROWSE, COPY TO etc. funcionam normalmente.
 *
 * Os comandos abaixo sao apenas "atalhos": o pre-processador do Clipper troca
 * cada comando pela chamada da funcao correspondente em ORACLE.PRG. Como uma
 * funcao chamada como comando descarta o retorno, use as funcoes diretamente
 * (ex.: IF !ORA_Use(...)) quando precisar testar o sucesso, e ORA_Error() para
 * ler a mensagem de erro.
 *
 * Marcadores usados nas regras:
 *   <x>       expressao qualquer
 *   <(x)>     "estringifica": um nome sem aspas (ALIAS F0005) vira "F0005"
 *   <x,...>   lista de expressoes separadas por virgula
 *   [ ... ]   parte opcional; se ausente, o trecho correspondente some da saida
 */

// ORA CONNECT USER "u" PASSWORD "p" DSN "host:1544/servico"
#command ORA CONNECT USER <u> PASSWORD <p> DSN <d> => ORA_Connect( <u>, <p>, <d> )

// ORA USE "SELECT ... :1 ..." ALIAS CLI BIND cCodigo
// os valores de BIND viram o vetor { cCodigo } (nas posicoes :1, :2 ...)
#command ORA USE <sql> [ALIAS <a>] [BIND <b,...>] ;
      => ORA_Use( <sql>, [<(a)>], [{ <b> }] )

// ORA EXEC "UPDATE ... SET X = :1" BIND 10  (com COMMIT automatico)
#command ORA EXEC <sql> [BIND <b,...>] ;
      => ORA_Exec( <sql>, [{ <b> }] )

// ORA CLOSE CLI   fecha e apaga o resultado; sem alias, fecha todos
#command ORA CLOSE [<a>] => ORA_Close( [<(a)>] )

#command ORA DISCONNECT => ORA_Disconnect()
