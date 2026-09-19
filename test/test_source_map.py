'''Unit tests for Fypp's --source-map feature.'''
import json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import fypp


def _make_tool(args=None, source_map_file=None):
    opts, _ = fypp.get_option_parser().parse_args(args or [])
    opts.source_map = source_map_file or '__dummy__'
    return fypp.Fypp(opts)


def _get_map(txt, args=None):
    return _make_tool(args).process_text_with_map(txt)


def _kinds(smap): return [m['kind'] for m in smap['mappings']]

_SRC_FIELDS = ('out_byte_start', 'out_byte_end', 'src_byte_start',
               'src_byte_end', 'src_file')


class TestMappingKinds(unittest.TestCase):

    def test_expanded_inline_eval(self):
        output, smap = _get_map("x = ${1 + 2}$\n")
        self.assertIn('3', output)
        self.assertIn('expanded', _kinds(smap))

    def test_expanded_line_eval(self):
        output, smap = _get_map("$:str(42)\n")
        self.assertIn('42', output)
        self.assertIn('expanded', _kinds(smap))

    def test_generated_content(self):
        _, smap = _get_map("line1\n", args=['-n'])
        self.assertIn('generated', _kinds(smap))

    def test_if_true_branch(self):
        output, smap = _get_map("#:if True\nkept\n#:endif\n")
        self.assertIn('kept', output)
        self.assertIn('verbatim', _kinds(smap))

    def test_for_loop(self):
        output, smap = _get_map("#:for i in range(3)\nval${i}$\n#:endfor\n")
        for v in ('val0', 'val1', 'val2'):
            self.assertIn(v, output)
        self.assertTrue(any(k in ('expanded', 'verbatim') for k in _kinds(smap)))

    def test_nested_if(self):
        output, smap = _get_map(
            "#:if True\nouter\n#:if True\ninner\n#:endif\n#:endif\n")
        self.assertIn('outer', output)
        self.assertIn('inner', output)
        self.assertIn('verbatim', _kinds(smap))


class TestIncludes(unittest.TestCase):

    def test_include_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'inc.fypp'), 'w') as f:
                f.write("! included line\n")
            inp = os.path.join(d, 'main.fypp')
            with open(inp, 'w') as f:
                f.write('#:include "inc.fypp"\n')
            smap_path = os.path.join(d, 'out.map')
            tool = _make_tool(args=['-I', d], source_map_file=smap_path)
            output = tool.process_file(inp)
            self.assertIn('included line', output)
            with open(smap_path) as f:
                smap = json.load(f)
            src_files = {m.get('src_file', '') for m in smap['mappings']}
            self.assertTrue(any('inc.fypp' in s for s in src_files))


