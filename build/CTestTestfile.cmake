# CMake generated Testfile for 
# Source directory: C:/Users/giova/Projetos/Help/Clipper/Oracle/bridge
# Build directory: C:/Users/giova/Projetos/Help/build
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(bridge_core "C:/Users/giova/Projetos/Help/build/test_bridge.exe")
set_tests_properties(bridge_core PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/giova/Projetos/Help/Clipper/Oracle/bridge/CMakeLists.txt;55;add_test;C:/Users/giova/Projetos/Help/Clipper/Oracle/bridge/CMakeLists.txt;0;")
add_test(bridge_err_sem_banco "C:/Users/giova/Projetos/Help/build/test_bridge.exe" "C:/Users/giova/Projetos/Help/build/ORABRIDGE.exe")
set_tests_properties(bridge_err_sem_banco PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/giova/Projetos/Help/Clipper/Oracle/bridge/CMakeLists.txt;57;add_test;C:/Users/giova/Projetos/Help/Clipper/Oracle/bridge/CMakeLists.txt;0;")
