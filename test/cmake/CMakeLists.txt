function(Fypp_add_test test_dir)
	#[===[.md:
	# Fypp_add_test

	Internal function for adding Fypp cmake tests

	## Synopsis
	```cmake
	Main interface
	  Fypp_add_test(<test_dir>
	  		[TEST_NAME <name>]
	  		[CTEST_OPTIONS <args> ...]
	  		[BUILD_OPTIONS <args> ...])
	```

	## Options
	`<test_dir>`
	  Path to the test CMake project

	`TEST_NAME` [Default `<test_dir>`]
	  Name of the test

	`CTEST_OPTIONS`
	  Additional test commands passed to the nested ctest call

	`BUILD_OPTIONS`
	  CMake configure options passed to the testing cmake

	## See also
	- <inv:cmake:std:label:build and test mode>

	]===]


	set(ARGS_Options
	)
	set(ARGS_OneValue
			TEST_NAME
	)
	set(ARGS_MultiValue
			BUILD_OPTIONS
			CTEST_OPTIONS
	)

	cmake_parse_arguments(PARSE_ARGV 1 ARGS "${ARGS_Options}" "${ARGS_OneValue}" "${ARGS_MultiValue}")

	# Resolve default options
	if (NOT DEFINED ARGS_TEST_NAME)
		set(ARGS_TEST_NAME ${test_dir})
	endif ()

	add_test(NAME ${ARGS_TEST_NAME} COMMAND ${CMAKE_CTEST_COMMAND}
			--build-and-test
			${CMAKE_CURRENT_FUNCTION_LIST_DIR}/${test_dir}
			${CMAKE_CURRENT_BINARY_DIR}/${test_dir}
			--build-generator "${CMAKE_GENERATOR}"
			--build-options
			${ARGS_BUILD_OPTIONS}
			--test-command ${CMAKE_CTEST_COMMAND} --test-dir=${CMAKE_CURRENT_BINARY_DIR}/${test_dir} --no-tests=ignore ${ARGS_CTEST_OPTIONS}
	)
endfunction()

set(build_options)
set(ctest_options)
set(test_dir_rel)
foreach (test_dir IN ITEMS
		module
)
	block()
		cmake_path(APPEND test_dir_rel ${test_dir})
		add_subdirectory(${test_dir})
	endblock()
endforeach ()