class TestEdgeCases(unittest.TestCase):

    def test_no_directives(self):
        inp = "program hello\n  print *, 'hi'\nend program hello\n"
        output, smap = _get_map(inp)
        self.assertEqual(output, inp)
        vb = [m for m in smap['mappings'] if m['kind'] == 'verbatim']
        self.assertEqual(len(vb), 1)
        self.assertEqual(vb[0]['out_byte_start'], 0)
        self.assertEqual(vb[0]['out_byte_end'], len(inp.encode('utf-8')))

    def test_multiline_continuation(self):
        output, smap = _get_map("#:if Tr&\n  &ue\nkept\n#:endif\n")
        self.assertIn('kept', output)
        self.assertTrue(len(_kinds(smap)) >= 1)

    def test_verbatim_byte_accuracy(self):
        inp = "before\n#:if True\nmiddle\n#:endif\nafter\n"
        output, smap = _get_map(inp)
        sb, ob = inp.encode('utf-8'), output.encode('utf-8')
        for m in smap['mappings']:
            if m['kind'] == 'verbatim':
                self.assertEqual(sb[m['src_byte_start']:m['src_byte_end']],
                                 ob[m['out_byte_start']:m['out_byte_end']])
    
    def test_verbatim_literal_continuation_markers(self):
        inp = "a&\n&b\n"
        output, smap = _get_map(inp)
        self.assertEqual(output, inp)
        ob = output.encode('utf-8')
        vb = [m for m in smap['mappings'] if m['kind'] == 'verbatim']
        self.assertEqual(len(vb), 1)
        self.assertEqual(vb[0]['out_byte_start'], 0)
        self.assertEqual(vb[0]['out_byte_end'], len(ob))
        self.assertEqual(inp.encode('utf-8')[vb[0]['src_byte_start']:vb[0]['src_byte_end']],
                         ob[vb[0]['out_byte_start']:vb[0]['out_byte_end']])

    def test_expanded_literal_continuation_markers_inline(self):
        output, smap = _get_map("${'a&\\n&b'}$\n")
        ob = output.encode('utf-8')
        self.assertEqual(output, "a&\n&b\n")
        es = sorted(smap['mappings'], key=lambda e: e['out_byte_start'])
        self.assertEqual(es[0]['out_byte_start'], 0)
        self.assertEqual(es[-1]['out_byte_end'], len(ob))
        for m in es:
            self.assertLessEqual(m['out_byte_start'], m['out_byte_end'])
            self.assertLessEqual(m['out_byte_end'], len(ob))
        self.assertIn('expanded', _kinds(smap))

    def test_expanded_literal_continuation_markers_set_var(self):
        output, smap = _get_map("#:set x='a&\\n&b'\n${x}$\n")
        ob = output.encode('utf-8')
        self.assertEqual(output, "a&\n&b\n")
        es = sorted(smap['mappings'], key=lambda e: e['out_byte_start'])
        self.assertEqual(es[0]['out_byte_start'], 0)
        self.assertEqual(es[-1]['out_byte_end'], len(ob))
        for m in es:
            self.assertLessEqual(m['out_byte_start'], m['out_byte_end'])
            self.assertLessEqual(m['out_byte_end'], len(ob))
        self.assertIn('expanded', _kinds(smap))

    def test_folding_splits_verbatim_into_precise_pieces(self):
        inp = "abcdefghij${1}$\n"
        output, smap = _get_map(inp, args=['-l', '8'])
        sb, ob = inp.encode('utf-8'), output.encode('utf-8')
        self.assertIn('generated', _kinds(smap))
        for m in smap['mappings']:
            if m['kind'] == 'verbatim':
                self.assertEqual(
                    sb[m['src_byte_start']:m['src_byte_end']],
                    ob[m['out_byte_start']:m['out_byte_end']])

    def test_folding_with_linenums_keeps_verbatim_byte_accuracy(self):
        inp = "abc ${1}$ def\n"
        output, smap = _get_map(inp, args=['-l', '8', '-n'])
        sb, ob = inp.encode('utf-8'), output.encode('utf-8')
        self.assertIn('generated', _kinds(smap))
        for m in smap['mappings']:
            if m['kind'] == 'verbatim':
                self.assertEqual(
                    sb[m['src_byte_start']:m['src_byte_end']],
                    ob[m['out_byte_start']:m['out_byte_end']])

    def test_folding_with_linenums_loop_keeps_verbatim_byte_accuracy(self):
        inp = "#:for i in range(2)\naaaaaaaa ${i}$ bbbbbbbb\n#:endfor\n"
        output, smap = _get_map(inp, args=['-l', '8', '-n'])
        sb, ob = inp.encode('utf-8'), output.encode('utf-8')
        self.assertIn('generated', _kinds(smap))
        verb = [m for m in smap['mappings'] if m['kind'] == 'verbatim']
        self.assertTrue(len(verb) > 0)
        for m in verb:
            if m['kind'] == 'verbatim':
                self.assertEqual(
                    sb[m['src_byte_start']:m['src_byte_end']],
                    ob[m['out_byte_start']:m['out_byte_end']])

    def test_muted_with_line_numbering(self):
        output, smap = _get_map(
            "#:mute\nhidden\n#:endmute\nvisible\n", args=['-n'])
        self.assertNotIn('hidden', output)
        self.assertIn('visible', output)
        n = len(output.encode('utf-8'))
        es = sorted(smap['mappings'], key=lambda e: e['out_byte_start'])
        self.assertTrue(len(es) >= 1)
        self.assertEqual(es[0]['out_byte_start'], 0)
        self.assertEqual(es[-1]['out_byte_end'], n)
        for i in range(len(es) - 1):
            self.assertEqual(es[i]['out_byte_end'], es[i+1]['out_byte_start'])

    def test_unicode_byte_accuracy(self):
        inp = "! café résumé\n"
        output, smap = _get_map(inp)
        self.assertEqual(output, inp)
        vb = [m for m in smap['mappings'] if m['kind'] == 'verbatim']
        self.assertEqual(len(vb), 1)
        self.assertEqual(vb[0]['out_byte_end'], len(inp.encode('utf-8')))
        self.assertEqual(vb[0]['src_byte_end'], len(inp.encode('utf-8')))

    def test_macro_call_mapping(self):
        inp = "#:def greet(name)\nHello ${name}$!\n#:enddef\n$:greet('World')\n"
        output, smap = _get_map(inp)
        self.assertIn('Hello World!', output)
        self.assertIn('expanded', _kinds(smap))

    def test_escape_sequences_stay_verbatim(self):
        for inp in ["cost = $\\{100\\}\n",
                     "! comment #\\: not a directive\n"]:
            with self.subTest(inp=inp):
                output, smap = _get_map(inp)
                verb = [m for m in smap['mappings'] if m['kind'] == 'verbatim']
                self.assertTrue(len(verb) > 0,
                    "escaped text should remain verbatim, not degrade to generated")

    def test_hash_in_verbatim_with_folding(self):
        inp = "aaa#bbb ${1}$\n"
        output, smap = _get_map(inp, args=['-l', '8'])
        verb = [m for m in smap['mappings'] if m['kind'] == 'verbatim']
        self.assertTrue(len(verb) > 0,
            "verbatim text containing '#' should not be consumed as insertion")


