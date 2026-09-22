cmake_minimum_required(VERSION 3.14)
project(sqlitebridge C)

# SQLITEBRIDGE.EXE - ponte entre SQLITE.LIB (Clipper 5.2) e um banco SQLite.
#
#   cmake -S . -B build
#   cmake --build build
#   ctest --test-dir build --output-on-failure      (testes sem banco)
#
# O acesso ao banco usa a amalgamation oficial do SQLite (sqlite3.c/.h), baixada do
# site oficial na primeira configuracao. Sem internet, aponte para uma copia local:
#   -DFETCHCONTENT_SOURCE_DIR_SQLITE3=<pasta com sqlite3.c e sqlite3.h>
# O SQLite e embutido (sem servidor nem cliente externo): o executavel gerado ja
# contem tudo que precisa para abrir o arquivo .db.

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(sqlite3
    URL                    https://www.sqlite.org/2026/sqlite-amalgamation-3530400.zip
    URL_HASH               SHA3_256=628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE)
FetchContent_MakeAvailable(sqlite3)

add_library(sqlite3 STATIC ${sqlite3_SOURCE_DIR}/sqlite3.c)
target_include_directories(sqlite3 PUBLIC ${sqlite3_SOURCE_DIR})
target_compile_definitions(sqlite3 PRIVATE SQLITE_THREADSAFE=0 SQLITE_OMIT_LOAD_EXTENSION)
if(NOT WIN32)
    target_link_libraries(sqlite3 PUBLIC ${CMAKE_DL_LIBS} pthread)
endif()

# parte sem dependencia do SQLite (requisicao, binds, DBF): testavel isoladamente
add_library(bridge_core STATIC bridge_core.c)
target_include_directories(bridge_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(sqlitebridge sqlitebridge.c)
target_link_libraries(sqlitebridge PRIVATE bridge_core sqlite3)
set_target_properties(sqlitebridge PROPERTIES OUTPUT_NAME SQLITEBRIDGE)

# executavel independente (sem depender das DLLs do compilador)
if(MINGW)
    target_link_options(sqlitebridge PRIVATE -static)
elseif(MSVC)
    set_property(TARGET sqlitebridge bridge_core sqlite3 PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded")
endif()

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bridge_core PRIVATE -Wall -Wextra)
    target_compile_options(sqlitebridge PRIVATE -Wall -Wextra)
endif()

enable_testing()
add_executable(test_bridge test_bridge.c)
target_link_libraries(test_bridge PRIVATE bridge_core)
add_test(NAME bridge_core COMMAND test_bridge)
# um caminho invalido para o .db precisa fazer a ponte responder "ERR" no .RSP (nao travar)
add_test(NAME bridge_err_arquivo_invalido COMMAND test_bridge $<TARGET_FILE:sqlitebridge>)
