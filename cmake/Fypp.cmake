include_guard(GLOBAL)
cmake_minimum_required(VERSION 3.20)
# CMake version compatibility
# TODO: Remove when cmake 3.25 is commonly distributed
if (POLICY CMP0140)
	cmake_policy(SET CMP0140 NEW)
endif ()
if (POLICY CMP0118)
	cmake_policy(SET CMP0118 NEW)
endif ()

#[==============================================================================================[
#                                         Preparations                                         #
]==============================================================================================]

# Find the appropriate fypp executable
find_package(Python3 REQUIRED)
cmake_path(GET Python3_EXECUTABLE PARENT_PATH Python3_BINDIR)
find_program(
		Fypp_EXECUTABLE
		NAMES fypp
		HINTS "${Python3_BINDIR}"
		DOC "Fypp preprocessor"
)
mark_as_advanced(Fypp_EXECUTABLE)

#[==============================================================================================[
#                                        Main interface                                        #
]==============================================================================================]

function(Fypp_target_sources target)
	#[===[
	# Fypp_target_sources

	Equivalent to `target_sources`. Separates the fypp file sources from the non-fypp files, passing the latter
	directly to the `target_sources`. Does not support `FILE_SET` interface yet.

	This is the preferred interface format over `Fypp_add_library` and `Fypp_add_executable`.

	## Notes

	- Due to cmake limitations only the target properties derived up to the point of this function call are parsed,
	  including those defined with `target_compile_definitions`.
	  [Upstream discussion](https://discourse.cmake.org/t/add-custom-command-with-target-properties-at-build-time/8464)

	## Synopsis
	```cmake
	```
	TODO: Documentation
	]===]

	set(ARGS_Options "")
	set(ARGS_OneValue "FILE_SET")
	set(ARGS_MultiValue "INTERFACE;PUBLIC;PRIVATE")
	cmake_parse_arguments(PARSE_ARGV 1 ARGS "${ARGS_Options}" "${ARGS_OneValue}" "${ARGS_MultiValue}")

	if (DEFINED ARGS_FILE_SET)
		# FILE_SET parsing is not yet supported
		# TODO: Figure out how to parse FILE_SET
		message(FATAL_ERROR
				"Fypp: FILE_SET is not yet supported in Fypp_target_sources")
	endif ()

	# Without FILE_SET, all values in ARGS_INTERFACE/PUBLIC/PRIVATE are source files
	# Forward the files to _Fypp_add_source
	foreach (type IN ITEMS INTERFACE PUBLIC PRIVATE)
		if (DEFINED ARGS_${type})
			get_Fypp_sources(FYPP_SOURCES_VAR fypp_sources OTHER_SOURCES_VAR other_sources
					SOURCES ${ARGS_${type}})
			target_sources(${target} ${type} ${other_sources})
			_Fypp_add_source(${target} ${type} ${fypp_sources})
		endif ()
	endforeach ()
endfunction()

function(Fypp_add_library name)
	#[===[
	# Fypp_add_library

	Equivalent to `add_library(<name> [<type>])` and `Fypp_target_sources(<name> PRIVATE <sources>)`

	## Synopsis
	```cmake
	```
	TODO: Documentation
	]===]
	set(ARGS_Options "STATIC;SHARED;OBJECT;MODULE;EXCLUDE_FROM_ALL;IMPORTED;ALIAS")
	set(ARGS_OneValue "")
	set(ARGS_MultiValue "")
	cmake_parse_arguments(PARSE_ARGV 1 ARGS "${ARGS_Options}" "${ARGS_OneValue}" "${ARGS_MultiValue}")

	if (ARGS_IMPORTED OR ARGS_ALIAS)
		# IMPORTED and ALIAS library types are ill-defined with Fypp
		message(FATAL_ERROR
				"Fypp: IMPORTED and ALIAS library types are ill-defined as Fypp libraries")
	endif ()

	# Gather the add_library inputs
	# Input sanitization will be done by base add_library
	set(add_library_inputs "")
	if (ARGS_STATIC)
		list(APPEND add_library_inputs STATIC)
	endif ()
	if (ARGS_SHARED)
		list(APPEND add_library_inputs SHARED)
	endif ()
	if (ARGS_MODULE)
		list(APPEND add_library_inputs MODULE)
	endif ()
	if (ARGS_OBJECT)
		list(APPEND add_library_inputs OBJECT)
	endif ()
	if (ARGS_EXCLUDE_FROM_ALL)
		list(APPEND add_library_inputs EXCLUDE_FROM_ALL)
	endif ()

	# Create the base library target
	add_library(${name} ${add_library_inputs})

	# All other arguments should be source files
	if (DEFINED ARGS_UNPARSED_ARGUMENTS)
		Fypp_target_sources(${name} PRIVATE ${ARGS_UNPARSED_ARGUMENTS})
	endif ()
