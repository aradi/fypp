'''Unit tests for testing Fypp.'''
import sys
import platform
import unittest
import fypp

def _linenum(linenr, fname=None, flag=None):
    if fname is None:
        fname = fypp.STRING
    return fypp.linenumdir_cpp(linenr, fname, flag)

def _defvar(var, val):
    return '-D{0}={1}'.format(var, val)

def _incdir(path):
    return '-I{0}'.format(path)

def _linelen(linelen):
    return '-l{0}'.format(linelen)

def _indentation(ind):
    return '--indentation={0}'.format(ind)

def _folding(fold):
    return '-f{0}'.format(fold)

def _moddir(path):
    return '-M{0}'.format(path)

def _linenumbering(nummode):
    return '-N{0}'.format(nummode)

def _linenum_gfortran5():
    return '--line-marker-format=gfortran5'

def _linenum_std():
    return '--line-marker-format=std'

def _importmodule(module):
    return '-m{0}'.format(module)


_LINENUM_FLAG = '-n'

_FIXED_FORMAT_FLAG = '--fixed-format'

_NO_FOLDING_FLAG = '-F'

_NEW_FILE = 1

_RETURN_TO_FILE = 2


# Various basic tests
#
# Each test consists of a tuple containing the test name and a tuple with the
# arguments of the get_test_output_method() routine.
#
SIMPLE_TESTS = [
    ('if_true',
     ([_defvar('TESTVAR', 1)],
      '#:if TESTVAR > 0\nTrue\n#:endif\n',
      'True\n'
     )
    ),
    ('if_false',
     ([_defvar('TESTVAR', 0)],
      '#:if TESTVAR > 0\nTrue\n#:endif\n',
      ''
     )
    ),
    ('if_else_true',
     ([_defvar('TESTVAR', 1)],
      '#:if TESTVAR > 0\nTrue\n#:else\nFalse\n#:endif\n',
      'True\n'
     )
    ),
    ('if_else_false',
     ([_defvar('TESTVAR', 0)],
      '#:if TESTVAR > 0\nTrue\n#:else\nFalse\n#:endif\n',
      'False\n'
     )
    ),
    ('if_elif_true1',
     ([_defvar('TESTVAR', 1)],
      '#:if TESTVAR == 1\nTrue1\n#:elif TESTVAR == 2\nTrue2\n#:endif\n',
      'True1\n'
     )
    ),
    ('if_elif_true2',
     ([_defvar('TESTVAR', 2)],
      '#:if TESTVAR == 1\nTrue1\n#:elif TESTVAR == 2\nTrue2\n#:endif\n',
      'True2\n'
     )
    ),
    ('if_elif_false',
     ([_defvar('TESTVAR', 0)],
      '#:if TESTVAR == 1\nTrue1\n#:elif TESTVAR == 2\nTrue2\n#:endif\n',
      ''
     )
    ),
    ('if_elif_else_true1',
     ([_defvar('TESTVAR', 1)],
      '#:if TESTVAR == 1\nTrue1\n#:elif TESTVAR == 2\nTrue2\n'
      '#:else\nFalse\n#:endif\n',
      'True1\n'
     )
    ),
    ('if_elif_else_true2',
     ([_defvar('TESTVAR', 2)],
      '#:if TESTVAR == 1\nTrue1\n#:elif TESTVAR == 2\nTrue2\n'
      '#:else\nFalse\n#:endif\n',
     'True2\n'
     )
    ),
    ('if_elif_else_false',
     ([_defvar('TESTVAR', 0)],
      '#:if TESTVAR == 1\nTrue1\n#:elif TESTVAR == 2\nTrue2\n'
      '#:else\nFalse\n#:endif\n',
     'False\n'
     )
    ),
    ('inline_if_true',
     ([_defvar('TESTVAR', 1)],
      '#{if TESTVAR > 0}#True#{endif}#Done',
      'TrueDone'
     )
    ),
    ('inline_if_false',
     ([_defvar('TESTVAR', 0)],
      '#{if TESTVAR > 0}#True#{endif}#Done',
      'Done'
     )
    ),
    ('inline_if_else_true',
     ([_defvar('TESTVAR', 1)],
      '#{if TESTVAR > 0}#True#{else}#False#{endif}#Done',
      'TrueDone'
     )
    ),
    ('inline_if_else_false',
     ([_defvar('TESTVAR', 0)],
      '#{if TESTVAR > 0}#True#{else}#False#{endif}#Done',
      'FalseDone'
     )
    ),
    ('inline_if_elif_true1',
     ([_defvar('TESTVAR', 1)],
      '#{if TESTVAR == 1}#True1#{elif TESTVAR == 2}#True2#{endif}#Done',
      'True1Done'
     )
    ),
    ('inline_if_elif_true2',
     ([_defvar('TESTVAR', 2)],
      '#{if TESTVAR == 1}#True1#{elif TESTVAR == 2}#True2#{endif}#Done',
      'True2Done'
     )
    ),
    ('inline_if_elif_false',
     ([_defvar('TESTVAR', 0)],
      '#{if TESTVAR == 1}#True1#{elif TESTVAR == 2}#True2#{endif}#Done',
      'Done'
     )
    ),
    ('inline_if_elif_else_true1',
     ([_defvar('TESTVAR', 1)],
      '#{if TESTVAR == 1}#True1#{elif TESTVAR == 2}#True2#{else}#False#{endif}#'
      'Done',
      'True1Done'
     )
    ),
    ('inline_if_elif_else_true2',
     ([_defvar('TESTVAR', 2)],
      '#{if TESTVAR == 1}#True1#{elif TESTVAR == 2}#True2#{else}#False#{endif}#'
      'Done',
      'True2Done'
     )
    ),
    ('inline_if_elif_else_false',
     ([_defvar('TESTVAR', 0)],
      '#{if TESTVAR == 1}#True1#{elif TESTVAR == 2}#True2#{else}#False#{endif}#'
      'Done',
      'FalseDone'
     )
    ),
    ('linesub_eol',
     ([_defvar('TESTVAR', 1)],
      'A\n$: TESTVAR + 1\nB\n',
      'A\n2\nB\n'
     )
    ),
    ('linesub_contlines',
     ([_defvar('TESTVAR', 1)],
      '$: TESTVAR & \n  & + 1\n',
      '2\n'
     )
    ),
    ('linesub_contlines2',
     ([_defvar('TESTVAR', 1)],
      '$: TEST& \n  &VAR & \n  & + 1\n',
      '2\n'
     )
    ),
    ('linesub_contlines_contchar1',
     ([],
      '$: \'hello&\n  world\'\n',
      'hello  world\n'
     )
    ),
    ('linesub_contlines2_contchar1',
     ([],
      '$: \'hello&\n  world&\n  !\'\n',
      'hello  world  !\n'
     )
    ),
    ('exprsub',
     ([_defvar('TESTVAR', 1)],
      'A${TESTVAR}$B${TESTVAR + 1}$C',
      'A1B2C'
     )
    ),
    ('exprsub_ignored_contlines',
     ([_defvar('TESTVAR', 1)],
      'A${TEST&\n  &VAR}$B${TESTVAR + 1}$C',
      'A${TEST&\n  &VAR}$B2C'
     )
    ),
    ('macrosubs',
     ([],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef\n${macro(1)}$',
      'MACRO|1|'
     )
    ),
    ('macrosubs_named_enddef',
     ([],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef macro\n${macro(1)}$',
      'MACRO|1|'
     )
    ),
    ('macrodef_whitespace',
     ([],
      '#:def macro (var)\nMACRO|${var}$|\n#:enddef macro\n${macro(1)}$',
      'MACRO|1|'
     )
    ),
    ('macro_noargs',
     ([],
      '#:def macro()\nMACRO\n#:enddef\n${macro()}$',
      'MACRO'
     )
    ),
    ('recursive_macrosubs',
     ([],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef\n${macro(macro(1))}$',
      'MACRO|MACRO|1||'
     )
    ),
    ('macrosubs_extvarsubs',
     ([_defvar('TESTVAR', 1)],
      '#:def macro(var)\nMACRO|${var}$-${TESTVAR}$|\n#:enddef\n${macro(2)}$',
      'MACRO|2-1|'
     )
    ),
    ('macro_trailing_newlines',
     ([],
      '#:def macro()\nL1\n\n#:enddef\n$: macro()\n',
      'L1\n\n',
     )
    ),
    ('macro_trailing_newlines_inline',
     ([],
      '#:def macro()\nL1\n\n#:enddef\n|${macro()}$|',
      '|L1\n|',
     )
    ),
    ('macro_call_named_arguments',
     ([],
      '#:def mymacro(A, B)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '$:mymacro(B=1, A=2)\n',
      'A=2,B=1\n'
     )
    ),
    ('macro_call_positional_and_named_arguments',
     ([],
      '#:def mymacro(A, B, C)\nA=${A}$,B=${B}$,C=${C}$\n#:enddef mymacro\n'\
      '$:mymacro(1, C=3, B=2)\n',
      'A=1,B=2,C=3\n'
     )
    ),
    ('optarg_macro_call_all_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '#:call mymacro\n1\n#:nextarg\n2\n#:endcall\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_block_all_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '#:block mymacro\n1\n#:contains\n2\n#:endblock\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_call_missing_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '#:call mymacro\n1\n#:endcall\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_block_missing_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '#:block mymacro\n1\n#:endblock\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_eval_call_all_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '$:mymacro(1, 2)\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_eval_call_missing_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '$:mymacro(1)\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_direct_call_all_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '@:mymacro(1, 2)\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_direct_call_all_args_inline',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '@{mymacro(1, 2)}@',
      'A=1,B=2'
      )
    ),
    ('optarg_macro_direct_call_missing_args',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '@:mymacro(1)\n',
      'A=1,B=2\n'
      )
    ),
    ('optarg_macro_direct_call_missing_args_inline',
     ([],
      '#:def mymacro(A, B=2)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '|@{mymacro(1)}@|',
      '|A=1,B=2|'
      )
    ),
    ('optarg_macro_tuple_as_default',
     ([],
      '#:def macro(X, Y=2, Z=(1,2==3))\nX=${X}$,Y=${Y}$,Z=${Z[0]}$,${Z[1]}$\n'\
      '#:enddef\n@:macro(1)\n',
      'X=1,Y=2,Z=1,False\n'
      )
    ),
    ('macro_vararg_no_varargs',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '$:macro(1, 2)\n',
      '|12[]|\n'
     )
    ),
    ('macro_vararg_one_vararg',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '$:macro(1, 2, 3)\n',
      '|12[3]|\n'
     )
    ),
    ('macro_vararg_two_varargs',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '$:macro(1, 2, 3, 4)\n',
      '|12[3, 4]|\n'
     )
    ),
    ('macro_vararg_named_arguments_eval',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '$:macro(y=2, x=1)\n',
      '|12[]|\n'
     )
    ),
    ('macro_vararg_named_arguments_directcall',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '@:macro(y=2, x=1)\n',
      '|12[]|\n'
     )
    ),
    ('macro_vararg_named_arguments_call',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '#:call macro\n#:nextarg y\n2\n#:nextarg x\n1\n#:endcall\n',
      '|12[]|\n'
     )
    ),
    ('macro_vararg_named_arguments_block',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '#:block macro\n#:contains y\n2\n#:contains x\n1\n#:endblock\n',
      '|12[]|\n'
     )
    ),
    ('macro_vararg_named_arguments_inline_call',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '#{call macro}##{nextarg y}#2#{nextarg x}#1#{endcall}#',
      '|12[]|'
     )
    ),
    ('macro_vararg_named_arguments_inline_block',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '#{block macro}##{contains y}#2#{contains x}#1#{endblock}#',
      '|12[]|'
     )
    ),
    ('macro_vararg_mixed_arguments_eval',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '$:macro(1, z=3, y=2)\n',
      '|123[]|\n'
     )
    ),
    ('macro_vararg_mixed_arguments_directcall',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '@:macro(1, z=3, y=2)\n',
      '|123[]|\n'
     )
    ),
    ('macro_vararg_mixed_arguments_call',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#:call macro\n1\n#:nextarg z\n3\n#:nextarg y\n2\n#:endcall\n',
      '|123[]|\n'
     )
    ),
    ('macro_vararg_mixed_arguments_block',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#:block macro\n1\n#:contains z\n3\n#:contains y\n2\n#:endblock\n',
      '|123[]|\n'
     )
    ),
    ('macro_vararg_mixed_arguments_call2',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#:call macro\n#:nextarg\n1\n#:nextarg z\n3\n#:nextarg y\n2\n#:endcall\n',
      '|123[]|\n'
     )
    ),
    ('macro_vararg_mixed_arguments_block2',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#:block macro\n'\
      '#:contains\n1\n'\
      '#:contains z\n3\n'\
      '#:contains y\n'\
      '2\n'\
      '#:endblock\n',
      '|123[]|\n'
     )
    ),
    ('macro_vararg_mixed_arguments_inline_call',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#{call macro}#1#{nextarg z}#3#{nextarg y}#2#{endcall}#',
      '|123[]|'
     )
    ),
    ('macro_vararg_mixed_arguments_inline_block',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#{block macro}#1#{contains z}#3#{contains y}#2#{endblock}#',
      '|123[]|'
     )
    ),
    ('macro_vararg_mixed_arguments_inline_call2',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#{call macro}##{nextarg}#1#{nextarg z}#3#{nextarg y}#2#{endcall}#',
      '|123[]|'
     )
    ),
    ('macro_vararg_mixed_arguments_inline_block2',
     ([],
      '#:def macro(x, y, z, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '#{block macro}##{contains}#1#{contains z}#3#{contains y}#2#{endblock}#',
      '|123[]|'
     )
    ),
    ('macro_varpos_varkw_with_keyword_arguments',
     ([],
      '#:def macro(x, y, *vararg, **varkw)\n'\
      '|${x}$${y}$${varkw["z"]}$${vararg}$|\n'\
      '#:enddef\n'\
      '$:macro(1, 2, z=3)\n',
      '|123[]|\n'
     )
    ),
    ('macro_varpos_varkw_with_pos_arguments',
     ([],
      '#:def macro(x, y, *vararg, **varkw)\n'\
      '|${x}$${y}$${vararg}$|\n'\
      '#:enddef\n'\
      '$:macro(1, 2, 4, 5)\n',
      '|12[4, 5]|\n'
     )
    ),
    ('macro_varpos_varkw_with_pos_and_kw_arguments',
     ([],
      '#:def macro(x, y, *vararg, **varkw)\n'\
      '|${x}$${y}$${varkw["z"]}$${vararg}$|\n'\
      '#:enddef\n'\
      '$:macro(1, 2, 4, 5, z=3)\n',
      '|123[4, 5]|\n'
     )
    ),
    ('for',
     ([],
      '#:for i in (1, 2, 3)\n${i}$\n#:endfor\n',
      '1\n2\n3\n'
     )
    ),
    ('for_macro',
     ([],
      '#:def mymacro(val)\nVAL:${val}$\n#:enddef\n'
      '#:for i in (1, 2, 3)\n$: mymacro(i)\n#:endfor\n',
      'VAL:1\nVAL:2\nVAL:3\n'
     )
    ),
    ('inline_for',
     ([],
      '#{for i in (1, 2, 3)}#${i}$#{endfor}#Done\n',
      '123Done\n'
     )
    ),
    ('inline_for_macro',
     ([],
      '#:def mymacro(val)\nVAL:${val}$\n#:enddef\n'
      '#{for i in (1, 2, 3)}#${mymacro(i)}$#{endfor}#Done\n',
      'VAL:1VAL:2VAL:3Done\n'
     )
    ),
    ('call_directive',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:call mymacro\nL1\nL2\nL3\n#:endcall\n',
      '|L1\nL2\nL3|\n',
     )
    ),
    ('block_directive',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:block mymacro\nL1\nL2\nL3\n#:endblock\n',
      '|L1\nL2\nL3|\n',
     )
    ),
    ('call_directive_named_endcall',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:call mymacro\nL1\nL2\nL3\n#:endcall mymacro\n',
      '|L1\nL2\nL3|\n',
     )
    ),
    ('block_directive_named_endblock',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:block mymacro\nL1\nL2\nL3\n#:endblock mymacro\n',
      '|L1\nL2\nL3|\n',
     )
    ),
    ('inine_call_directive_named_endcall',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#{call mymacro}#L1 L2 L3#{endcall mymacro}#',
      '|L1 L2 L3|',
     )
    ),
    ('inine_block_directive_named_endblock',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#{block mymacro}#L1 L2 L3#{endblock mymacro}#',
      '|L1 L2 L3|',
     )
    ),
    ('call_directive_quotation',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:call mymacro\n"""L1"""\nL2\nL3\n#:endcall\n',
      '|"""L1"""\nL2\nL3|\n',
     )
    ),
    ('block_directive_quotation',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:block mymacro\n"""L1"""\nL2\nL3\n#:endblock\n',
      '|"""L1"""\nL2\nL3|\n',
     )
    ),
    ('call_directive_backslash_escape1',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:call mymacro\nL1\\n\nL2\nL3\n#:endcall\n',
      '|L1\\n\nL2\nL3|\n',
     )
    ),
    ('block_directive_backslash_escape1',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:block mymacro\nL1\\n\nL2\nL3\n#:endblock\n',
      '|L1\\n\nL2\nL3|\n',
     )
    ),
    ('call_directive_backslash_escape2',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:call mymacro\nL1\\"a\\"\\n\nL2\nL3\n#:endcall\n',
      '|L1\\"a\\"\\n\nL2\nL3|\n',
     )
    ),
    ('block_directive_backslash_escape2',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '#:block mymacro\nL1\\"a\\"\\n\nL2\nL3\n#:endblock\n',
      '|L1\\"a\\"\\n\nL2\nL3|\n',
     )
    ),
    ('call_directive_2_args',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '#:call mymacro\n"""L1"""\nL2\n#:nextarg\nL3\n#:endcall\n',
      '|"""L1"""\nL2|L3|\n',
     )
    ),
    ('block_directive_2_args',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '#:block mymacro\n"""L1"""\nL2\n#:contains\nL3\n#:endblock\n',
      '|"""L1"""\nL2|L3|\n',
     )
    ),
    ('call_directive_2_args_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '#{call mymacro}#A1#{nextarg}#A2#{endcall}#',
      '|A1|A2|',
     )
    ),
    ('block_directive_2_args_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '#{block mymacro}#A1#{contains}#A2#{endblock}#',
      '|A1|A2|',
     )
    ),
    ('call_lambda_func',
     ([],
      '#:set convert = lambda s: s.lower()\n'\
      '#:call convert\nHELLO\n#:endcall\n',
      'hello\n',
     )
    ),
    ('call_no_header_arg_no_body_arg',
     ([],
      '#:def macro0()\nNOARG\n#:enddef\n'\
      '#:call macro0()\n#:endcall\n',
      'NOARG\n',
     )
    ),
    ('block_no_header_arg_no_body_arg',
     ([],
      '#:def macro0()\nNOARG\n#:enddef\n'\
      '#:block macro0()\n#:endblock\n',
      'NOARG\n',
     )
    ),
    ('call_header_pos_arg_no_body_arg',
     ([],
      '#:def macro(arg)\n|${arg}$|\n#:enddef\n'\
      '#:call macro("h1")\n#:endcall\n',
      '|h1|\n',
     )
    ),
    ('block_header_pos_arg_no_body_arg',
     ([],
      '#:def macro(arg)\n|${arg}$|\n#:enddef\n'\
      '#:block macro("h1")\n#:endblock\n',
      '|h1|\n',
     )
    ),
    ('call_header_kwarg_no_body_arg',
     ([],
      '#:def macro(arg)\n|${arg}$|\n#:enddef\n'\
      '#:call macro(arg="h1")\n#:endcall\n',
      '|h1|\n',
     )
    ),
    ('block_header_kwarg_no_body_arg',
     ([],
      '#:def macro(arg)\n|${arg}$|\n#:enddef\n'\
      '#:block macro(arg="h1")\n#:endblock\n',
      '|h1|\n',
     )
    ),
    ('call_header_mixed_args_no_body_arg',
     ([],
      '#:def macro(arg, arg2)\n|${arg}$|${arg2}$|\n#:enddef\n'\
      '#:call macro("h1", arg2="h2")\n#:endcall\n',
      '|h1|h2|\n',
     )
    ),
    ('block_header_mixed_args_no_body_arg',
     ([],
      '#:def macro(arg, arg2)\n|${arg}$|${arg2}$|\n#:enddef\n'\
      '#:block macro("h1", arg2="h2")\n#:endblock\n',
      '|h1|h2|\n',
     )
    ),
    ('call_header_mixed_args_body_pos_arg',
     ([],
      '#:def macro(arg, arg2, arg3)\n|${arg}$|${arg2}$|${arg3}$|\n#:enddef\n'\
      '#:call macro("h1", arg3="h3")\nB1\n#:endcall\n',
      '|h1|B1|h3|\n',
     )
    ),
    ('block_header_mixed_args_body_pos_arg',
     ([],
      '#:def macro(arg, arg2, arg3)\n|${arg}$|${arg2}$|${arg3}$|\n#:enddef\n'\
      '#:block macro("h1", arg3="h3")\nB1\n#:endblock\n',
      '|h1|B1|h3|\n',
     )
    ),
    ('call_header_kwargs_body_pos_arg',
     ([],
      '#:def macro(arg, arg2, arg3)\n|${arg}$|${arg2}$|${arg3}$|\n#:enddef\n'\
      '#:call macro(arg3="h3", arg2="h2")\nB1\n#:endcall\n',
      '|B1|h2|h3|\n',
     )
    ),
    ('block_header_kwargs_body_pos_arg',
     ([],
      '#:def macro(arg, arg2, arg3)\n|${arg}$|${arg2}$|${arg3}$|\n#:enddef\n'\
      '#:block macro(arg3="h3", arg2="h2")\nB1\n#:endblock\n',
      '|B1|h2|h3|\n',
     )
    ),
    ('call_header_kwargs_body_kwarg',
     ([],
      '#:def macro(arg1, arg2, arg3)\n|${arg1}$|${arg2}$|${arg3}$|\n#:enddef\n'\
      '#:call macro(arg1="h1", arg3="h3")\n#:nextarg arg2\nB1\n#:endcall\n',
      '|h1|B1|h3|\n',
     )
    ),
    ('block_header_kwargs_body_kwarg',
     ([],
      '#:def macro(arg1, arg2, arg3)\n|${arg1}$|${arg2}$|${arg3}$|\n#:enddef\n'\
      '#:block macro(arg1="h1", arg3="h3")\n#:contains arg2\nB1\n#:endblock\n',
      '|h1|B1|h3|\n',
     )
    ),
    ('direct_call',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro(a < b)\n',
      '|a < b|\n',
     )
    ),
    ('direct_call_whitespace',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro (a < b)\n',
      '|a < b|\n',
     )
    ),
    ('direct_call_inline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@{mymacro(a < b)}@',
      '|a < b|',
     )
    ),
    ('direct_call2',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro(a < b )\n',
      '|a < b|\n',
     )
    ),
    ('direct_call2_inline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@{mymacro(a < b )}@',
      '|a < b|',
     )
    ),
    ('direct_call3',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro( a < b)\n',
      '|a < b|\n',
     )
    ),
    ('direct_call3_inline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@{mymacro( a < b)}@',
      '|a < b|',
     )
    ),
    ('direct_call4',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro(a < b)\n',
      '|a < b|\n',
     )
    ),
    ('direct_call4_inline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@{mymacro(a < b)}@',
      '|a < b|',
     )
    ),
    ('direct_call_contline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro(a &\n    &< b&\n    &)\n',
      '|a < b|\n',
     )
    ),
    ('direct_call_quotation',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro( """L1""" )\n',
      '|"""L1"""|\n',
     )
    ),
    ('direct_call_quotation_inline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@{mymacro( """L1""" )}@',
      '|"""L1"""|',
     )
    ),
    ('direct_call_backslash_escape1',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro(L1\\n)\n',
      '|L1\\n|\n',
     )
    ),
    ('direct_call_backslash_escape1_inline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@{mymacro(L1\\n)}@',
      '|L1\\n|',
     )
    ),
    ('direct_call_backslash_escape2',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro(L1\\"a\\"\\n)\n',
      '|L1\\"a\\"\\n|\n',
     )
    ),
    ('direct_call_backslash_escape2_inline',
     ([],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@{mymacro(L1\\"a\\"\\n)}@',
      '|L1\\"a\\"\\n|',
     )
    ),
    ('direct_call_2_args',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro("""L1""", L2)\n',
      '|"""L1"""|L2|\n',
     )
    ),
    ('direct_call_2_args_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro("""L1""", L2)}@',
      '|"""L1"""|L2|',
     )
    ),
    ('direct_call_2_args_escape1',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro("""L1"""","L2, L3)\n',
      '|"""L1"""","L2|L3|\n',
     )
    ),
    ('direct_call_2_args_escape1_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro("""L1"""","L2, L3)}@',
      '|"""L1"""","L2|L3|',
     )
    ),
    ('direct_call_2_args_escape2',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro((L1, L2), L3)\n',
      '|(L1, L2)|L3|\n',
     )
    ),
    ('direct_call_2_args_escape2_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro((L1, L2), L3)}@',
      '|(L1, L2)|L3|',
     )
    ),
    ('direct_call_2_args_escape3',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro({L1, L2}, L3)\n',
      '|L1, L2|L3|\n',
     )
    ),
    ('direct_call_2_args_escape3_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro({L1, L2}, L3)}@',
      '|L1, L2|L3|',
     )
    ),
    ('direct_call_2_args_escape4',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro([L1, L2], L3)\n',
      '|[L1, L2]|L3|\n',
     )
    ),
    ('direct_call_2_args_escape4_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro([L1, L2], L3)}@',
      '|[L1, L2]|L3|',
     )
    ),
    ('direct_call_2_args_escape5',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro("L1, L2", L3)\n',
      '|"L1, L2"|L3|\n',
     )
    ),
    ('direct_call_2_args_escape5_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro("L1, L2", L3)}@',
      '|"L1, L2"|L3|',
     )
    ),
    ('direct_call_2_args_escape6',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro(\'L1, L2\', L3)\n',
      '|\'L1, L2\'|L3|\n',
     )
    ),
    ('direct_call_2_args_escape6_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro(\'L1, L2\', L3)}@',
      '|\'L1, L2\'|L3|',
     )
    ),
    ('direct_call_2_args_escape7',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro(L1 ${2, 2}$, L3)\n',
      '|L1 (2, 2)|L3|\n',
     )
    ),
    ('direct_call_2_args_escape7_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro(L1 ${2, 2}$, L3)}@',
      '|L1 (2, 2)|L3|',
     )
    ),
    ('direct_call_2_args_escape8',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro({{L1, L2}}, L3)\n',
      '|{L1, L2}|L3|\n',
     )
    ),
    ('direct_call_2_args_escape8_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro({{L1, L2}}, L3)}@',
      '|{L1, L2}|L3|',
     )
    ),
    ('direct_call_kwarg',
     ([],
      '#:def mymacro(a)\n|${a}$|\n#:enddef\n'\
      '@:mymacro(a = b)\n',
      '|b|\n',
     )
    ),
    ('direct_call_kwarg_eq_operator',
     ([],
      '#:def mymacro(a)\n|${a}$|\n#:enddef\n'\
      '@:mymacro(a == b)\n',
      '|a == b|\n',
     )
    ),
    ('direct_call_kwarg_ptr_assignment',
     ([],
      '#:def mymacro(a)\n|${a}$|\n#:enddef\n'\
      '@:mymacro(a => b)\n',
      '|> b|\n',
     )
    ),
    ('direct_call_kwarg_escape',
     ([],
      '#:def mymacro(val1)\n|${val1}$|\n#:enddef\n'\
      '@:mymacro({a = b})\n',
      '|a = b|\n',
     )
    ),
    ('direct_call_varsubs',
     ([],
      '#:def mymacro(val1)\n|${val1}$|\n#:enddef\n'\
      '@:mymacro(2x2=${2*2}$)\n',
      '|2x2=4|\n',
     )
    ),
    ('direct_call_varsubs_inline',
     ([],
      '#:def mymacro(val1)\n|${val1}$|\n#:enddef\n'\
      '@{mymacro(2x2=${2*2}$)}@',
      '|2x2=4|',
     )
    ),
    ('direct_call_varsubs_2_args',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro(${2*1}$, ${2*2}$)\n',
      '|2|4|\n',
     )
    ),
    ('direct_call_varsubs_2_args_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro(${2*1}$, ${2*2}$)}@',
      '|2|4|',
     )
    ),
    ('direct_call_varsubs_2_args_escape',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro((${2*1}$, ${2*2}$), ${2*3}$)\n',
      '|(2, 4)|6|\n',
     )
    ),
    ('direct_call_varsubs_2_args_escape_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro((${2*1}$, ${2*2}$), ${2*3}$)}@',
      '|(2, 4)|6|',
     )
    ),
    ('direct_call_no_param',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '@:mymacro()\n',
      '||\n'
     )
    ),
    ('direct_call_no_param_inline',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '@{mymacro()}@',
      '||'
     )
    ),
    ('direct_call_no_param2',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '@:mymacro( )\n',
      '||\n'
     )
    ),
    ('direct_call_no_param2_inline',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '@{mymacro( )}@',
      '||'
     )
    ),
    ('call_no_param_inline',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '#{call mymacro}##{endcall}#\n',
      '||\n'
     )
    ),
    ('block_no_param_inline',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '#{block mymacro}##{endblock}#\n',
      '||\n'
     )
    ),
    ('call_no_param',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '#:call mymacro\n#:endcall\n',
      '||\n'
     )
    ),
    ('block_no_param',
     ([],
      '#:def mymacro()\n||\n#:enddef mymacro\n'\
      '#:block mymacro\n#:endblock\n',
      '||\n'
     )
    ),
    ('call_empty_param_inline',
     ([],
      '#:def mymacro(txt)\n|${txt}$|\n#:enddef mymacro\n'\
      '#{call mymacro}# #{endcall}#\n',
      '| |\n'
     )
    ),
    ('block_empty_param_inline',
     ([],
      '#:def mymacro(txt)\n|${txt}$|\n#:enddef mymacro\n'\
      '#{block mymacro}# #{endblock}#\n',
      '| |\n'
     )
    ),
    ('call_empty_param',
     ([],
      '#:def mymacro(txt)\n|${txt}$|\n#:enddef mymacro\n'\
      '#:call mymacro\n\n#:endcall\n',
      '||\n'
     )
    ),
    ('block_empty_param',
     ([],
      '#:def mymacro(txt)\n|${txt}$|\n#:enddef mymacro\n'\
      '#:block mymacro\n\n#:endblock\n',
      '||\n'
     )
    ),
    ('call_empty_param_directcall',
     ([],
      '#:def mymacro(txt)\n|${txt}$|\n#:enddef mymacro\n'\
      '@:mymacro({})\n',
      '||\n'
     )
    ),
    ('call_whitespace_param_directcall',
     ([],
      '#:def mymacro(txt)\n|${txt}$|\n#:enddef mymacro\n'\
      '@:mymacro({ })\n',
      '| |\n'
     )
    ),
    ('comment_single',
     ([],
      ' #! Comment here\nDone\n',
      'Done\n',
     )
    ),
    ('comment_multiple',
     ([],
      ' #! Comment1\n#! Comment2\nDone\n',
      'Done\n',
     )
    ),
    ('set',
     ([],
      '#:set x = 2\n$: x\n',
      '2\n',
     )
    ),
    ('set_no_rhs',
     ([],
      '#:set x\n$:x\n',
      '\n',
     )
    ),
    ('set_equal_sign_nospace',
     ([],
      '#:set x=2\n$: x\n',
      '2\n',
     )
    ),
    ('set_equal_sign_withspace',
     ([],
      '#:set x = 2\n$: x\n',
      '2\n',
     )
    ),
    ('inline_set_equal_withspace',
     ([],
      '#{set x = 2}#${x}$Done\n',
      '2Done\n',
     )
    ),
    ('inline_set_equal_nospace',
     ([],
      '#{set x=2}#${x}$Done\n',
      '2Done\n',
     )
    ),
    ('set_function',
     ([],
      '$:setvar("x", 2)\n${x}$\nDone\n',
      "\n2\nDone\n",
     )
    ),
    ('set_function_tuple',
     ([],
      '$:setvar("x, y", (2, 3))\n${x}$${y}$\nDone\n',
      "\n23\nDone\n",
     )
    ),
    ('set_function_tuple2',
     ([],
      '$:setvar("(x, y)", (2, 3))\n${x}$${y}$\nDone\n',
      "\n23\nDone\n",
     )
    ),
    ('set_function_multiple_args',
     ([],
      '$:setvar("x", 2, "y", 3)\n${x}$${y}$\nDone\n',
      "\n23\nDone\n",
     )
    ),
    ('getvar_existing_value',
     ([_defvar('VAR', '\"VAL\"')],
      '$:getvar("VAR", "DEFAULT")\n',
      'VAL\n',
     )
    ),
    ('getvar_default_value',
     ([],
      '$:getvar("VAR", "DEFAULT")\n',
      'DEFAULT\n',
     )
    ),
    ('getvar_local_scope',
     ([],
      '#:set X = 1\n'\
      '#:def test()\n$:getvar("X")\n#:set X = 2\n$:getvar("X")\n#:enddef\n'\
      '$:test()\n',
      '1\n2\n',
      )
    ),
    ('del_existing_variable',
     ([],
      '#:set X = 12\n$:defined("X")\n#:del X\n$:defined("X")\n',
      'True\nFalse\n',
     )
    ),
    ('del_variable_tuple',
     ([],
      '#:set X = 1\n#:set Y = 2\n${defined("X")}$${defined("Y")}$\n'\
      '#:del X, Y\n${defined("X")}$${defined("Y")}$\n',
      'TrueTrue\nFalseFalse\n',
     )
    ),
    ('del_variable_local_scope',
     ([],
      '#:set echo = lambda s: s\n#:set X = 1\n'\
      '#:call echo\n$:X\n#:set X = 2\n$:X\n$:defined("X")\n'\
      '#:del X\n$:defined("X")\n#:endcall\n$:X\n',
      '1\n2\nTrue\nFalse\n1\n',
     )
    ),
    ('del_macro',
     ([],
      '#:def mymacro(txt)\n|${txt}$|\n#:enddef mymacro\n$:defined("mymacro")\n'\
      '$:mymacro("A")\n#:del mymacro\n$:defined("mymacro")\n',
      'True\n|A|\nFalse\n',
     )
    ),
    ('del_inline',
     ([],
      '#:set X = 12\n$:defined("X")\n#{del X}#${defined("X")}$\n',
      'True\nFalse\n',
     )
    ),
    ('del_inline_tuple',
     ([],
      '#:set X = 1\n#:set Y = 2\n${defined("X")}$${defined("Y")}$\n'\
      '#{del X, Y}#${defined("X")}$${defined("Y")}$\n',
      'TrueTrue\nFalseFalse\n',
     )
    ),
    ('delvar_function',
     ([],
      '#:set X = 12\n$:defined("X")\n$:delvar("X")\n$:defined("X")\n',
      'True\n\nFalse\n',
     )
    ),
    ('delvar_function_tuple',
     ([],
      '#:set X = 1\n#:set Y = 2\n${defined("X")}$${defined("Y")}$\n'\
      '$:delvar("X, Y")\n${defined("X")}$${defined("Y")}$\n',
      'TrueTrue\n\nFalseFalse\n',
     )
    ),
    ('delvar_function_multiple_args',
     ([],
      '#:set X = 1\n#:set Y = 2\n${defined("X")}$${defined("Y")}$\n'\
      '$:delvar("X", "Y")\n${defined("X")}$${defined("Y")}$\n',
      'TrueTrue\n\nFalseFalse\n',
     )
    ),
    ('mute',
     ([],
      'A\n#:mute\nB\n#:set VAR = 2\n#:endmute\nVAR=${VAR}$\n',
      'A\nVAR=2\n'
     )
    ),
    ('builtin_var_line',
     ([],
      '${_LINE_}$',
      '1'
     )
    ),
    ('builtin_var_file',
     ([],
      '${_FILE_}$',
      fypp.STRING
     )
    ),
    ('builtin_var_line_in_lineeval',
     ([],
      '$:_LINE_\n',
      '1\n'
     )
    ),
    ('builtin_var_system',
     ([],
      '${_SYSTEM_}$',
      platform.system()
     )
    ),
    ('builtin_var_machine',
     ([],
      '${_MACHINE_}$',
      platform.machine()
     )
    ),
    ('escaped_control_inline',
     ([],
      r'A#\{if False}\#B#\{endif}\#',
      'A#{if False}#B#{endif}#'
     )
    ),
    ('escaped_control_line',
     ([],
      '#\\:if False\n',
      '#:if False\n'
     )
    ),
    ('escaped_eval_inline',
     ([],
      r'A$\{1 + 1}\$',
      'A${1 + 1}$'
     )
    ),
    ('escaped_eval_line',
     ([],
      '$\\: 1 + 1\n',
      '$: 1 + 1\n'
     )
    ),
    ('multi_escape',
     ([],
      r'$\\\{1 + 1}\\$',
      r'$\\{1 + 1}\$'
     )
    ),
    ('escape_direct_call',
     ([],
      '@\\:assertTrue(x > y)\n',
      '@:assertTrue(x > y)\n'
     )
    ),
    ('escape_direct_call_inline',
     ([],
      '@\\{assertTrue(x > y)}@',
      '@{assertTrue(x > y)}@'
     )
    ),
    ('escape_comment',
     ([],
      'A\n  #\! Comment\n',
      'A\n  #! Comment\n',
     )
    ),
    ('fold_lines',
     ([_linelen(10), _indentation(2), _folding('simple')],
      'This line is not folded\nThis line ${1 + 1}$ is folded\n',
      'This line is not folded\nThis line&\n  & 2 is &\n  &folded\n'
     )
    ),
    ('prevent_comment_folding',
     ([_linelen(10), _indentation(2), _folding('simple')],
      '#:def macro()\n ! Should be not folded\nShould be folded\n#:enddef\n'
      '$:macro()\n',
      ' ! Should be not folded\nShould be&\n  & folded\n'
     )
    ),
    ('no_folding',
     ([_linelen(15), _indentation(4), _NO_FOLDING_FLAG],
      '  ${3}$456 89 123456 8',
      '  3456 89 123456 8',
     )
    ),
    ('brute_folding',
     ([_linelen(15), _indentation(4), _folding('brute')],
      '  ${3}$456 89 123456 8',
      '  3456 89 1234&\n    &56 8',
     )
    ),
    ('simple_folding',
     ([_linelen(15), _indentation(4), _folding('simple')],
      '  ${3}$456 89 123456 8',
      '  3456 89 1234&\n      &56 8',
     )
    ),
    ('smart_folding',
     ([_linelen(15), _indentation(4), _folding('smart')],
      '  ${3}$456 89 123456 8',
      '  3456 89&\n      & 123456&\n      & 8',
     )
    ),
    ('fixed_format_folding',
     ([_FIXED_FORMAT_FLAG],
      '      print *, ${\'aa\'}$, bb, cc, dd, ee, ff, gg, hh, ii, jj, kk, ll, '
      'mm, nn, oo, pp, qq, rr, ss, tt\n',
      '      print *, aa, bb, cc, dd, ee, ff, gg, hh, ii, jj, kk, ll, mm, nn, '
      'o\n     &o, pp, qq, rr, ss, tt\n',
     )
    ),
    ('tuple_assignment',
     ([],
      '#:set mytuple = (1, 2, 3)\n#:set a, b, c = mytuple\n${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('tuple_assignment2',
     ([],
      '#:set a, b, c = (1, 2, 3)\n${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('tuple_assignment3',
     ([],
      '#:set a, b, c = 1, 2, 3\n${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('tuple_assignment_nospace',
     ([],
      '#:set a,b,c = (1, 2, 3)\n${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('tuple_assignment_vartuple',
     ([],
      '#:set (a, b, c) = (1, 2, 3)\n${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('tuple_assignment_vartuple2',
     ([],
      '#:set ( a, b, c ) = (1, 2, 3)\n${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('inline_tuple_assignment',
     ([],
      '#{set a, b, c = 1, 2, 3}#${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('inline_tuple_assignment_vartuple',
     ([],
      '#{set (a, b, c) = 1, 2, 3}#${a}$${b}$${c}$\n',
      '123\n'
     )
    ),
   ('whitespace_but_no_param',
     ([],
      '#:if True\nOK\n#:endif \n',
      'OK\n'
     )
    ),
   ('whitespace_but_no_param2',
     ([],
      '#:if True\nOK\n#:endif \n \n',
      'OK\n \n'
     )
    ),
   ('whitespace_but_no_param_inline',
     ([],
      '#{if True}#OK#{endif }#',
      'OK'
     )
    ),
   ('for_loop_scope',
     ([],
      '#{for i in range(4)}##{set X = i}##{endfor}#${X}$${i}$\n',
      '33\n'
     )
    ),
    ('macro_scope',
     ([],
      '#:set X = 3\n#:def setx()\n#:set X = -5\n#:enddef\n$:setx()\n$:X\n',
      '\n3\n'
     )
    ),
    ('local_macro_local_scope',
     ([],
      '#:set echo = lambda s: s\n'\
      '#:set X = 3\n#:call echo\n'\
      '#:def mymacro()\nX:${X}$\n#:enddef\n'\
      '#:set X = 2\n$:mymacro()\n#:endcall\n',
      'X:2\n',
     )
    ),
    ('local_macro_global_scope',
     ([],
      '#:set echo = lambda s: s\n'\
      '#:set X = 3\n#:call echo\n'
      '#:def mymacro()\nX:${X}$\n#:enddef\n'\
      '$:mymacro()\n#:endcall\n',
      'X:3\n',
     )
    ),
    ('scope_global_macro_called_from_local_scope',
     ([],
      '#:set echo = lambda s: s\n'\
      '#:def printX()\nX:${X}$\n#:enddef\n#:set X = 1\n'\
      '#:call echo\n#:set X = 2\n'\
      '#:call echo\n#:set X = 3\n$:printX()\n'\
      '#:endcall\n#:endcall\nX:${X}$\n',
      'X:1\nX:1\n',
     )
    ),
    ('scope_macro_lookup_locals_in_definition_scope',
     ([],
      '#:set X = 0\n'\
      '#:def macro1()\n#:set X = 1\n'\
      '#:def macro2()\n'\
      '#:def macro3a()\nX3a:${X}$\n#:enddef macro3a\n'\
      '#:def macro3b()\n#:set X = 3\n$:macro3a()\n#:enddef macro3b\n'\
      '#:set X = 2\n$:macro3b()\nX2:${X}$\n'\
      '#:enddef macro2\n$:macro2()\nX1:${X}$\n'\
      '#:enddef macro1\n$:macro1()\nX0:${X}$\n',
      'X3a:2\nX2:2\nX1:1\nX0:0\n',
     )
    ),
    ('scope_macro_lookup_locals_above_definition_scope',
     ([],
      '#:set X = 0\n'\
      '#:def macro1()\n#:set X = 1\n'\
      '#:def macro2()\n'\
      '#:def macro3a()\nX3a:${X}$\n#:enddef macro3a\n'\
      '#:def macro3b()\n#:set X = 3\n$:macro3a()\n#:enddef macro3b\n'\
      '$:macro3b()\nX2:${X}$\n'\
      '#:enddef macro2\n$:macro2()\nX1:${X}$\n'\
      '#:enddef macro1\n$:macro1()\nX0:${X}$\n',
      'X3a:1\nX2:1\nX1:1\nX0:0\n',
     )
    ),
    ('scope_macro_lookup_locals_global_scope',
     ([],
      '#:set X = 0\n'\
      '#:def macro1()\n'\
      '#:def macro2()\n'\
      '#:def macro3a()\nX3a:${X}$\n#:enddef macro3a\n'\
      '#:def macro3b()\n#:set X = 3\n$:macro3a()\n#:enddef macro3b\n'\
      '$:macro3b()\nX2:${X}$\n'\
      '#:enddef macro2\n$:macro2()\nX1:${X}$\n'\
      '#:enddef macro1\n$:macro1()\nX0:${X}$\n',
      'X3a:0\nX2:0\nX1:0\nX0:0\n',
     )
    ),
    ('scope_generator_within_macro',
     ([],
      '#:def foo()\n#:set b = 21\n$:sum([b for i in range(2)])\n#:enddef\n'\
      '$:foo()\n',
      '42\n'
     )
    ),
    ('correct_predefined_var_injection',
     ([],
      '#:def ASSERT(cond)\n"${cond}$", ${_FILE_}$, ${_LINE_}$\n#:enddef\n'\
      '@:ASSERT(2 < 3)\n',
      '"2 < 3", ' + fypp.STRING + ', 4\n'
     )
    ),
    ('correct_line_numbering_in_if',
     ([],
      '#:if _LINE_ == 1\nOK\n#:endif\n',
      'OK\n'
     )
    ),
    ('correct_line_numbering_in_for',
     ([],
      '#:for line in [_LINE_]\n${line}$ - ${_LINE_}$\n#:endfor\n',
      '1 - 2\n'
     )
    ),
    ('line_numbering_macro',
     ([],
      '#:def macro()\n${_THIS_LINE_}$,${_LINE_}$\n#:enddef macro\n'\
      '${_THIS_LINE_}$,${_LINE_}$|${macro()}$\n',
      '4,4|2,4\n'
     )
    ),
    ('line_numbering_argeval',
     ([],
      "#:set func = lambda s: str(_THIS_LINE_) + ',' + str(_LINE_) + '|' + s\n"\
      "#:call func\n${_THIS_LINE_}$,${_LINE_}$\n#:endcall\n",
      '2,2|3,3\n'
     )
    ),
    ('line_numbering_argeval_macrocall',
     ([_incdir('include')],
      "#:include 'assert.inc'\n"\
      "#:call ASSERT_CODE\n@:ASSERT()\n#:endcall ASSERT_CODE\n",
      'include/assert.inc:7|<string>:3\n'
     )
    ),
    ('line_numbering_eval_within_macro',
     ([],
      '#:def m1(A)\n${_LINE_}$\n#:enddef\n'\
      '#:def m2(A)\n#:call m1\n${A}$\n#:endcall\n#:enddef\n'\
      '$:m2(1)\n',
      '9\n'
     )
    ),
    ('global_existing',
     ([],
      '#:set A = 1\n#:def macro()\n#:global A\n#:set A = 2\n#:enddef macro\n'\
      '$:macro()\n$:A\n',
      '\n2\n'
     )
    ),
    ('global_non_existing',
     ([],
      '#:def macro()\n#:global A\n#:set A = 2\n#:enddef macro\n'\
      '$:defined("A")\n$:macro()\n$:A\n',
      'False\n\n2\n'
     )
    ),
    ('global_non_existing_evaldir',
     ([],
      '#:def macro()\n$:globalvar("A")\n#:set A = 2\n#:enddef macro\n'\
      '$:defined("A")\n$:macro()\n$:A\n',
      'False\n\n2\n'
     )
    ),
    ('global_non_existing_evaldir_tuple',
     ([],
      '#:def macro()\n$:globalvar("A, B")\n#:set A = 2\n#:set B = 3\n'\
      '#:enddef macro\n'\
      '$:defined("A")\n$:defined("B")\n$:macro()\n$:A\n$:B\n',
      'False\nFalse\n\n2\n3\n'
     )
    ),
    ('global_non_existing_evaldir_arglist',
     ([],
      '#:def macro()\n$:globalvar("A", "B")\n#:set A = 2\n#:set B = 3\n'\
      '#:enddef macro\n'\
      '$:defined("A")\n$:defined("B")\n$:macro()\n$:A\n$:B\n',
      'False\nFalse\n\n2\n3\n'
     )
    ),
    ('global_in_global_scope',
     ([],
      '#:set A = 1\n#:global A\n$:A\n',
      '1\n'
     )
    ),
    ('global_without_assignment',
     ([],
      '#:def macro()\n#:global A\n#:enddef macro\n'\
      '$:defined("A")\n$:macro()\n$:defined("A")\n',
      'False\n\nFalse\n'
     )
    ),
]


# Tests with line enumerations
#
# Each test consists of a tuple containing the test name and a tuple with the
# arguments of the get_test_output_method() routine.
#
LINENUM_TESTS = [
    # Explicit test for line number marker format
    ('explicit_str_linenum_test',
     ([_LINENUM_FLAG],
      '',
      '# 1 "<string>"\n',
     )
    ),
    # Explicit test for line number marker format (GFortran5 compatibility)
    ('explicit_str_linenum_test_gfortran5',
     ([_LINENUM_FLAG, _linenum_gfortran5()],
      '',
      '# 1 "<string>" 1\n',
     )
    ),
    # Explicit test for standard line number marker format
    ('explicit_str_linenum_test_standard',
     ([_LINENUM_FLAG, _linenum_std()],
      '',
      '#line 1 "<string>"\n',
     )
    ),
    ('trivial',
     ([_LINENUM_FLAG],
      'Test\n',
      _linenum(0) + 'Test\n'
     )
    ),
    ('if_true',
     ([_LINENUM_FLAG],
      '#:if 1 < 2\nTrue\n#:endif\nDone\n',
      _linenum(0) + _linenum(1) + 'True\n' + _linenum(3)
      + 'Done\n'
     )
    ),
    ('if_false',
     ([_LINENUM_FLAG],
      '#:if 1 > 2\nTrue\n#:endif\nDone\n',
      _linenum(0) + _linenum(3) + 'Done\n'
     )
    ),
    ('if_else_true',
     ([_LINENUM_FLAG],
      '#:if 1 < 2\nTrue\n#:else\nFalse\n#:endif\nDone\n',
      _linenum(0) + _linenum(1) + 'True\n' + _linenum(5)
      + 'Done\n'
     )
    ),
    ('if_else_false',
     ([_LINENUM_FLAG],
      '#:if 1 > 2\nTrue\n#:else\nFalse\n#:endif\nDone\n',
      _linenum(0) + _linenum(3) + 'False\n' + _linenum(5)
      + 'Done\n'
     )
    ),
    ('if_elif_true1',
     ([_LINENUM_FLAG],
      '#:if 1 == 1\nTrue1\n#:elif 1 == 2\nTrue2\n#:endif\nDone\n',
      _linenum(0) + _linenum(1) + 'True1\n' + _linenum(5)
      + 'Done\n'
     )
    ),
    ('if_elif_true2',
     ([_LINENUM_FLAG],
      '#:if 2 == 1\nTrue1\n#:elif 2 == 2\nTrue2\n#:endif\nDone\n',
      _linenum(0) + _linenum(3) + 'True2\n' + _linenum(5)
      + 'Done\n'
     )
    ),
    ('if_elif_false',
     ([_LINENUM_FLAG],
      '#:if 0 == 1\nTrue1\n#:elif 0 == 2\nTrue2\n#:endif\nDone\n',
      _linenum(0) + _linenum(5) + 'Done\n'
     )
    ),
    ('if_elif_else_true1',
     ([_LINENUM_FLAG],
      '#:if 1 == 1\nTrue1\n#:elif 1 == 2\nTrue2\n'
      '#:else\nFalse\n#:endif\nDone\n',
      _linenum(0) + _linenum(1) + 'True1\n' + _linenum(7)
      + 'Done\n'
     )
    ),
    ('if_elif_else_true2',
     ([_LINENUM_FLAG],
      '#:if 2 == 1\nTrue1\n#:elif 2 == 2\nTrue2\n'
      '#:else\nFalse\n#:endif\nDone\n',
      _linenum(0) + _linenum(3) + 'True2\n' + _linenum(7)
      + 'Done\n'
     )
    ),
    ('if_elif_else_false',
     ([_LINENUM_FLAG],
      '#:if 0 == 1\nTrue1\n#:elif 0 == 2\nTrue2\n'
      '#:else\nFalse\n#:endif\nDone\n',
      _linenum(0) + _linenum(5) + 'False\n' + _linenum(7)
      + 'Done\n'
     )
    ),
    ('inline_if_true',
     ([_LINENUM_FLAG],
      '#{if 1 < 2}#True#{endif}#Done\n',
      _linenum(0) + 'TrueDone\n'
     )
    ),
    ('inline_if_false',
     ([_LINENUM_FLAG],
      '#{if 1 > 2}#True#{endif}#Done\n',
      _linenum(0) + 'Done\n'
     )
    ),
    ('inline_if_else_true',
     ([_LINENUM_FLAG],
      '#{if 1 < 2}#True#{else}#False#{endif}#Done\n',
      _linenum(0) + 'TrueDone\n'
     )
    ),
    ('inline_if_else_false',
     ([_LINENUM_FLAG],
      '#{if 1 > 2}#True#{else}#False#{endif}#Done\n',
      _linenum(0) + 'FalseDone\n'
     )
    ),
    ('inline_if_elif_true1',
     ([_LINENUM_FLAG],
      '#{if 1 == 1}#True1#{elif 1 == 2}#True2#{endif}#Done\n',
      _linenum(0) + 'True1Done\n'
     )
    ),
    ('inline_if_elif_true2',
     ([_LINENUM_FLAG],
      '#{if 2 == 1}#True1#{elif 2 == 2}#True2#{endif}#Done\n',
      _linenum(0) + 'True2Done\n'
     )
    ),
    ('inline_if_elif_false',
     ([_LINENUM_FLAG],
      '#{if 0 == 1}#True1#{elif 0 == 2}#True2#{endif}#Done\n',
      _linenum(0) + 'Done\n'
     )
    ),
    ('inline_if_elif_else_true1',
     ([_LINENUM_FLAG],
      '#{if 1 == 1}#True1#{elif 1 == 2}#True2#{else}#False#{endif}#Done\n',
      _linenum(0) + 'True1Done\n'
     )
    ),
    ('inline_if_elif_else_true2',
     ([_LINENUM_FLAG],
      '#{if 2 == 1}#True1#{elif 2 == 2}#True2#{else}#False#{endif}#Done\n',
      _linenum(0) + 'True2Done\n'
     )
    ),
    ('inline_if_elif_else_false',
     ([_LINENUM_FLAG],
      '#{if 0 == 1}#True1#{elif 0 == 2}#True2#{else}#False#{endif}#Done\n',
      _linenum(0) + 'FalseDone\n'
     )
    ),
    ('linesub_oneline',
     ([_LINENUM_FLAG],
      'A\n$: 1 + 1\nB\n',
      _linenum(0) + 'A\n2\nB\n'
     )
    ),
    ('linesub_contlines',
     ([_LINENUM_FLAG, _defvar('TESTVAR', 1)],
      '$: TESTVAR & \n  & + 1\nDone\n',
      _linenum(0) + '2\n' + _linenum(2) + 'Done\n'
     )
    ),
    ('linesub_contlines2',
     ([_LINENUM_FLAG, _defvar('TESTVAR', 1)],
      '$: TEST& \n  &VAR & \n  & + 1\nDone\n',
      _linenum(0) + '2\n' + _linenum(3) + 'Done\n'
     )
    ),
    ('exprsub_single_line',
     ([_LINENUM_FLAG, _defvar('TESTVAR', 1)],
      'A${TESTVAR}$B${TESTVAR + 1}$C',
      _linenum(0) + 'A1B2C'
     )
    ),
    ('exprsub_multi_line',
     ([_LINENUM_FLAG],
      '${"line1\\nline2"}$\nDone\n',
      _linenum(0) + 'line1\n' + _linenum(0) + 'line2\nDone\n'
     )
    ),
    ('macrosubs',
     ([_LINENUM_FLAG],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef\n${macro(1)}$',
      _linenum(0) + _linenum(3) + 'MACRO|1|'
     )
    ),
    ('recursive_macrosubs',
     ([_LINENUM_FLAG],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef\n${macro(macro(1))}$',
      _linenum(0) + _linenum(3) + 'MACRO|MACRO|1||'
     )
    ),
    ('macrosubs_multiline',
     ([_LINENUM_FLAG],
      '#:def macro(c)\nMACRO1|${c}$|\nMACRO2|${c}$|\n#:enddef\n${macro(\'A\')}$'
      '\n',
      _linenum(0) + _linenum(4) + 'MACRO1|A|\n' + _linenum(4)
      + 'MACRO2|A|\n'
     )
    ),
    ('recursive_macrosubs_multiline',
     ([_LINENUM_FLAG],
      '#:def f(c)\nLINE1|${c}$|\nLINE2|${c}$|\n#:enddef\n$: f(f("A"))\n',
      (_linenum(0) + _linenum(4) + 'LINE1|LINE1|A|\n' +
       _linenum(4) + 'LINE2|A||\n' + _linenum(4) + 'LINE2|LINE1|A|\n' +
       _linenum(4) + 'LINE2|A||\n')
     )
    ),
    ('multiline_macrocall',
     ([_LINENUM_FLAG],
      '#:def macro(c)\nMACRO|${c}$|\n#:enddef\n$: mac& \n  &ro(\'A\')\nDone\n',
      _linenum(0) + _linenum(3) + 'MACRO|A|\n' + _linenum(5)
      + 'Done\n'
     )
    ),
    ('call_directive_2_args',
     ([_LINENUM_FLAG],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '#:call mymacro\nL1\nL2\n#:nextarg\nL3\n#:endcall\n',
      _linenum(0) + _linenum(3) + '|L1\n' + _linenum(3)
      + 'L2|L3|\n' + _linenum(9),
     )
    ),
    ('for',
     ([_LINENUM_FLAG],
      '#:for i in (1, 2)\n${i}$\n#:endfor\nDone\n',
      (_linenum(0) + _linenum(1) + '1\n' + _linenum(1) + '2\n'
       + _linenum(3) + 'Done\n')
     )
    ),
    ('inline_for',
     ([_LINENUM_FLAG],
      '#{for i in (1, 2)}#${i}$#{endfor}#Done\n',
      _linenum(0) + '12Done\n'
     )
    ),
    ('set',
     ([_LINENUM_FLAG],
      '#:set x = 2\n$: x\n',
      _linenum(0) + _linenum(1) + '2\n',
     )
    ),
    ('inline_set',
     ([_LINENUM_FLAG],
      '#{set x = 2}#${x}$Done\n',
      _linenum(0) + '2Done\n',
     )
    ),
    ('comment_single',
     ([_LINENUM_FLAG],
      ' #! Comment here\nDone\n',
      _linenum(0) + _linenum(1) + 'Done\n'
     )
    ),
    ('comment_multiple',
     ([_LINENUM_FLAG],
      ' #! Comment1\n#! Comment2\nDone\n',
      _linenum(0) + _linenum(2) + 'Done\n',
     )
    ),
    ('mute',
     ([_LINENUM_FLAG],
      'A\n#:mute\nB\n#:set VAR = 2\n#:endmute\nVAR=${VAR}$\n',
      _linenum(0) + 'A\n' + _linenum(5) + 'VAR=2\n'
     )
    ),
    ('direct_call',
     ([_LINENUM_FLAG],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro( a < b )\n',
      _linenum(0) + _linenum(3) + '|a < b|\n',
     )
    ),
    ('direct_call_contline',
     ([_LINENUM_FLAG],
      '#:def mymacro(val)\n|${val}$|\n#:enddef\n'\
      '@:mymacro(a &\n    &< b&\n    &)\nDone\n',
      _linenum(0) + _linenum(3) + '|a < b|\n' + _linenum(6)
      + 'Done\n',
     )
    ),
    ('assert_directive',
     ([_LINENUM_FLAG],
      '#:assert 1 < 2\nDone\n',
      _linenum(0) + _linenum(1) + 'Done\n',
     )
    ),
    ('assert_directive_contline',
     ([_LINENUM_FLAG],
      '#:assert 1&\n& < 2\nDone\n',
      _linenum(0) + _linenum(2) + 'Done\n',
     )
    ),
    ('smart_folding',
     ([_LINENUM_FLAG, _linelen(15), _indentation(4), _folding('smart')],
      '  ${3}$456 89 123456 8\nDone\n',
      _linenum(0) + '  3456 89&\n' + _linenum(0)
      + '      & 123456&\n' + _linenum(0) + '      & 8\n' + 'Done\n'
     )
    ),
    ('smart_folding_nocontlines',
     ([_LINENUM_FLAG, _linenumbering('nocontlines'), _linelen(15),
       _indentation(4), _folding('smart')],
      '  ${3}$456 89 123456 8\nDone\n',
      _linenum(0) + '  3456 89&\n' + '      & 123456&\n' \
      + '      & 8\n' + _linenum(1) + 'Done\n'
     )
    ),
]


# Tests with include files
#
# Each test consists of a tuple containing the test name and a tuple with the
# arguments of the get_test_output_method() routine.
#
INCLUDE_TESTS = [
    ('explicit_include',
     ([],
      '#:include "include/fypp1.inc"\n',
      'INCL1\nINCL5\n'
     )
    ),
    ('search_include',
     ([_incdir('include')],
      '#:include "fypp1.inc"\n',
      'INCL1\nINCL5\n'
     )
    ),
    ('nested_include_in_incpath',
     ([_incdir('include')],
      '#:include "subfolder/include_fypp1.inc"\n',
      'INCL1\nINCL5\n'
     )
    ),
    ('nested_include_in_folder_of_incfile',
     ([_incdir('include')],
      '#:include "subfolder/include_fypp2.inc"\n',
      'FYPP2\n'
     )
    ),
    ('search_include_linenum',
     ([_LINENUM_FLAG, _incdir('include')],
      '#:include "fypp1.inc"\n$: incmacro(1)\n',
      (_linenum(0)
       + _linenum(0, 'include/fypp1.inc', flag=_NEW_FILE)
       + 'INCL1\n' + _linenum(4, 'include/fypp1.inc')
       + 'INCL5\n' + _linenum(1, flag=_RETURN_TO_FILE) + 'INCMACRO(1)\n')
     )
    ),
    ('nested_include_in_incpath_linenum',
     ([_LINENUM_FLAG, _incdir('include')],
      '#:include "subfolder/include_fypp1.inc"\n',
      (_linenum(0)
       + _linenum(0, 'include/subfolder/include_fypp1.inc', flag=_NEW_FILE)
       + _linenum(0, 'include/fypp1.inc', flag=_NEW_FILE) + 'INCL1\n'
       + _linenum(4, 'include/fypp1.inc') + 'INCL5\n'
       + _linenum(1, 'include/subfolder/include_fypp1.inc',
                  flag=_RETURN_TO_FILE)
       + _linenum(1, flag=_RETURN_TO_FILE))
     )
    ),
    ('nested_include_in_folder_of_incfile2',
     ([_LINENUM_FLAG, _incdir('include')],
      '#:include "subfolder/include_fypp2.inc"\n',
      (_linenum(0)
       + _linenum(0, 'include/subfolder/include_fypp2.inc', flag=_NEW_FILE)
       + _linenum(0, 'include/subfolder/fypp2.inc', flag=_NEW_FILE)
       + 'FYPP2\n'
       + _linenum(1, 'include/subfolder/include_fypp2.inc',
                  flag=_RETURN_TO_FILE)
       + _linenum(1, flag=_RETURN_TO_FILE))
     )
    ),
    ('muted_include',
     ([_incdir('include')],
      'START\n#:mute\n#:include \'fypp1.inc\'\n#:endmute\nDONE\n',
      'START\nDONE\n'
     )
    ),
    ('muted_include_linenum',
     ([_LINENUM_FLAG, _incdir('include')],
      'START\n#:mute\n#:include \'fypp1.inc\'\n#:endmute\nDONE\n',
      _linenum(0) + 'START\n' + _linenum(4) + 'DONE\n'
     )
    ),
]


# Tests triggering exceptions
#
# Each test consists of a tuple containing the test name and a tuple with the
# arguments of the get_test_exception_method() routine.
#
EXCEPTION_TESTS = [
    #
    # Parser errors
    #
    ('invalid_directive',
     ([],
      '#:invalid\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_macrodef',
     ([],
      '#:def alma[x]\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_for_decl',
     ([],
      '#:for i = 1, 2\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_include',
     ([],
      '#:include <test.h>\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('inline_include',
     ([],
      '#{include "test.h"}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('wrong_include_file',
     ([],
      '#:include "testfkjsdlfkjslf.h"\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_else',
     ([],
      '#:if 1 > 2\nA\n#:else True\nB\n#:endif\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('invalid_endif',
     ([],
      '#:if 1 > 2\nA\n#:else\nB\n#:endif INV\n',
      [(fypp.FyppFatalError, fypp.STRING, (4, 5))]
     )
    ),
    ('invalid_endfor',
     ([],
      '#:for i in range(5)\n${i}$\n#:endfor INV\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('invalid_variable_assign',
     ([],
      '#:set A=\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_mute',
     ([],
      '#:mute TEST\n#:endmute\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_endmute',
     ([],
      '#:mute\n#:endmute INVALID\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('inline_mute',
     ([],
      '#{mute}#test#{endmute}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('inline_endmute',
     ([],
      '#:mute\ntest#{endmute}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 1))]
     )
    ),
    ('setvar_with_equal',
     ([],
      '#:setvar x = 2\n$: x\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('inline_set_without_equal',
     ([],
      '#{set x 2}#${x}$Done\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('missing_del_name',
     ([],
      '#:del\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_del_name',
     ([],
      '#:del [a, b]\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('inline_def',
     ([],
      '#{def macro()}#TEST#{enddef}#',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('invalid_direct_call_expr',
     ([],
      '#:def macro()\n#:enddef\n@:macro{}\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('invalid_direct_call_expr_inline',
     ([],
      '#:def macro()\n#:enddef\n@{macro{}}@\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 2))]
     )
    ),
    ('invalid_direct_call_expr2',
     ([],
      '#:def macro()\n#:enddef\n@:macro(\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('invalid_direct_call_expr2_inline',
     ([],
      '#:def macro()\n#:enddef\n@{macro(}@\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 2))]
     )
    ),
    ('direct_call_non_eval_dir',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@:mymacro(L1 #{if True}#2, 2#{endif}#)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 3))]
     )
    ),
    ('direct_call_non_eval_dir_inline',
     ([],
      '#:def mymacro(val1, val2)\n|${val1}$|${val2}$|\n#:enddef\n'\
      '@{mymacro(L1 #{if True}#2, 2#{endif}#)}@',
      [(fypp.FyppFatalError, fypp.STRING, (3, 3))]
     )
    ),
    ('direct_call_unclosed quote',
     ([],
      '#:def mymacro(arg1)\n|${arg1}$|\n#:enddef\n'\
      '@:mymacro("something)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('direct_call_unclosed bracket',
     ([],
      '#:def mymacro(arg1)\n|${arg1}$|\n#:enddef\n'\
      '@:mymacro({something)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('direct_call_unbalanced bracket',
     ([],
      '#:def mymacro(arg1)\n|${arg1}$|\n#:enddef\n'\
      '@:mymacro({(})\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('missing_line_dir_content',
     ([],
      '#:\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('missing_line_dir_content2',
     ([],
      '#: \n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('missing_inline_dir_content',
     ([],
      '#{}#',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('missing_inline_dir_content2',
     ([],
      '#{ }#',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('set_setvar',
     ([],
      '#:setvar x 2\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('inline_setvar',
     ([],
      '#{setvar x 2}#',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    #
    # Builder errors
    #
    ('line_if_inline_endif',
     ([],
      '#:if 1 < 2\nTrue\n#{endif}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 2))]
     )
    ),
    ('inline_if_line_endif',
     ([],
      '#{if 1 < 2}#True\n#:endif\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('line_if_inline_elif',
     ([],
      '#:if 1 < 2\nTrue\n#{elif 2 > 3}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 2))]
     )
    ),
    ('inline_if_line_elif',
     ([],
      '#{if 1 < 2}#True\n#:elif 2 > 3\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('line_if_inline_else',
     ([],
      '#:if 1 < 2\nTrue\n#{else}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 2))]
     )
    ),
    ('inline_if_line_else',
     ([],
      '#{if 1 < 2}#True\n#:else\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('loose_else',
     ([],
      'A\n#:else\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('loose_inline_else',
     ([],
      'A\n#{else}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 1))]
     )
    ),
    ('loose_elif',
     ([],
      'A\n#:elif 1 > 2\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('loose_inline_elif',
     ([],
      'A\n#{elif 1 > 2}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 1))]
     )
    ),
    ('loose_endif',
     ([],
      'A\n#:endif\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('loose_inline_endif',
     ([],
      'A\n#{endif}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 1))]
     )
    ),
    ('mismatching_else',
     ([],
      '#:if 1 < 2\n#:for i in range(3)\n#:else\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('mismatching_elif',
     ([],
      '#:if 1 < 2\n#:for i in range(3)\n#:elif 1 > 2\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('mismatching_endif',
     ([],
      '#:if 1 < 2\n#:for i in range(3)\n#:endif\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('line_def_inline_enddef',
     ([],
      '#:def alma(x)\n#{enddef}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 1))]
     )
    ),
    ('loose_enddef',
     ([],
      '#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('loose_inline_enddef',
     ([],
      '#{enddef}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('mismatching_enddef',
     ([],
      '#:def test(x)\n#{if 1 < 2}#\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('enddef_name_mismatch',
     ([],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef nonsense\n${macro(1)}$',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('endcall_name_mismatch',
     ([],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef\n'\
      '#:call macro\n1\n#:endcall nonsense\n',
      [(fypp.FyppFatalError, fypp.STRING, (5, 6))]
     )
    ),
    ('inline_endcall_name_mismatch',
     ([],
      '#:def macro(var)\nMACRO|${var}$|\n#:enddef\n'\
      '#{call macro}#1#{endcall nonsense}#',
      [(fypp.FyppFatalError, fypp.STRING, (3, 3))]
     )
    ),
    ('line_for_inline_endfor',
     ([],
      '#:for i in range(3)\nA\n#{endfor}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 2))]
     )
    ),
    ('inline_for_line_endfor',
     ([],
      '#{for i in range(3)}#Empty\n#:endfor\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2))]
     )
    ),
    ('loose_endfor',
     ([],
      '#:endfor\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('loose_inline_endfor',
     ([],
      '#{endfor}#',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('mismatching_endfor',
     ([],
      '#:for i in range(3)\n#{if 1 < 2}#\n#:endfor\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('loose_endmute',
     ([],
      '#:endmute\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('mismatching_endmute',
     ([],
      '#:mute\n#{if 1 < 2}#\n#:endmute\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('unclosed_directive',
     ([],
      '#:if 1 > 2\nA\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('missing_space_after_directive',
     ([],
      '#:if(1 > 2)\nA\n#:endif',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('missing_space_after_inline_directive',
     ([],
      '#{if(1 > 2)}#A#{endif}#',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('mixing_block_and_endcall',
     ([],
      '#:def test(x)\n#:enddef\n#:block test\n1\n#:endcall\n',
      [(fypp.FyppFatalError, fypp.STRING, (4, 5))]
      )
    ),
    ('mixing_call_and_endblock',
     ([],
      '#:def test(x)\n#:enddef\n#:call test\n1\n#:endblock\n',
      [(fypp.FyppFatalError, fypp.STRING, (4, 5))]
      )
    ),
    ('mixing_call_and_contains',
     ([],
      '#:def test(x,y)\n#:enddef\n#:call test\n1\n#:contains\n2\n#:endcall\n',
      [(fypp.FyppFatalError, fypp.STRING, (4, 5))]
      )
    ),
    ('mixing_block_and_nextarg',
     ([],
      '#:def test(x,y)\n#:enddef\n#:block test\n1\n#:nextarg\n2\n#:endblock\n',
      [(fypp.FyppFatalError, fypp.STRING, (4, 5))]
      )
    ),
    #
    # Renderer errors
    #
    ('invalid_expression',
     ([],
      '${i}$',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('invalid_variable',
     ([],
      '#:set i 1.2.3\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_condition',
     ([],
      '#{if i >>> 3}##{endif}#',
      [(fypp.FyppFatalError, fypp.STRING, (0, 0))]
     )
    ),
    ('invalid_iterator',
     ([],
      '#:for i in 1.2.3\nDummy\n#:endfor\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_macro_argument_expression',
     ([],
      '#:def alma(x))\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('tuple_macro_argument',
     ([],
      '#:def alma((x, y))\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))],
     ),
    ),
    ('repeated_keyword_argument',
     ([],
      '#:def mymacro(A, B)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '$:mymacro(A=1, A=2, B=3)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4))]
     )
    ),
    ('pos_arg_after_keyword_arg',
     ([],
      '#:def mymacro(A, B)\nA=${A}$,B=${B}$\n#:enddef mymacro\n'\
      '$:mymacro(B=4, 2)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4))]
     )
    ),
    ('macrodef_pos_arg_after_keyword_arg',
     ([],
      '#:def mymacro(A, B=2, C)\nA=${A}$,B=${B},C=${C}$$\n#:enddef mymacro\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('macrodef_pos_arg_after_var_arg',
     ([],
      '#:def mymacro(A, *B, C)\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     ),
    ),
    ('macrodef_pos_arg_after_var_kwarg',
     ([],
      '#:def mymacro(A, **B, C)\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_macro_prefix',
     ([],
      '#:def __test(x)\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('reserved_macro_name',
     ([],
      '#:def defined(x)\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('macro_double_defined_arg',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${vararg}$|\n#:enddef\n'\
      '$:macro(1, 2, x=1)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('macro_invalid_argument_name',
     ([],
      '#:def macro(x, __y, *vararg)\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('macro_invalid_varargument_name',
     ([],
      '#:def macro(x, y, *__vararg)\n#:enddef\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_variable_prefix',
     ([],
      '#:set __test = 2\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('reserved_variable_name',
     ([],
      '#:set _LINE_ = 2\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('macro_call_more_args',
     ([],
      '#:def test(x)\n${x}$\n#:enddef\n$: test(\'A\', 1)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('macro_call_less_args',
     ([],
      '#:def test(x)\n${x}$\n#:enddef\n$: test()\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('macro_invalid_keyword_arguments',
     ([],
      '#:def macro(x, y)\n|${x}$${y}$|\n#:enddef\n'\
      '$:macro(1, 2, z=3)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('macro_vararg_invalid_keyword_arguments',
     ([],
      '#:def macro(x, y, *vararg)\n|${x}$${y}$${z}$${vararg}$|\n#:enddef\n'\
      '$:macro(1, 2, z=3)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('macro_kwarg_invalid_posarg',
     ([],
      '#:def macro(x, y, **varkw)\n|${x}$${y}$${varkw}$|\n#:enddef\n'\
      '$:macro(1, 2, 3, z=3)\n',
      [(fypp.FyppFatalError, fypp.STRING, (3, 4)),
       (fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('short_line_length',
     ([_linelen(4)],
      '',
      [(fypp.FyppFatalError, None, None)]
     )
    ),
    ('failing_macro_in_include',
     ([],
      '#:include "include/failingmacro.inc"\n$:failingmacro()\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 2)),
       (fypp.FyppFatalError, 'include/failingmacro.inc', (2, 3))]
     )
    ),
    ('incompatible_tuple_assignment1',
     ([],
      '#:set a,b,c = (1, 2)\n${a}$${b}$${c}$\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('incompatible_tuple_assignment2',
     ([],
      '#:set a,b,c = (1, 2, 3, 4)\n${a}$${b}$${c}$\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('invalid_lhs_tuple1',
     ([],
      '#:set (a, b = (1, 2)\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('invalid_lhs_tuple2',
     ([],
      '#:set a, b) = (1, 2)\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('invalid_del_tuple1',
     ([],
      '#:del (a, b\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('invalid_del_tuple2',
     ([],
      '#:del a, b)\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('del_nonexisting_variable',
     ([],
      '#:del X\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('local_macro_visibility',
     ([],
      '#:set echo = lambda s: s\n'\
      '#:call echo\n'
      '#:def mymacro()\nX\n#:enddef\n'\
      '#:endcall\n$:mymacro()\n',
      [(fypp.FyppFatalError, fypp.STRING, (6, 7))]
     )
    ),
    #
    # Command line errors
    #
    ('def_error',
     (['-DVAR=1.2.2'],
      '',
      [(fypp.FyppFatalError, None, None)]
     )
    ),
    ('missing_module',
     (['-mWhateverDummyKJFDKf'],
      '',
      [(fypp.FyppFatalError, None, None)]
     )
    ),
    #
    # User requested stop
    #
    ('userstop',
     ([],
      '#:set A = 12\n#:if A > 10\n#:stop "Wrong A: {0}".format(A)\n#:endif\n',
      [(fypp.FyppStopRequest, fypp.STRING, (2, 3))]
     )
    ),
    ('invalid_userstop_expr',
     ([],
      '#:set A = 12\n#:if A > 10\n#:stop "Wrong A: {0}".format(BA)\n#:endif\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 3))]
     )
    ),
    ('invalid_inline_stop',
     ([],
      '#:set A = 1\n#:if A > 10\n#{stop "Wrong A: {0}".format(BA)}#\n#:endif\n',
      [(fypp.FyppFatalError, fypp.STRING, (2, 2))]
     )
    ),
    ('assert',
     ([],
      '#:set A = 12\n#:assert A < 10\n',
      [(fypp.FyppStopRequest, fypp.STRING, (1, 2))]
     )
    ),
    ('invalid_assert_expr',
     ([],
      '#:assert A < 10\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1))]
     )
    ),
    ('invalid_inline_assert',
     ([],
      '#:set A = 12\n#{assert A < 10}#\n',
      [(fypp.FyppFatalError, fypp.STRING, (1, 1))]
     )
    ),
    ('global_existing_in_local_scope',
     ([],
      '#:def macro()\n#:set A = 12\n#:global A\n#:enddef\n$:macro()\n',
      [(fypp.FyppFatalError, fypp.STRING, (4, 5)),
       (fypp.FyppFatalError, fypp.STRING, (2, 3)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
    ('setvar_func_odd_arguments',
     ([],
      '$:setvar("i", 1, "j")\n',
      [(fypp.FyppFatalError, fypp.STRING, (0, 1)),
       (fypp.FyppFatalError, None, None)]
     )
    ),
]


# Tests with module imports
#
# Each test consists of a tuple containing the test name and a tuple with the
# arguments of the get_test_output_method() routine.
#
# NOTE: imports are global in Python, so all instances of Fypp following after
# the tests below will see the imported modules Therefore, this tests should be
# executed as last to minimize unwanted interactions between unit tests. Also,
# no tests before these should import any modules.
#
IMPORT_TESTS = [
    ('import_module',
     ([_importmodule('math')],
      '$:int(math.sqrt(4))\n',
      '2\n'
     )
    ),
    ('import_module_current_dir',
     ([_importmodule('inimod')],
      '${inimod.get_version()}$',
      '1'
     )
    ),
    ('import_module_modified_lookupdir',
     ([_moddir('include'), _importmodule('inimod2')],
      '${inimod2.get_version()}$',
      '2'
     )
    ),
    ('import_subpackage',
     ([_importmodule('os.path')],
      '${os.path.isabs("a")}$',
      'False'
      )
    ),
]


def _get_test_output_method(args, inp, out):
    '''Returns a test method for checking correctness of Fypp output.

    Args:
        args (list of str): Command-line arguments to pass to Fypp.
        inp (str): Input with Fypp directives.
        out (str): Expected output.

    Returns:
       method: Method to test equality of output with result delivered by Fypp.
    '''

    def test_output(self):
        '''Tests whether Fypp result matches expected output.'''
        optparser = fypp.get_option_parser()
        options, leftover = optparser.parse_args(args)
        self.assertEqual(len(leftover), 0)
        tool = fypp.Fypp(options)
        result = tool.process_text(inp)
        self.assertEqual(out, result)
    return test_output


def _get_test_exception_method(args, inp, exceptions):
    '''Returns a test method for checking correctness of thrown exception.

    Args:
        args (list of str): Command-line arguments to pass to Fypp.
        inp (str): Input with Fypp directives.
        exceptions (list of tuples): Each tuple contains an exception, a file
            name and a span (tuple or int). The tuples should be in reverse
            order (latest raised exception first).

    Returns:
       method: Method to test, whether Fypp throws the correct exception.
    '''

    def test_exception(self):
        '''Tests whether Fypp throws the correct exception.'''
        optparser = fypp.get_option_parser()
        options, leftover = optparser.parse_args(args)
        self.assertEqual(len(leftover), 0)
        try:
            tool = fypp.Fypp(options)
            _ = tool.process_text(inp)
        except Exception as e:
            raised = e
        else:
            self.fail('No exception was raised')
        for exc, fname, span in exceptions:
            self.assertTrue(isinstance(raised, exc))
            if fname is None:
                self.assertTrue(raised.fname is None)
            else:
                self.assertEqual(fname, raised.fname)
            if span is None:
                self.assertTrue(raised.span is None)
            else:
                self.assertEqual(span, raised.span)
            raised = raised.__cause__
        self.assertTrue(not isinstance(raised, fypp.FyppError))

    return test_exception


def _test_needed(flag):
    return True


class _TestContainer(unittest.TestCase):
    '''General test container class.'''

    @classmethod
    def add_test_methods(cls, tests, methodfactory):
        '''Adds tests to a test case.

        Args:
            tests (list of tuples): Tests to attach.
            testcase (TestCase): Class which the tests should be attached to.
            methodfactory (function): Functions which turns the tuples in
                tests into methods, which can be then attached to the test case.
        '''
        already_added = set()
        for itest, test in enumerate(tests):
            name = test[0]
            if name in already_added:
                msg = "multiple occurrence of test name '{0}'".format(name)
                raise ValueError(msg)
            already_added.add(name)
            testargs = test[1]
            methodname = 'test_' + name
            if len(test) < 3:
                addtest = True
            else:
                addtest = _test_needed(test[2])
            if addtest:
                setattr(cls, methodname, methodfactory(*testargs))


class SimpleTest(_TestContainer): pass
SimpleTest.add_test_methods(SIMPLE_TESTS, _get_test_output_method)

class LineNumberingTest(_TestContainer): pass
LineNumberingTest.add_test_methods(LINENUM_TESTS, _get_test_output_method)

class IncludeTest(_TestContainer): pass
IncludeTest.add_test_methods(INCLUDE_TESTS, _get_test_output_method)

class ExceptionTest(_TestContainer): pass
ExceptionTest.add_test_methods(EXCEPTION_TESTS, _get_test_exception_method)

class ImportTest(_TestContainer): pass
ImportTest.add_test_methods(IMPORT_TESTS, _get_test_output_method)


if __name__ == '__main__':
    unittest.main()
