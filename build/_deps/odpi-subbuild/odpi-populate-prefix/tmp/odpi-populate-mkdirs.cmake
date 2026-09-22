# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file LICENSE.rst or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION ${CMAKE_VERSION}) # this file comes with cmake

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "C:/Users/giova/Projetos/Help/build/_deps/odpi-src")
  file(MAKE_DIRECTORY "C:/Users/giova/Projetos/Help/build/_deps/odpi-src")
endif()
file(MAKE_DIRECTORY
  "C:/Users/giova/Projetos/Help/build/_deps/odpi-build"
  "C:/Users/giova/Projetos/Help/build/_deps/odpi-subbuild/odpi-populate-prefix"
  "C:/Users/giova/Projetos/Help/build/_deps/odpi-subbuild/odpi-populate-prefix/tmp"
  "C:/Users/giova/Projetos/Help/build/_deps/odpi-subbuild/odpi-populate-prefix/src/odpi-populate-stamp"
  "C:/Users/giova/Projetos/Help/build/_deps/odpi-subbuild/odpi-populate-prefix/src"
  "C:/Users/giova/Projetos/Help/build/_deps/odpi-subbuild/odpi-populate-prefix/src/odpi-populate-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "C:/Users/giova/Projetos/Help/build/_deps/odpi-subbuild/odpi-populate-prefix/src/odpi-populate-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "C:/Users/giova/Projetos/Help/build/_deps/odpi-subbuild/odpi-populate-prefix/src/odpi-populate-stamp${cfgdir}") # cfgdir has leading slash
endif()