class TestAPI(unittest.TestCase):

    def test_process_text_returns_str(self):
        self.assertIsInstance(_make_tool().process_text("hello\n"), str)

    def test_process_text_with_map_returns_tuple(self):
        result = _make_tool().process_text_with_map("hello\n")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], dict)

    def test_process_text_with_map_no_sourcemap(self):
        opts, _ = fypp.get_option_parser().parse_args([])
        opts.source_map = None
        output, smap = fypp.Fypp(opts).process_text_with_map("hello\n")
        self.assertIsInstance(output, str)
        self.assertIsNone(smap)

    def test_cli_source_map_writes_file(self):
        with tempfile.TemporaryDirectory() as d:
            inp = os.path.join(d, 'input.fypp')
            smap_path = os.path.join(d, 'output.map')
            with open(inp, 'w') as f:
                f.write("program test\nend program test\n")
            _make_tool(source_map_file=smap_path).process_file(
                inp, os.path.join(d, 'output.f90'))
            with open(smap_path) as f:
                smap = json.load(f)
            self.assertIn('version', smap)
            self.assertIn('mappings', smap)


class TestJSONFormat(unittest.TestCase):

    def test_source_map_version(self):
        _, smap = _get_map("hello\n")
        self.assertEqual(smap['version'], 1)
        self.assertIn('source_file', smap)

    def test_mapping_fields_verbatim(self):
        _, smap = _get_map("hello\n")
        for m in smap['mappings']:
            self.assertIn('kind', m)
            if m['kind'] == 'verbatim':
                for f in _SRC_FIELDS:
                    self.assertIn(f, m)

    def test_mapping_fields_expanded(self):
        _, smap = _get_map("${1 + 1}$\n")
        expanded = [m for m in smap['mappings'] if m['kind'] == 'expanded']
        self.assertTrue(len(expanded) >= 1)
        for m in expanded:
            for f in _SRC_FIELDS:
                self.assertIn(f, m)

    def test_muted_produces_no_mappings(self):
        _, smap = _get_map("#:if False\ngone\n#:endif\n")
        self.assertEqual(smap['mappings'], [])

    def test_generated_fields(self):
        _, smap = _get_map("hello\n", args=['-n'])
        gen = [m for m in smap['mappings'] if m['kind'] == 'generated']
        self.assertTrue(len(gen) >= 1)
        for m in gen:
            self.assertIn('out_byte_start', m)
            self.assertIn('out_byte_end', m)

    def test_no_overlapping_output_ranges(self):
        _, smap = _get_map("before\n#:if True\nkept\n#:endif\nafter\n")
        es = sorted(smap['mappings'], key=lambda e: e['out_byte_start'])
        for i in range(len(es) - 1):
            self.assertLessEqual(es[i]['out_byte_end'], es[i+1]['out_byte_start'])

    def test_continuous_coverage(self):
        for inp, args in [("alpha\nbeta\n", []),
                          ("before\n$:str(99)\nafter\n", []),
                          ("line1\nline2\n", ['-n']),
                          ("#:mute\nx\n#:endmute\nafter\n", ['-n']),
                          ("A${str(7)}$X&YaZXa& &a  \nbY Y${2}$\n",
                           ['-l', '8']),
                          ("AAAAAAAAAA${1}$Z\n", ['-l', '8', '-n'])]:
            with self.subTest(inp=inp, args=args):
                output, smap = _get_map(inp, args=args)
                n = len(output.encode('utf-8'))
                if not n: continue
                es = sorted(smap['mappings'], key=lambda e: e['out_byte_start'])
                self.assertTrue(len(es) >= 1)
                self.assertEqual(es[0]['out_byte_start'], 0)
                self.assertEqual(es[-1]['out_byte_end'], n)
                for i in range(len(es) - 1):
                    self.assertEqual(es[i]['out_byte_end'], es[i+1]['out_byte_start'])


