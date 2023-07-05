# Basic tests
add_test(NAME version
        COMMAND ${CMAKE_Fypp_COMPILER} --version)

# Integration tests
add_subdirectory(cmake)
