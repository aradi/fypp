list(APPEND build_options
		"-DCMAKE_MODULE_PATH=${PROJECT_SOURCE_DIR}/cmake"
)
foreach (test IN ITEMS fypp)
	set(args)
	if (build_options)
		list(APPEND args BUILD_OPTIONS ${build_options})
	endif ()
	if (test_command)
		list(APPEND args TEST_COMMAND ${test_command})
	endif ()
	Fypp_add_test(${test_dir_rel}/${test} ${args})
endforeach ()
