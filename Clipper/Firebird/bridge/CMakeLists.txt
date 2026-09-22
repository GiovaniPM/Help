cmake_minimum_required(VERSION 3.14)
project(fbbridge C)

# FBBRIDGE.EXE - ponte entre FIREBIRD.LIB (Clipper 5.2) e o Firebird.
#
#   cmake -S . -B build
#   cmake --build build
#   ctest --test-dir build --output-on-failure      (testes sem banco)
#
# O acesso ao Firebird usa a API classica (ibase.h + fbclient), que vem pronta na
# instalacao do Firebird (servidor ou so o pacote de cliente) -- diferente do ODPI-C
# usado antes para o Oracle, nao e um conjunto de fontes simples para baixar do
# GitHub e compilar junto. Se o CMake nao achar sozinho, informe a pasta da
# instalacao:
#
#   cmake -S . -B build -DFIREBIRD_ROOT="C:/Program Files/Firebird/Firebird_5_0"
#
# Em execucao o programa precisa do fbclient.dll/.so (mesma arquitetura, 32/64
# bits, do executavel) no PATH ou na mesma pasta do FBBRIDGE.EXE.

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(FIREBIRD_ROOT "" CACHE PATH "Pasta de instalacao do Firebird (contem include/ibase.h e lib/fbclient)")

find_path(FIREBIRD_INCLUDE_DIR
    NAMES ibase.h
    HINTS "${FIREBIRD_ROOT}/include"
    PATHS
        "C:/Program Files/Firebird/Firebird_5_0/include"
        "C:/Program Files/Firebird/Firebird_4_0/include"
        "C:/Program Files/Firebird/Firebird_3_0/include"
        "C:/Program Files (x86)/Firebird/Firebird_5_0/include"
        "C:/Program Files (x86)/Firebird/Firebird_4_0/include"
        "C:/Program Files (x86)/Firebird/Firebird_3_0/include"
        /opt/firebird/include
        /usr/include
        /usr/include/firebird
        /usr/local/include
)

find_library(FIREBIRD_LIBRARY
    NAMES fbclient fbclient_ms libfbclient
    HINTS "${FIREBIRD_ROOT}/lib"
    PATHS
        "C:/Program Files/Firebird/Firebird_5_0/lib"
        "C:/Program Files/Firebird/Firebird_4_0/lib"
        "C:/Program Files/Firebird/Firebird_3_0/lib"
        "C:/Program Files (x86)/Firebird/Firebird_5_0/lib"
        "C:/Program Files (x86)/Firebird/Firebird_4_0/lib"
        "C:/Program Files (x86)/Firebird/Firebird_3_0/lib"
        /opt/firebird/lib
        /usr/lib
        /usr/lib/firebird
        /usr/lib/x86_64-linux-gnu
        /usr/local/lib
)

if(NOT FIREBIRD_INCLUDE_DIR OR NOT FIREBIRD_LIBRARY)
    message(FATAL_ERROR
        "Nao encontrei o cliente do Firebird (ibase.h / fbclient).\n"
        "Instale o Firebird (servidor ou so o pacote de cliente) e rode o cmake de novo com:\n"
        "  -DFIREBIRD_ROOT=\"<pasta da instalacao do Firebird>\"\n"
        "(ex.: \"C:/Program Files/Firebird/Firebird_5_0\" no Windows, ou a pasta onde o\n"
        "pacote firebird3.0-dev / libfbclient2-dev foi instalado no Linux).")
endif()

add_library(firebird_client INTERFACE)
target_include_directories(firebird_client INTERFACE ${FIREBIRD_INCLUDE_DIR})
target_link_libraries(firebird_client INTERFACE ${FIREBIRD_LIBRARY})

# parte sem dependencia do Firebird (requisicao, binds, DBF): testavel isoladamente
add_library(bridge_core STATIC bridge_core.c)
target_include_directories(bridge_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(fbbridge fbbridge.c)
target_link_libraries(fbbridge PRIVATE bridge_core firebird_client)
set_target_properties(fbbridge PROPERTIES OUTPUT_NAME FBBRIDGE)

# fbbridge.c usa pow() de <math.h> (conversao dos binds numericos)
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang" AND NOT WIN32)
    target_link_libraries(fbbridge PRIVATE m)
endif()

# executavel independente (sem depender das DLLs do compilador)
if(MINGW)
    target_link_options(fbbridge PRIVATE -static)
elseif(MSVC)
    set_property(TARGET fbbridge bridge_core PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded")
endif()

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bridge_core PRIVATE -Wall -Wextra)
    target_compile_options(fbbridge PRIVATE -Wall -Wextra)
endif()

enable_testing()
add_executable(test_bridge test_bridge.c)
target_link_libraries(test_bridge PRIVATE bridge_core)
add_test(NAME bridge_core COMMAND test_bridge)
# sem cliente Firebird nem banco, a ponte precisa responder "ERR" no .RSP (nao travar)
add_test(NAME bridge_err_sem_banco COMMAND test_bridge $<TARGET_FILE:fbbridge>)
