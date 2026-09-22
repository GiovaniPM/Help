/*
 * FIREBIRD.CH - comandos da biblioteca FIREBIRD.LIB (Clipper 5.2)
 *
 * Inclua no programa com:  #include "firebird.ch"
 *
 * FB CONNECT USER <usuario> PASSWORD <senha> DSN <dsn>
 * FB USE <select> [ALIAS <alias>] [BIND <v1>, <v2>, ...]
 * FB EXEC <dml/ddl/psql> [BIND <v1>, <v2>, ...]
 * FB CLOSE [<alias>]
 * FB DISCONNECT
 *
 * Depois de FB USE a area de trabalho fica aberta e selecionada: GO TOP, SKIP,
 * EOF(), FIELD->, INDEX ON, SET FILTER, BROWSE, COPY TO etc. funcionam normalmente.
 *
 * Os comandos abaixo sao apenas "atalhos": o pre-processador do Clipper troca
 * cada comando pela chamada da funcao correspondente em FIREBIRD.PRG. Como uma
 * funcao chamada como comando descarta o retorno, use as funcoes diretamente
 * (ex.: IF !FB_Use(...)) quando precisar testar o sucesso, e FB_Error() para
 * ler a mensagem de erro.
 *
 * Marcadores usados nas regras:
 *   <x>       expressao qualquer
 *   <(x)>     "estringifica": um nome sem aspas (ALIAS F0005) vira "F0005"
 *   <x,...>   lista de expressoes separadas por virgula
 *   [ ... ]   parte opcional; se ausente, o trecho correspondente some da saida
 */

// FB CONNECT USER "u" PASSWORD "p" DSN "host/porta:caminho/banco.fdb"
#command FB CONNECT USER <u> PASSWORD <p> DSN <d> => FB_Connect( <u>, <p>, <d> )

// FB USE "SELECT ... ? ..." ALIAS CLI BIND cCodigo
// os valores de BIND viram o vetor { cCodigo } (nas interrogacoes, na ordem em que aparecem)
#command FB USE <sql> [ALIAS <a>] [BIND <b,...>] ;
      => FB_Use( <sql>, [<(a)>], [{ <b> }] )

// FB EXEC "UPDATE ... SET X = ?" BIND 10  (com COMMIT automatico)
#command FB EXEC <sql> [BIND <b,...>] ;
      => FB_Exec( <sql>, [{ <b> }] )

// FB CLOSE CLI   fecha e apaga o resultado; sem alias, fecha todos
#command FB CLOSE [<a>] => FB_Close( [<(a)>] )

#command FB DISCONNECT => FB_Disconnect()
