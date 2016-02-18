import unittest
import fypp


def _strsyncl(linenr):
    return fypp.syncline(linenr, fypp.STRING)

def _filesyncl(fname, linenr):
    return fypp.syncline(linenr, fname)


def _defvar(var, val):
    return '-D{}={}'.format(var, val)

def _incdir(path):
    return '-I{}'.format(path)


_SYNCL_FLAG = '-s'


simple_tests = [
    ('if_true', [ _defvar('TESTVAR', 1) ],
     '@:if TESTVAR > 0\nTrue\n@:endif\n',
     'True\n'
     ),
    #
    ('if_false', [ _defvar('TESTVAR', 0) ],
     '@:if TESTVAR > 0\nTrue\n@:endif\n',
     ''
     ),
    #
    ('if_else_true', [ _defvar('TESTVAR', 1) ],
     '@:if TESTVAR > 0\nTrue\n@:else\nFalse\n@:endif\n',
     'True\n'
     ),
    #
    ('if_else_false', [ _defvar('TESTVAR', 0) ],
     '@:if TESTVAR > 0\nTrue\n@:else\nFalse\n@:endif\n',
     'False\n'
     ),
    #
    ('if_elif_true1', [ _defvar('TESTVAR', 1) ],
     '@:if TESTVAR == 1\nTrue1\n@:elif TESTVAR == 2\nTrue2\n@:endif\n',
     'True1\n'
     ),
    #
    ('if_elif_true2', [ _defvar('TESTVAR', 2) ],
     '@:if TESTVAR == 1\nTrue1\n@:elif TESTVAR == 2\nTrue2\n@:endif\n',
     'True2\n'
     ),
    #
    ('if_elif_false', [ _defvar('TESTVAR', 0) ],
     '@:if TESTVAR == 1\nTrue1\n@:elif TESTVAR == 2\nTrue2\n@:endif\n',
     ''
     ),
    #
    ('if_elif_else_true1', [ _defvar('TESTVAR', 1) ],
     '@:if TESTVAR == 1\nTrue1\n@:elif TESTVAR == 2\nTrue2\n'
     '@:else\nFalse\n@:endif\n',
     'True1\n'
     ),
    #
    ('if_elif_else_true2', [ _defvar('TESTVAR', 2) ],
     '@:if TESTVAR == 1\nTrue1\n@:elif TESTVAR == 2\nTrue2\n'
     '@:else\nFalse\n@:endif\n',
     'True2\n'
     ),
    #
    ('if_elif_else_false', [ _defvar('TESTVAR', 0) ],
     '@:if TESTVAR == 1\nTrue1\n@:elif TESTVAR == 2\nTrue2\n'
     '@:else\nFalse\n@:endif\n',
     'False\n'
     ),
    #
    ('inline_if_true', [ _defvar('TESTVAR', 1) ],
     '@{if TESTVAR > 0}@True@{endif}@Done',
     'TrueDone'
     ),
    #
    ('inline_if_false', [ _defvar('TESTVAR', 0) ],
     '@{if TESTVAR > 0}@True@{endif}@Done',
     'Done'
     ),
    #
    ('inline_if_else_true', [ _defvar('TESTVAR', 1) ],
     '@{if TESTVAR > 0}@True@{else}@False@{endif}@Done',
     'TrueDone'
     ),
    #
    ('inline_if_else_false', [ _defvar('TESTVAR', 0) ],
     '@{if TESTVAR > 0}@True@{else}@False@{endif}@Done',
     'FalseDone'
     ),
    #
    ('inline_if_elif_true1', [ _defvar('TESTVAR', 1) ],
     '@{if TESTVAR == 1}@True1@{elif TESTVAR == 2}@True2@{endif}@Done',
     'True1Done'
     ),
    #
    ('inline_if_elif_true2', [ _defvar('TESTVAR', 2) ],
     '@{if TESTVAR == 1}@True1@{elif TESTVAR == 2}@True2@{endif}@Done',
     'True2Done'
     ),
    #
    ('inline_if_elif_false', [ _defvar('TESTVAR', 0) ],
     '@{if TESTVAR == 1}@True1@{elif TESTVAR == 2}@True2@{endif}@Done',
     'Done'
     ),
    #
    ('inline_if_elif_else_true1', [ _defvar('TESTVAR', 1) ],
     '@{if TESTVAR == 1}@True1@{elif TESTVAR == 2}@True2@{else}@False@{endif}@'
     'Done',
     'True1Done'
     ),
    #
    ('inline_if_elif_else_true2', [ _defvar('TESTVAR', 2) ],
     '@{if TESTVAR == 1}@True1@{elif TESTVAR == 2}@True2@{else}@False@{endif}@'
     'Done',
     'True2Done'
     ),
    #
    ('inline_if_elif_else_false', [ _defvar('TESTVAR', 0) ],
     '@{if TESTVAR == 1}@True1@{elif TESTVAR == 2}@True2@{else}@False@{endif}@'
     'Done',
     'FalseDone'
     ),
    #
    ('exprsub', [ _defvar('TESTVAR', 0) ],
     '<${TESTVAR}$ x ${ 2 - 3 }$>',
     '<0 x -1>'
     ),
    #
    ('linesub_no_eol', [ _defvar('TESTVAR', 1) ],
     '$: TESTVAR + 1',
     '2'
     ),
    #
    ('linesub_eol', [ _defvar('TESTVAR', 1) ],
     'A\n$: TESTVAR + 1\nB\n',
     'A\n2\nB\n'
     ),
    #
    ('linesub_contlines', [ _defvar('TESTVAR', 1) ],
     '$: TESTVAR & \n  & + 1',
     '2'
     ),
    #
    ('linesub_contlines2', [ _defvar('TESTVAR', 1) ],
     '$: TEST& \n  &VAR & \n  & + 1',
     '2'
     ),
    #
    ('linesub_contlines_contchar1', [],
     '$: \'hello&\n  world\'\n',
     'hello  world\n'
     ),
    #
    ('linesub_contlines2_contchar1', [],
     '$: \'hello&\n  world&\n  !\'\n',
     'hello  world  !\n'
     ),
    #
    ('exprsub', [ _defvar('TESTVAR', 1) ],
     'A${TESTVAR}$B${TESTVAR + 1}$C',
     'A1B2C'
     ),
    #
    ('exprsub_ignored_contlines', [ _defvar('TESTVAR', 1) ],
     'A${TEST&\n  &VAR}$B${TESTVAR + 1}$C',
     'A${TEST&\n  &VAR}$B2C'
     ),
    #
    ('macrosubs', [],
     '@:def macro(var)\nMACRO|${var}$|\n@:enddef\n${macro(1)}$',
     'MACRO|1|'
     ),
    #
    ('recursive_macrosubs', [],
     '@:def macro(var)\nMACRO|${var}$|\n@:enddef\n${macro(macro(1))}$',
     'MACRO|MACRO|1||'
     ),
    #
    ('macrosubs_extvarsubs', [ _defvar('TESTVAR', 1) ],
     '@:def macro(var)\nMACRO|${var}$-${TESTVAR}$|\n@:enddef\n${macro(2)}$',
     'MACRO|2-1|'
     ),
    #
    ('macrosubs_extvar_override', [ _defvar('TESTVAR', 1) ],
     '@:def macro(var)\nMACRO|${var}$-${TESTVAR}$|\n@:enddef\n'
     '${macro(2, TESTVAR=4)}$',
     'MACRO|2-4|'
     ),
    #
    ('inline_macrodef', [],
     '@{def f(x)}@${x}$^2@{enddef}@\n$: f(20)\nDone\n',
     '\n20^2\nDone\n'
     ),
    #
    ('for', [],
     '@:for i in (1, 2, 3)\n${i}$\n@:endfor\n',
     '1\n2\n3\n'
     ),
    #
    ('for_macro', [],
     '@:def mymacro(val)\nVAL:${val}$\n@:enddef\n'
     '@:for i in (1, 2, 3)\n$: mymacro(i)\n@:endfor\n',
     'VAL:1\nVAL:2\nVAL:3\n'
     ),
    #
    ('inline_for', [],
     '@{for i in (1, 2, 3)}@${i}$@{endfor}@Done\n',
     '123Done\n'
     ),
    #
    ('inline_for_macro', [],
     '@:def mymacro(val)\nVAL:${val}$\n@:enddef\n'
     '@{for i in (1, 2, 3)}@${mymacro(i)}$@{endfor}@Done\n',
     'VAL:1VAL:2VAL:3Done\n'
     ),
    #
    ('comment_single', [],
     ' @! Comment here\nDone\n',
     'Done\n',
     ),
    #
    ('comment_multiple', [],
     ' @! Comment1\n@! Comment2\nDone\n',
     'Done\n',
     ),
    #
    ('setvar', [],
     '@:setvar x 2\n$: x\n',
     '2\n',
     ),
    #
    ('inline_setvar', [],
     '@{setvar x 2}@${x}$Done\n',
     '2Done\n',
     ),
    #
    ('mute', [],
     'A\n@:mute\nB\n@:setvar VAR 2\n@:endmute\nVAR=${VAR}$\n',
     'A\nVAR=2\n'
     ),
]