endfunction()

function(Fypp_add_executable name)
	#[===[
	# Fypp_add_executable

	Equivalent to `add_executable(<name>)` and `Fypp_target_sources(<name> PRIVATE <sources>)`

	## Synopsis
	```cmake
	```
	TODO: Documentation
	]===]
	set(ARGS_Options "WIN32;MACOSX_BUNDLE;EXCLUDE_FROM_ALL;IMPORTED;ALIAS")
	set(ARGS_OneValue "")
	set(ARGS_MultiValue "")
	cmake_parse_arguments(PARSE_ARGV 1 ARGS "${ARGS_Options}" "${ARGS_OneValue}" "${ARGS_MultiValue}")

	if (ARGS_IMPORTED OR ARGS_ALIAS)
		# IMPORTED and ALIAS library types are ill-defined with Fypp
		message(FATAL_ERROR
				"Fypp: IMPORTED and ALIAS library types are ill-defined as Fypp libraries")
	endif ()

	# Gather the add_executable inputs
	# Input sanitization will be done by base add_executable
	set(add_executable_inputs "")
	if (ARGS_WIN32)
		list(APPEND add_executable_inputs WIN32)
	endif ()
	if (ARGS_MACOSX_BUNDLE)
		list(APPEND add_executable_inputs MACOSX_BUNDLE)
	endif ()
	if (ARGS_EXCLUDE_FROM_ALL)
		list(APPEND add_executable_inputs EXCLUDE_FROM_ALL)
	endif ()

	# Create the base executable target
	add_executable(${name} ${add_executable_inputs})

	# All other arguments should be source files
	if (DEFINED ARGS_UNPARSED_ARGUMENTS)
		Fypp_target_sources(${name} PRIVATE ${ARGS_UNPARSED_ARGUMENTS})
	endif ()
endfunction()

#[==============================================================================================[
#                                      Auxiliary interface                                      #
]==============================================================================================]

function(get_Fypp_sources)
	#[===[
	# get_Fypp_sources

	Separate the fypp files from the other source files

	## Synopsis
	```cmake
	```
	TODO: Documentation
	]===]
	set(ARGS_Options "")
	set(ARGS_OneValue "FYPP_SOURCES_VAR;OTHER_SOURCES_VAR")
	set(ARGS_MultiValue "SOURCES")
	cmake_parse_arguments(PARSE_ARGV 0 ARGS "${ARGS_Options}" "${ARGS_OneValue}" "${ARGS_MultiValue}")

	if (NOT DEFINED ARGS_FYPP_SOURCES_VAR)
		message(FATAL_ERROR
				"Fypp: FYPP_SOURCES_VAR is required for get_Fypp_sources() function")
	endif ()
	if (NOT DEFINED ARGS_SOURCES)
		message(FATAL_ERROR
				"Fypp: SOURCES is required for get_Fypp_sources() function")
	endif ()

	# Initialize the output variables to empty
	set(${ARGS_FYPP_SOURCES_VAR} "")
	if (DEFINED ARGS_OTHER_SOURCES_VAR)
		set(${ARGS_OTHER_SOURCES_VAR} "")
	endif ()

	# Loop through the sources and check the extension
	foreach (source IN LISTS ARGS_SOURCES)
		cmake_path(GET source EXTENSION LAST_ONLY source_ext)
		if (source_ext MATCHES fypp|fpp|FYPP|FPP)
			list(APPEND ${ARGS_FYPP_SOURCES_VAR} ${source})
		elseif (DEFINED ARGS_OTHER_SOURCES_VAR)
			list(APPEND ${ARGS_OTHER_SOURCES_VAR} ${source})
		endif ()
	endforeach ()

	# Return the values to the caller
	if (CMAKE_VERSION VERSION_LESS 3.25)
		# TODO: Remove when cmake 3.25 is commonly distributed
		set(${ARGS_FYPP_SOURCES_VAR} ${${ARGS_FYPP_SOURCES_VAR}} PARENT_SCOPE)
		if (DEFINED ARGS_OTHER_SOURCES_VAR)
			set(${ARGS_OTHER_SOURCES_VAR} ${${ARGS_OTHER_SOURCES_VAR}} PARENT_SCOPE)
		endif ()
	else ()
		return(PROPAGATE
				${ARGS_FYPP_SOURCES_VAR}
				# TODO: Does this one work when none is defined?
				${ARGS_OTHER_SOURCES_VAR}
				)
	endif ()