def _assert_valid_map(tc, output, smap, inp=None):
    '''No crash, continuous coverage, no zero-width, verbatim byte accuracy.'''
    ob = output.encode('utf-8')
    n = len(ob)
    es = sorted(smap['mappings'], key=lambda e: e['out_byte_start'])
    for i, e in enumerate(es):
        tc.assertGreater(e['out_byte_end'], e['out_byte_start'],
                         f"zero-width entry #{i}: {e}")
    if n == 0:
        tc.assertEqual(es, [])
        return
    tc.assertTrue(len(es) >= 1)
    tc.assertEqual(es[0]['out_byte_start'], 0)
    tc.assertEqual(es[-1]['out_byte_end'], n)
    for i in range(len(es) - 1):
        tc.assertEqual(es[i]['out_byte_end'], es[i + 1]['out_byte_start'],
                       f"gap/overlap between {i} and {i+1}")
    if inp is not None:
        sb = inp.encode('utf-8')
        for e in es:
            if e['kind'] == 'verbatim':
                tc.assertEqual(
                    sb[e['src_byte_start']:e['src_byte_end']],
                    ob[e['out_byte_start']:e['out_byte_end']])


class TestStressEdgeCases(unittest.TestCase):

    def test_empty_lines_between_directives(self):
        inp = "#:if True\n\n\nkept\n\n#:endif\n"
        output, smap = _get_map(inp)
        self.assertIn('kept', output)
        _assert_valid_map(self, output, smap, inp)

    def test_empty_lines_with_linenums(self):
        inp = "#:if True\n\n\nkept\n\n#:endif\n"
        output, smap = _get_map(inp, args=['-n'])
        _assert_valid_map(self, output, smap, inp)

    def test_backslash_in_verbatim(self):
        inp = "path = C:\\users\n"
        output, smap = _get_map(inp)
        self.assertEqual(output, inp)
        _assert_valid_map(self, output, smap, inp)

    def test_backslash_with_folding(self):
        inp = "path = C:\\users\\longdirname\n"
        output, smap = _get_map(inp, args=['-l', '15'])
        _assert_valid_map(self, output, smap, inp)

    def test_eval_producing_line_directive_pattern(self):
        inp = '${\"# 1 \\\"fake.f90\\\"\"}$\n'
        output, smap = _get_map(inp, args=['-n'])
        self.assertIn('fake.f90', output)
        _assert_valid_map(self, output, smap)

    def test_fold_7_eval(self):
        inp = "ab${1}$cd\n"
        output, smap = _get_map(inp, args=['-l', '7'])
        _assert_valid_map(self, output, smap, inp)

    def test_fold_7_with_linenums(self):
        inp = "ab${1}$cd\n"
        output, smap = _get_map(inp, args=['-l', '7', '-n'])
        _assert_valid_map(self, output, smap, inp)

    def test_fold_7_indent_0(self):
        inp = "ABCDEFGHIJ${99}$XYZ\n"
        output, smap = _get_map(inp, args=['-l', '7', '--indentation', '0'])
        _assert_valid_map(self, output, smap, inp)

    def test_tab_with_eval_and_fold(self):
        inp = "\tab${1}$cdefgh\n"
        output, smap = _get_map(inp, args=['-l', '10'])
        _assert_valid_map(self, output, smap, inp)

    def test_none_eval_then_verbatim(self):
        inp = "${None}$hello\n"
        output, smap = _get_map(inp)
        self.assertIn('hello', output)
        _assert_valid_map(self, output, smap)

    def test_empty_eval_between_verbatim(self):
        inp = "before${None}$after\n"
        output, smap = _get_map(inp)
        self.assertIn('beforeafter', output)
        _assert_valid_map(self, output, smap)

    def test_mute_between_visible_linenums(self):
        inp = "before\n#:mute\nhidden\n#:endmute\nafter\n"
        output, smap = _get_map(inp, args=['-n'])
        self.assertNotIn('hidden', output)
        _assert_valid_map(self, output, smap, inp)

    def test_multiple_mute_blocks(self):
        inp = "#:mute\na\n#:endmute\nvis1\n#:mute\nb\n#:endmute\nvis2\n"
        output, smap = _get_map(inp, args=['-n'])
        self.assertIn('vis1', output)
        _assert_valid_map(self, output, smap, inp)

    def test_call_endcall_basic(self):
        inp = ("#:def wrap(body)\nBEGIN\n${body}$\nEND\n#:enddef\n"
               "#:call wrap\nhello\n#:endcall\n")
        output, smap = _get_map(inp)
        self.assertIn('BEGIN', output)
        self.assertIn('hello', output)
        _assert_valid_map(self, output, smap)

    def test_call_endcall_with_linenums(self):
        inp = ("#:def wrap(body)\nBEGIN\n${body}$\nEND\n#:enddef\n"
               "#:call wrap\nhello\n#:endcall\n")
        output, smap = _get_map(inp, args=['-n'])
        _assert_valid_map(self, output, smap)

    def test_fold_empty_eval_verbatim_gap(self):
        '''Fold insertion between verbatim pieces must not cause a gap.'''
        inp = ("#:for i in range(2)\n"
               "path\\dir ${i}$ ${None}$ end\n"
               "#:endfor\n")
        output, smap = _get_map(inp, args=['-l', '12'])
        self.assertIn('path', output)
        _assert_valid_map(self, output, smap)

    def test_include_chain(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'C.fypp'), 'w') as f:
                f.write("! from C\n")
            with open(os.path.join(d, 'B.fypp'), 'w') as f:
                f.write("! from B\n#:include 'C.fypp'\n")
            inp = os.path.join(d, 'A.fypp')
            with open(inp, 'w') as f:
                f.write("! from A\n#:include 'B.fypp'\n! back in A\n")
            smap_path = os.path.join(d, 'out.map')
            tool = _make_tool(args=['-I', d], source_map_file=smap_path)
            output = tool.process_file(inp)
            self.assertIn('from C', output)
            with open(smap_path) as f:
                smap = json.load(f)
            files = {e.get('src_file', '') for e in smap['mappings']}
            self.assertTrue(any('C.fypp' in s for s in files))
            ob = output.encode('utf-8')
            es = sorted(smap['mappings'], key=lambda e: e['out_byte_start'])
            self.assertEqual(es[0]['out_byte_start'], 0)
            self.assertEqual(es[-1]['out_byte_end'], len(ob))
            for i in range(len(es) - 1):
                self.assertEqual(es[i]['out_byte_end'],
                                 es[i + 1]['out_byte_start'])

    def test_crlf_verbatim(self):
        inp = "hello\r\nworld\r\n"
        output, smap = _get_map(inp)
        _assert_valid_map(self, output, smap, inp)


if __name__ == '__main__':
    unittest.main()