syncline_tests = [
    # This test (but only this) must be changed, if syncline format changes.
    ('explicit_str_syncline_test', [ _SYNCL_FLAG ],
     '',
     '# 1 "<string>"\n',
     ),
    #
    ('trivial', [ _SYNCL_FLAG ],
     'Test\n',
     _strsyncl(0) + 'Test\n'
     ),
    #
    ('if_true', [ _SYNCL_FLAG ],
     '@:if 1 < 2\nTrue\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(1) + 'True\n' + _strsyncl(3) + 'Done\n'
     ),
    #
    ('if_false', [ _SYNCL_FLAG ],
     '@:if 1 > 2\nTrue\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(3) + 'Done\n'
     ),
    #
    ('if_else_true', [ _SYNCL_FLAG ],
     '@:if 1 < 2\nTrue\n@:else\nFalse\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(1) + 'True\n' + _strsyncl(5) + 'Done\n'
     ),
    #
    ('if_else_false', [ _SYNCL_FLAG ],
     '@:if 1 > 2\nTrue\n@:else\nFalse\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(3) + 'False\n' + _strsyncl(5) + 'Done\n'
     ),
    ('if_elif_true1', [ _SYNCL_FLAG ],
     '@:if 1 == 1\nTrue1\n@:elif 1 == 2\nTrue2\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(1) + 'True1\n' + _strsyncl(5) + 'Done\n'
     ),
    #
    ('if_elif_true2', [ _SYNCL_FLAG ],
     '@:if 2 == 1\nTrue1\n@:elif 2 == 2\nTrue2\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(3) + 'True2\n' + _strsyncl(5) + 'Done\n'
     ),
    #
    ('if_elif_false', [ _SYNCL_FLAG ],
     '@:if 0 == 1\nTrue1\n@:elif 0 == 2\nTrue2\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(5) + 'Done\n'
     ),
    #
    ('if_elif_else_true1', [ _SYNCL_FLAG ],
     '@:if 1 == 1\nTrue1\n@:elif 1 == 2\nTrue2\n'
     '@:else\nFalse\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(1) + 'True1\n' + _strsyncl(7) + 'Done\n'
     ),
    #
    ('if_elif_else_true2', [ _SYNCL_FLAG ],
     '@:if 2 == 1\nTrue1\n@:elif 2 == 2\nTrue2\n'
     '@:else\nFalse\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(3) + 'True2\n' + _strsyncl(7) + 'Done\n'
     ),
    #
    ('if_elif_else_false', [ _SYNCL_FLAG ],
     '@:if 0 == 1\nTrue1\n@:elif 0 == 2\nTrue2\n'
     '@:else\nFalse\n@:endif\nDone\n',
     _strsyncl(0) + _strsyncl(5) + 'False\n' + _strsyncl(7) + 'Done\n'
     ),
    #
    ('inline_if_true', [ _SYNCL_FLAG ],
     '@{if 1 < 2}@True@{endif}@Done\n',
     _strsyncl(0) + 'TrueDone\n'
     ),
    #
    ('inline_if_false', [ _SYNCL_FLAG ],
     '@{if 1 > 2}@True@{endif}@Done\n',
     _strsyncl(0) + 'Done\n'
     ),
    #
    ('inline_if_else_true', [ _SYNCL_FLAG ],
     '@{if 1 < 2}@True@{else}@False@{endif}@Done\n',
     _strsyncl(0) + 'TrueDone\n'
     ),
    #
    ('inline_if_else_false', [ _SYNCL_FLAG ],
     '@{if 1 > 2}@True@{else}@False@{endif}@Done\n',
     _strsyncl(0) + 'FalseDone\n'
     ),
    ('inline_if_elif_true1', [ _SYNCL_FLAG ],
     '@{if 1 == 1}@True1@{elif 1 == 2}@True2@{endif}@Done\n',
     _strsyncl(0) + 'True1Done\n'
     ),
    #
    ('inline_if_elif_true2', [ _SYNCL_FLAG ],
     '@{if 2 == 1}@True1@{elif 2 == 2}@True2@{endif}@Done\n',
     _strsyncl(0) + 'True2Done\n'
     ),
    #
    ('inline_if_elif_false', [ _SYNCL_FLAG ],
     '@{if 0 == 1}@True1@{elif 0 == 2}@True2@{endif}@Done\n',
     _strsyncl(0) + 'Done\n'
     ),
    #
    ('inline_if_elif_else_true1', [ _SYNCL_FLAG ],
     '@{if 1 == 1}@True1@{elif 1 == 2}@True2@{else}@False@{endif}@Done\n',
     _strsyncl(0) + 'True1Done\n'
     ),
    #
    ('inline_if_elif_else_true2', [ _SYNCL_FLAG ],
     '@{if 2 == 1}@True1@{elif 2 == 2}@True2@{else}@False@{endif}@Done\n',
     _strsyncl(0) + 'True2Done\n'
     ),
    #
    ('inline_if_elif_else_false', [ _SYNCL_FLAG ],
     '@{if 0 == 1}@True1@{elif 0 == 2}@True2@{else}@False@{endif}@Done\n',
     _strsyncl(0) + 'FalseDone\n'
     ),
    #
    ('linesub_oneline', [ _SYNCL_FLAG ],
     'A\n$: 1 + 1\nB\n',
     _strsyncl(0) + 'A\n2\nB\n'
     ),
    #
    ('linesub_contlines', [ _SYNCL_FLAG, _defvar('TESTVAR', 1) ],
     '$: TESTVAR & \n  & + 1\nDone\n',
     _strsyncl(0) + '2\n' + _strsyncl(2) + 'Done\n'
     ),
    #
    ('linesub_contlines2', [ _SYNCL_FLAG,_defvar('TESTVAR', 1) ],
     '$: TEST& \n  &VAR & \n  & + 1\nDone\n',
     _strsyncl(0) + '2\n' + _strsyncl(3) + 'Done\n'
     ),
    #
    ('exprsub_single_line', [ _SYNCL_FLAG, _defvar('TESTVAR', 1) ],
     'A${TESTVAR}$B${TESTVAR + 1}$C',
     _strsyncl(0) + 'A1B2C'
     ),
    #
    ('exprsub_multi_line', [ _SYNCL_FLAG ],
     '${"line1\\nline2"}$\nDone\n',
     _strsyncl(0) + 'line1\n' + _strsyncl(0) + 'line2\nDone\n'
     ),
    #
    ('macrosubs', [ _SYNCL_FLAG ],
     '@:def macro(var)\nMACRO|${var}$|\n@:enddef\n${macro(1)}$',
     _strsyncl(0) + _strsyncl(3) + 'MACRO|1|'
     ),
    #
    ('recursive_macrosubs', [ _SYNCL_FLAG ],
     '@:def macro(var)\nMACRO|${var}$|\n@:enddef\n${macro(macro(1))}$',
     _strsyncl(0) + _strsyncl(3) + 'MACRO|MACRO|1||'
     ),
    #
    ('macrosubs_multiline', [ _SYNCL_FLAG ],
     '@:def macro(c)\nMACRO1|${c}$|\nMACRO2|${c}$|\n@:enddef\n${macro(\'A\')}$'
     '\n',
     _strsyncl(0) + _strsyncl(4) + 'MACRO1|A|\n' + _strsyncl(4) + 'MACRO2|A|\n'
     ),
    #
    ('recursive_macrosubs_multiline', [ _SYNCL_FLAG ],
     '@:def f(c)\nLINE1|${c}$|\nLINE2|${c}$|\n@:enddef\n$: f(f("A"))\n',
     (_strsyncl(0) + _strsyncl(4) + 'LINE1|LINE1|A|\n' + _strsyncl(4)
      + 'LINE2|A||\n' + _strsyncl(4) + 'LINE2|LINE1|A|\n' + _strsyncl(4)
      + 'LINE2|A||\n')
     ),
    # 
    ('multiline_macrocall', [ _SYNCL_FLAG ],
     '@:def macro(c)\nMACRO|${c}$|\n@:enddef\n$: mac& \n  &ro(\'A\')\nDone\n',
     _strsyncl(0) + _strsyncl(3) + 'MACRO|A|\n' + _strsyncl(5) + 'Done\n'
     ),
    #
    ('for', [ _SYNCL_FLAG ],
     '@:for i in (1, 2)\n${i}$\n@:endfor\nDone\n',
     (_strsyncl(0) + _strsyncl(1) + '1\n' + _strsyncl(1) + '2\n' 
      + _strsyncl(3) + 'Done\n')
     ),
    #
    ('inline_for', [ _SYNCL_FLAG ],
     '@{for i in (1, 2)}@${i}$@{endfor}@Done\n',
     _strsyncl(0) + '12Done\n'
     ),
    #
    ('setvar', [ _SYNCL_FLAG ],
     '@:setvar x 2\n$: x\n',
     _strsyncl(0) + _strsyncl(1) + '2\n',
     ),
    #
    ('inline_setvar', [ _SYNCL_FLAG ],
     '@{setvar x 2}@${x}$Done\n',
     _strsyncl(0) + '2Done\n',
     ),
    #
    ('comment_single', [ _SYNCL_FLAG ],
     ' @! Comment here\nDone\n',
     _strsyncl(0) + _strsyncl(1) + 'Done\n'
     ),
    #
    ('comment_multiple', [ _SYNCL_FLAG ],
     ' @! Comment1\n@! Comment2\nDone\n',
     _strsyncl(0) + _strsyncl(2) + 'Done\n',
     ),
    #
    ('mute', [ _SYNCL_FLAG ],
     'A\n@:mute\nB\n@:setvar VAR 2\n@:endmute\nVAR=${VAR}$\n',
     _strsyncl(0) + 'A\n' + _strsyncl(5) + 'VAR=2\n'
     ),
]

