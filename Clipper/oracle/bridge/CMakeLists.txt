cmake_minimum_required(VERSION 3.14)
project(orabridge C)

# ORABRIDGE.EXE - ponte entre ORACLE.LIB (Clipper 5.2) e o Oracle.
#
#   cmake -S . -B build
#   cmake --build build
#   ctest --test-dir build --output-on-failure      (testes sem banco)
#
# O acesso ao Oracle usa o ODPI-C, baixado do GitHub na primeira configuracao. Sem
# internet, aponte para uma copia local:  -DFETCHCONTENT_SOURCE_DIR_ODPI=<pasta do odpi>
# Em execucao o programa precisa do Oracle Instant Client (mesma arquitetura, 32/64
# bits, do executavel) no PATH ou na mesma pasta do ORABRIDGE.EXE.

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(odpi
    GIT_REPOSITORY https://github.com/oracle/odpi.git
    GIT_TAG        v5.6.4
    GIT_SHALLOW    TRUE)
FetchContent_MakeAvailable(odpi)

file(GLOB ODPI_SOURCES CONFIGURE_DEPENDS ${odpi_SOURCE_DIR}/src/*.c)
add_library(odpi STATIC ${ODPI_SOURCES})
target_include_directories(odpi PUBLIC ${odpi_SOURCE_DIR}/include PRIVATE ${odpi_SOURCE_DIR}/src)
if(NOT WIN32)
    target_link_libraries(odpi PUBLIC ${CMAKE_DL_LIBS} pthread)
endif()

# parte sem dependencia do Oracle (requisicao, binds, DBF): testavel isoladamente
add_library(bridge_core STATIC bridge_core.c)
target_include_directories(bridge_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(orabridge orabridge.c)
target_link_libraries(orabridge PRIVATE bridge_core odpi)
set_target_properties(orabridge PROPERTIES OUTPUT_NAME ORABRIDGE)

# executavel independente (sem depender das DLLs do compilador)
if(MINGW)
    target_link_options(orabridge PRIVATE -static)
elseif(MSVC)
    set_property(TARGET orabridge bridge_core odpi PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded")
endif()

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bridge_core PRIVATE -Wall -Wextra)
    target_compile_options(orabridge PRIVATE -Wall -Wextra)
endif()

enable_testing()
add_executable(test_bridge test_bridge.c)
target_link_libraries(test_bridge PRIVATE bridge_core)
add_test(NAME bridge_core COMMAND test_bridge)
# sem Oracle Client nem banco, a ponte precisa responder "ERR" no .RSP (nao travar)
add_test(NAME bridge_err_sem_banco COMMAND test_bridge $<TARGET_FILE:orabridge>)
