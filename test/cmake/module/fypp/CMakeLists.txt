cmake_minimum_required(VERSION 3.15)

project(test_fypp LANGUAGES Fortran)
include(Fypp)

Fypp_add_executable(exec src/test_exec.fypp)
#Fypp_add_library(test_obj OBJECT src/test_obj.fypp src/test_bare.f90)
Fypp_add_library(test_static STATIC src/test_static.fypp)
Fypp_add_library(test_shared SHARED src/test_shared.fypp)
add_library(test_obj_other OBJECT)
target_compile_definitions(test_obj_other PRIVATE FOO BAR=some_value)
Fypp_target_sources(test_obj_other PRIVATE src/test_obj.fypp src/test_bare.f90)

enable_testing()
add_test(NAME test_exec COMMAND $<TARGET_FILE:exec>)