include_tests = [
    #
    ('explicit_include', [],
     '@:include "include/fypp1.inc"\n',
     'INCL1\nINCL5\n'
     ),
    #
    ('search_include', [ _incdir('include') ],
     '@:include "fypp1.inc"\n',
     'INCL1\nINCL5\n'
     ),
    #
    ('search_include_syncl', [ _SYNCL_FLAG, _incdir('include') ],
     '@:include "fypp1.inc"\n$: incmacro(1)\n',
     (_strsyncl(0) + _filesyncl('include/fypp1.inc', 0) 
      + 'INCL1\n' + _filesyncl('include/fypp1.inc', 4) 
      + 'INCL5\n' + _strsyncl(1) + 'INCMACRO(1)\n')
     ),
]

exception_tests = [
    #
    # Parser errors
    #
    ('invalid_directive', [],
     '@:invalid\n',
     fypp.FyppParserError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_macrodef', [],
     '@:def alma[x]\n@:enddef\n',
     fypp.FyppParserError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_variable_assign', [],
     '@:setvar A=3\n',
     fypp.FyppParserError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_for_decl', [],
     '@:for i = 1, 2\n',
     fypp.FyppParserError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_include', [],
     '@:include <test.h>\n',
     fypp.FyppParserError, fypp.STRING, (0, 1)
     ),
    #
    ('inline_include', [],
     '@{include "test.h"}@\n',
     fypp.FyppParserError, fypp.STRING, (0, 0)
     ),
    #
    ('wrong_include_file', [],
     '@:include "testfkjsdlfkjslf.h"\n',
     fypp.FyppParserError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_else', [],
     '@:if 1 > 2\nA\n@:else True\nB\n@:endif\n',
     fypp.FyppParserError, fypp.STRING, (2, 3)
     ),
    #
    ('invalid_endif', [],
     '@:if 1 > 2\nA\n@:else\nB\n@:endif INV\n',
     fypp.FyppParserError, fypp.STRING, (4, 5)
     ),
    #
    ('invalid_enddef', [],
     '@:def test(x)\nA:${x}$\n@:enddef INV\n',
     fypp.FyppParserError, fypp.STRING, (2, 3)
     ),
    #
    ('invalid_endfor', [],
     '@:for i in range(5)\n${i}$\n@:endfor INV\n',
     fypp.FyppParserError, fypp.STRING, (2, 3)
     ),
    #
    ('invalid_mute', [],
     '@:mute TEST\n@:endmute\n',
     fypp.FyppParserError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_endmute', [],
     '@:mute\n@:endmute INVALID\n',
     fypp.FyppParserError, fypp.STRING, (1, 2)
     ),
    #
    ('inline_mute', [],
     '@{mute}@test@{endmute}@\n',
     fypp.FyppParserError, fypp.STRING, (0, 0)
     ),
    #
    ('inline_endmute', [],
     '@:mute\ntest@{endmute}@\n',
     fypp.FyppParserError, fypp.STRING, (1, 1)
     ),
    #
    # Builder errors
    #
    ('line_if_inline_endif', [],
     '@:if 1 < 2\nTrue\n@{endif}@\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 2)
     ),
    #
    ('inline_if_line_endif', [],
     '@{if 1 < 2}@True\n@:endif\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('line_if_inline_elif', [],
     '@:if 1 < 2\nTrue\n@{elif 2 > 3}@\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 2)
     ),
    #
    ('inline_if_line_elif', [],
     '@{if 1 < 2}@True\n@:elif 2 > 3\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('line_if_inline_else', [],
     '@:if 1 < 2\nTrue\n@{else}@\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 2)
     ),
    #
    ('inline_if_line_else', [],
     '@{if 1 < 2}@True\n@:else\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('loose_else', [],
     'A\n@:else\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('loose_inline_else', [],
     'A\n@{else}@\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 1)
     ),
    #
    ('loose_elif', [],
     'A\n@:elif 1 > 2\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('loose_inline_elif', [],
     'A\n@{elif 1 > 2}@\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 1)
     ),
    #
    ('loose_endif', [],
     'A\n@:endif\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('loose_inline_endif', [],
     'A\n@{endif}@\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 1)
     ),
    #
    ('mismatching_else', [],
     '@:if 1 < 2\n@:for i in range(3)\n@:else\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 3)
     ),
    #
    ('mismatching_elif', [],
     '@:if 1 < 2\n@:for i in range(3)\n@:elif 1 > 2\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 3)
     ),
    #
    ('mismatching_endif', [],
     '@:if 1 < 2\n@:for i in range(3)\n@:endif\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 3)
     ),
    #
    ('line_def_inline_enddef', [],
     '@:def alma(x)\n@{enddef}@\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 1)
     ),
    #
    ('inline_def_line_enddef', [],
     '@{def alma(x)}@Empty\n@:enddef\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('loose_enddef', [],
     '@:enddef\n',
     fypp.FyppBuilderError, fypp.STRING, (0, 1)
     ),
    #
    ('loose_inline_enddef', [],
     '@{enddef}@\n',
     fypp.FyppBuilderError, fypp.STRING, (0, 0)
     ),
    #
    ('mismatching_enddef', [],
     '@:def test(x)\n@{if 1 < 2}@\n@:enddef\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 3)
     ),
    #
    ('line_for_inline_endfor', [],
     '@:for i in range(3)\nA\n@{endfor}@\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 2)
     ),
    #
    ('inline_for_line_endfor', [],
     '@{for i in range(3)}@Empty\n@:endfor\n',
     fypp.FyppBuilderError, fypp.STRING, (1, 2)
     ),
    #
    ('loose_endfor', [],
     '@:endfor\n',
     fypp.FyppBuilderError, fypp.STRING, (0, 1)
     ),
    #
    ('loose_inline_endfor', [],
     '@{endfor}@',
     fypp.FyppBuilderError, fypp.STRING, (0, 0)
     ),
    #
    ('mismatching_endfor', [],
     '@:for i in range(3)\n@{if 1 < 2}@\n@:endfor\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 3)
     ),
    #
    ('loose_endmute', [],
     '@:endmute\n',
     fypp.FyppBuilderError, fypp.STRING, (0, 1)
     ),
    #
    ('mismatching_endmute', [],
     '@:mute\n@{if 1 < 2}@\n@:endmute\n',
     fypp.FyppBuilderError, fypp.STRING, (2, 3)
     ),
    #
    ('unclosed_directive', [],
     '@:if 1 > 2\nA\n',
     fypp.FyppBuilderError, fypp.STRING, None
     ),
    #
    # Renderer errors
    #
    ('invalid_expression', [],
     '${i}$',
     fypp.FyppRendererError, fypp.STRING, (0, 0)
     ),
    #
    ('invalid_variable', [],
     '@:setvar i 1.2.3\n',
     fypp.FyppRendererError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_condition', [],
     '@{if i >>> 3}@@{endif}@',
     fypp.FyppRendererError, fypp.STRING, (0, 0)
     ),
    #
    ('invalid_iterator', [],
     '@:for i in 1.2.3\nDummy\n@:endfor\n',
     fypp.FyppRendererError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_macro_name', [],
     '@:def __test(x)\n@:enddef\n',
     fypp.FyppRendererError, fypp.STRING, (0, 1)
     ),
    #
    ('invalid_variable_name', [],
     '@:setvar __test 2\n',
     fypp.FyppRendererError, fypp.STRING, (0, 1)
     ),
    #
    ('macro_call_more_args', [],
     '@:def test(x)\n${x}$\n@:enddef\n$: test(\'A\', 1)\n',
     fypp.FyppRendererError, fypp.STRING, (3, 3)
     ),
    #
    ('macro_call_less_args', [],
     '@:def test(x)\n${x}$\n@:enddef\n$: test()\n',
     fypp.FyppRendererError, fypp.STRING, (3, 3)
     ),
    #
    # Command line errors
    # 
    ('def_error', [ '-DVAR=1.2.2'],
     '',
     fypp.FyppCmdLineError, None, None
     ),
    #
    ('missing_module', [ '-mWhateverDummyKJFDKf'],
     '',
     fypp.FyppCmdLineError, None, None
     ),
    #
    ('missing_ini', [ '-iWhateverDummyKJFDKf'],
     '',
     fypp.FyppCmdLineError, None, None
     ),
    #
    ('broken_ini', [ '-iinclude/brokenini.py'],
     '',
     fypp.FyppCmdLineError, None, None
     ),
]
    

