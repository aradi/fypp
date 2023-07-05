cmake_minimum_required(VERSION 3.15)
# CMake version compatibility
# TODO: Remove when cmake 3.25 is commonly distributed
if (POLICY CMP0140)
    cmake_policy(SET CMP0140 NEW)
endif ()

#[==============================================================================================[
#                                    Basic project defintion                                    #
]==============================================================================================]

project(Fypp
        VERSION 3.1.0
        LANGUAGES NONE)

# Back-porting to PROJECT_IS_TOP_LEVEL to older cmake
# TODO: Remove when requiring cmake >= 3.21
if (NOT DEFINED Fypp_IS_TOP_LEVEL)
    if (CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
        set(PROJECT_IS_TOP_LEVEL ON)
    else ()
        set(PROJECT_IS_TOP_LEVEL OFF)
    endif ()
endif ()

#[==============================================================================================[
#                                            Options                                            #
]==============================================================================================]

option(FYPP_TESTS "Fypp: Build unit tests" ${PROJECT_IS_TOP_LEVEL})
option(FYPP_INSTALL "Fypp: Install project" ${PROJECT_IS_TOP_LEVEL})

#[==============================================================================================[
#                                     Project configuration                                     #
]==============================================================================================]

# Include basic tools
if (FYPP_INSTALL)
    include(CMakePackageConfigHelpers)
    if (UNIX)
        include(GNUInstallDirs)
    endif ()
endif ()
list(PREPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

if (FYPP_TESTS)
    enable_testing()
    add_subdirectory(test)
endif ()

#[==============================================================================================[
#                                       Install or Export                                       #
]==============================================================================================]
# Installation
if (FYPP_INSTALL)
    # cmake export files
    write_basic_package_version_file(
            FyppConfigVersion.cmake
            VERSION ${PROJECT_VERSION}
            COMPATIBILITY SameMinorVersion
            ARCH_INDEPENDENT)
    configure_package_config_file(
            cmake/FyppConfig.cmake.in
            FyppConfig.cmake
            INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/Fypp)
    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/FyppConfigVersion.cmake
            ${CMAKE_CURRENT_BINARY_DIR}/FyppConfig.cmake
            cmake/CMakeDetermineFyppCompiler.cmake
            cmake/CMakeFyppCompiler.cmake.in
            cmake/CMakeFyppInformation.cmake
            cmake/CMakeTestFyppCompiler.cmake
            DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/Fypp)
endif ()

# Make project available for FetchContent
if (NOT PROJECT_IS_TOP_LEVEL)
    # Set variables for FetchContent
    # All variables have to be consistent with FyppConfig.cmake
    # Propagate variables
    if (CMAKE_VERSION VERSION_LESS 3.25)
        # TODO: Remove when cmake 3.25 is commonly distributed
        set(Fypp_VERSION ${Fypp_VERSION} PARENT_SCOPE)
        set(Fypp_VERSION_MAJOR ${Fypp_VERSION_MAJOR} PARENT_SCOPE)
        set(Fypp_VERSION_MINOR ${Fypp_VERSION_MINOR} PARENT_SCOPE)
        set(Fypp_VERSION_PATCH ${Fypp_VERSION_PATCH} PARENT_SCOPE)
        set(Fypp_VERSION_TWEAK ${Fypp_VERSION_TWEAK} PARENT_SCOPE)
        set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} PARENT_SCOPE)
    else ()
        return(PROPAGATE
                Fypp_VERSION
                Fypp_VERSION_MAJOR
                Fypp_VERSION_MINOR
                Fypp_VERSION_PATCH
                Fypp_VERSION_TWEAK
                CMAKE_MODULE_PATH
                )
    endif ()
endif ()
