#:mute
#:def ASSERT_CODE(code)
$:code
#:enddef ASSERT_CODE

#:def ASSERT()
${_THIS_FILE_}$:${_THIS_LINE_}$|${_FILE_}$:${_LINE_}$
#:enddef ASSERT
#:endmute
