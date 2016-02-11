import unittest
import fypp

simple_tests = [
    ('if_true', [ '-DTESTVAR=1' ],
     '#if TESTVAR > 0\nTrueBranch\n#endif\n',
     'TrueBranch\n'
     ),
    #
    ('if_false', [ '-DTESTVAR=0' ],
     '#if TESTVAR > 0\nTrueBranch\n#endif\n',
     ''
     ),
    #
    ('if_else_true', [ '-DTESTVAR=1' ],
     '#if TESTVAR > 0\nTrueBranch\n#else\nFalseBranch\n#endif\n',
     'TrueBranch\n'
     ),
    #
    ('if_else_false', [ '-DTESTVAR=0' ],
     '#if TESTVAR > 0\nTrueBranch\n#else\nFalseBranch\n#endif\n',
     'FalseBranch\n'
     ),
    #
    ('if_elif_true1', [ '-DTESTVAR=1' ],
     '#if TESTVAR == 1\nTrueBranch1\n#elif TESTVAR == 2\nTrueBranch2\n#endif\n',
     'TrueBranch1\n'
     ),
    #
    ('if_elif_true2', [ '-DTESTVAR=2' ],
     '#if TESTVAR == 1\nTrueBranch1\n#elif TESTVAR == 2\nTrueBranch2\n#endif\n',
     'TrueBranch2\n'
     ),
    #
    ('if_elif_false', [ '-DTESTVAR=0' ],
     '#if TESTVAR == 1\nTrueBranch1\n#elif TESTVAR == 2\nTrueBranch2\n#endif\n',
     ''
     ),
    #
    ('if_elif_else_true1', [ '-DTESTVAR=1' ],
     '#if TESTVAR == 1\nTrueBranch1\n#elif TESTVAR == 2\nTrueBranch2\n'
     '#else\nFalseBranch\n#endif\n',
     'TrueBranch1\n'
     ),
    #
    ('if_elif_else_true2', [ '-DTESTVAR=2' ],
     '#if TESTVAR == 1\nTrueBranch1\n#elif TESTVAR == 2\nTrueBranch2\n'
     '#else\nFalseBranch\n#endif\n',
     'TrueBranch2\n'
     ),
    #
    ('if_elif_else_false', [ '-DTESTVAR=0' ],
     '#if TESTVAR == 1\nTrueBranch1\n#elif TESTVAR == 2\nTrueBranch2\n'
     '#else\nFalseBranch\n#endif\n',
     'FalseBranch\n'
     ),
    #
    ('exprsub', [ '-DTESTVAR=0' ],
     '|${ TESTVAR }$ x ${ 2 - 3 }$|',
     '|0 x -1|'
     ),
    #
    ('linesub_no_eol', [ '-DTESTVAR=1' ],
     '$ TESTVAR + 1',
     '2'
     ),
    #
    ('linesub_eol', [ '-DTESTVAR=1' ],
     'A\n$ TESTVAR + 1\nB\n',
     'A\n2\nB\n'
     ),
    #
    ('linesub_contlines', [ '-DTESTVAR=1' ],
     '$ TESTVAR & \n  & + 1',
     '2'
     ),
    #
    ('linesub_contlines2', [ '-DTESTVAR=1' ],
     '$ TEST& \n  &VAR & \n  & + 1',
     '2'
     ),
    #
    ('exprsub', [ '-DTESTVAR=1' ],
     'A${TESTVAR}$B${TESTVAR + 1}$C',
     'A1B2C'
     ),
    #
    ('exprsub_ignored_contlines', [ '-DTESTVAR=1' ],
     'A${TEST&\n  &VAR}$B${TESTVAR + 1}$C',
     'A${TEST&\n  &VAR}$B2C'
     ),
    #
    ('macrosubs', [],
     '#def macro(var)\nMACRO|${var}$|\n#enddef\n${macro(1)}$',
     'MACRO|1|'
     ),
    #
    ('recursive_macrosubs', [],
     '#def macro(var)\nMACRO|${var}$|\n#enddef\n${macro(macro(1))}$',
     'MACRO|MACRO|1||'
     ),
    #
    ('macrosubs_extvarsubs', [ '-DTESTVAR=1' ],
     '#def macro(var)\nMACRO|${var}$-${TESTVAR}$|\n#enddef\n${macro(2)}$',
     'MACRO|2-1|'
     ),
    #
    ('macrosubs_extvar_override', [ '-DTESTVAR=1' ],
     '#def macro(var)\nMACRO|${var}$-${TESTVAR}$|\n#enddef\n'
     '${macro(2, TESTVAR=4)}$',
     'MACRO|2-4|'
     ),
    #
    ('for', [],
     '#for i in (1, 2, 3)\n${i}$\n#endfor\n',
     '1\n2\n3\n'
     ),
    #
    ('for_macro', [],
     '#def mymacro(val)\nVAL:${val}$\n#enddef\n'
     '#for i in (1, 2, 3)\n$ mymacro(i)\n#endfor\n',
     'VAL:1\nVAL:2\nVAL:3\n'
     ),
]


class SimpleTests(unittest.TestCase):
    pass


def create_test_method(args, inp, out):
    def testmethod(self):
        tool = fypp.FyppCmdLineTool(args)
        result = tool.process_text(inp)
        self.assertEqual(result, out)
    return testmethod


def add_test_methods(tests, testclass):
    for ii, test in enumerate(tests):
        name, args, inp, out = test
        methodname = 'test{}_{}'.format(ii + 1, name)
        setattr(testclass, methodname, create_test_method(args, inp, out))


add_test_methods(simple_tests, SimpleTests)


if __name__ == '__main__':
    unittest.main()