endfunction()

#[==============================================================================================[
#                                       Private interface                                       #
]==============================================================================================]

# Main implementation
function(_Fypp_add_source target type)
	#[===[
	# _Fypp_add_source

	Main implementation of the fypp wrapper.
	Adds fypp generated source to target with appropriate add_custom_command dependencies
	]===]

	# Early return if no sources are passed
	if (NOT ARGN)
		return()
	endif ()

	# Create a pseudo file with the fypp metadata
	get_property(target_bindir TARGET ${target}
			PROPERTY BINARY_DIR)
	# TODO: Get the appropriate path to `target.dir` folder
	# TODO: back-port cmake_path or convert to get_filename_component
	cmake_path(APPEND target_bindir CMakeFiles ${target}.dir OUTPUT_VARIABLE target_cmake_bindir)
	cmake_path(APPEND target_cmake_bindir fypp_files OUTPUT_VARIABLE target_fypp_files)
	if (NOT EXISTS ${target_fypp_files})
		# Create the main custom_command with appropriate COMMENT
		# TODO: Add depfile support
		add_custom_command(OUTPUT ${target_fypp_files}
				# Make sure all the parent directories exist
				COMMAND ${CMAKE_COMMAND} -E make_directory ${target_cmake_bindir}
				# Initialize the file fypp_files with the name of the target
				COMMAND ${CMAKE_COMMAND} -E echo "${target}:" ${target_fypp_files}
				COMMENT "Parsing the fypp files for ${target} target"
				WORKING_DIRECTORY ${target_bindir}
				)
	endif ()

	# Get the target properties to forward them to fypp
	# Note: This does not pick up the final properties used at build time or genex
	# https://discourse.cmake.org/t/add-custom-command-with-target-properties-at-build-time/8464
	get_property(target_defines TARGET ${target}
			PROPERTY COMPILE_DEFINITIONS)
	get_property(target_includes TARGET ${target}
			PROPERTY INCLUDE_DIRECTORIES)
	# Normalize the properties to fypp format
	set(define_flags "")
	foreach (define IN LISTS target_defines)
#		string(REGEX REPLACE "=(.*)" "=\"\\1\"" define_sanitized ${define})
#		list(APPEND define_flags "-D${define_sanitized}")
		string(REGEX REPLACE "=(.*)" "=\"\\1\"" define_sanitized ${define})
		list(APPEND define_flags "-D${define}")
	endforeach ()
	set(include_flags "")
	foreach (include IN LISTS target_includes)
		list(APPEND include_flags "-I${include}")
	endforeach ()

	set(fypp_compiled_files "")
	# Add each fypp file to add_custom_command
	foreach (source IN LISTS ARGN)
		# Get the absolute path of the source file
		if (IS_ABSOLUTE source)
			cmake_path(NATIVE_PATH source NORMALIZE source_path)
		else ()
			cmake_path(ABSOLUTE_PATH source NORMALIZE OUTPUT_VARIABLE source_path_abs)
			cmake_path(NATIVE_PATH source_path_abs NORMALIZE source_path)
		endif ()
		# Create a variable for the output file
		cmake_path(RELATIVE_PATH source_path BASE_DIRECTORY ${PROJECT_SOURCE_DIR}
				OUTPUT_VARIABLE rel_path)
		cmake_path(APPEND target_cmake_bindir ${rel_path}.f90 OUTPUT_VARIABLE out_file)
		cmake_path(NATIVE_PATH out_file NORMALIZE out_path)
		# Append fypp command to the main target custom_command
		add_custom_command(OUTPUT ${out_file}
				# Append the name of the generated files to the fypp_files
				# TODO: This might duplicate the file names when dependency is rerun
				COMMAND ${CMAKE_COMMAND} -E echo ${out_file} >> ${target_fypp_files}
				COMMAND ${Fypp_EXECUTABLE} -p ${define_flags} ${include_flags} ${source_path} ${out_path}
				DEPENDS ${source}
				COMMENT "Adding file ${out_file}")
		set_source_files_properties(${out_file} PROPERTIES
				GENERATED True)
		list(APPEND fypp_compiled_files ${out_file})
	endforeach ()
	# Finally add the generated source to the target
	# TODO: Sanitize the output files better to not duplicate folder structure
	target_sources(${target} ${type} ${fypp_compiled_files})
endfunction()