class SimpleTest(unittest.TestCase):
    pass


class SynclineTest(unittest.TestCase):
    pass


class IncludeTest(unittest.TestCase):
    pass


class ExceptionTest(unittest.TestCase):
    pass


def test_output_method(args, inp, out):
    def test_output(self):
        tool = fypp.Fypp(args)
        result = tool.process_text(inp)
        self.assertEqual(out, result)
    return test_output


def test_exception_method(args, inp, exc, fname, span):
    def test_exception(self):
        with self.assertRaises(exc) as cm:
            tool = fypp.Fypp(args)
            result = tool.process_text(inp)
        raised = cm.exception
        if fname is None:
            self.assertTrue(raised.fname is None)
        else:
            self.assertEqual(fname, raised.fname)
        if span is None:
            self.assertTrue(raised.span is None)
        else:
            self.assertEqual(span, raised.span)
    return test_exception


def add_test_methods(tests, testclass, methodfactory):
    for ii, test in enumerate(tests):
        name = test[0]
        testargs = test[1:]
        methodname = 'test{}_{}'.format(ii + 1, name)
        setattr(testclass, methodname, methodfactory(*testargs))


add_test_methods(simple_tests, SimpleTest, test_output_method)
add_test_methods(syncline_tests, SynclineTest, test_output_method)
add_test_methods(include_tests, IncludeTest, test_output_method)
add_test_methods(exception_tests, ExceptionTest, test_exception_method)


if __name__ == '__main__':
    unittest.main()
