/*
 * SQLITE.CH - comandos da biblioteca SQLITE.LIB (Clipper 5.2)
 *
 * Inclua no programa com:  #include "sqlite.ch"
 *
 * SQLITE CONNECT FILE <arquivo>
 * SQLITE USE <select> [ALIAS <alias>] [BIND <v1>, <v2>, ...]
 * SQLITE EXEC <dml/ddl> [BIND <v1>, <v2>, ...]
 * SQLITE CLOSE [<alias>]
 * SQLITE DISCONNECT
 *
 * Depois de SQLITE USE a area de trabalho fica aberta e selecionada: GO TOP, SKIP,
 * EOF(), FIELD->, INDEX ON, SET FILTER, BROWSE, COPY TO etc. funcionam normalmente.
 *
 * Os comandos abaixo sao apenas "atalhos": o pre-processador do Clipper troca
 * cada comando pela chamada da funcao correspondente em SQLITE.PRG. Como uma
 * funcao chamada como comando descarta o retorno, use as funcoes diretamente
 * (ex.: IF !SQLITE_Use(...)) quando precisar testar o sucesso, e SQLITE_Error()
 * para ler a mensagem de erro.
 *
 * Marcadores usados nas regras:
 *   <x>       expressao qualquer
 *   <(x)>     "estringifica": um nome sem aspas (ALIAS F0005) vira "F0005"
 *   <x,...>   lista de expressoes separadas por virgula
 *   [ ... ]   parte opcional; se ausente, o trecho correspondente some da saida
 */

// SQLITE CONNECT FILE "C:\DADOS\SISTEMA.DB"   (o arquivo e criado se nao existir)
#command SQLITE CONNECT FILE <f> => SQLITE_Connect( <f> )

// SQLITE USE "SELECT ... :1 ..." ALIAS CLI BIND cCodigo
// os valores de BIND viram o vetor { cCodigo } (nas posicoes :1, :2 ...)
#command SQLITE USE <sql> [ALIAS <a>] [BIND <b,...>] ;
      => SQLITE_Use( <sql>, [<(a)>], [{ <b> }] )

// SQLITE EXEC "UPDATE ... SET X = :1" BIND 10
#command SQLITE EXEC <sql> [BIND <b,...>] ;
      => SQLITE_Exec( <sql>, [{ <b> }] )

// SQLITE CLOSE CLI   fecha e apaga o resultado; sem alias, fecha todos
#command SQLITE CLOSE [<a>] => SQLITE_Close( [<(a)>] )

#command SQLITE DISCONNECT => SQLITE_Disconnect()
