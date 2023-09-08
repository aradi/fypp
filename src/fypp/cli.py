import argparse
import sys
from .fypp import FyppDefaults, Fypp, FyppStopRequest, FyppFatalError, _formatted_exception, USER_ERROR_EXIT_CODE, \
    ERROR_EXIT_CODE
from ._version import __version__


def get_option_parser() -> argparse.ArgumentParser:
    """
    Returns an option parser for the Fypp command line tool.

    :return: Parser which can create an optparse.Values object with
            Fypp settings based on command line arguments.
    """
    defs = FyppDefaults()
    parser = argparse.ArgumentParser(
        prog="fypp",
        description="""
        Preprocesses source code with Fypp directives. The input is
        read from INFILE (default: \'-\', stdin) and written to
        OUTFILE (default: \'-\', stdout).
        """)
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('-D', '--define', action='append', dest='defines',
                        metavar='VAR[=VALUE]', default=defs.defines,
                        help="""
                        define variable, value is interpreted as
                        Python expression (e.g \'-DDEBUG=1\' sets DEBUG to the
                        integer 1) or set to None if omitted
                        """)

    parser.add_argument('-I', '--include', action='append', dest='includes',
                        metavar='INCDIR', default=defs.includes,
                        help="""
                        add directory to the search paths for include files
                        """)
    parser.add_argument('-m', '--module', action='append', dest='modules',
                        metavar='MOD', default=defs.modules,
                        help="""
                        import a python module at startup (import only trustworthy modules
                        as they have access to an **unrestricted** Python environment!)
                        """)

    parser.add_argument('-M', '--module-dir', action='append',
                        dest='moduledirs', metavar='MODDIR',
                        default=defs.moduledirs,
                        help="""
                        directory to be searched for user imported modules before
                        looking up standard locations in sys.path
                        """)

    parser.add_argument('-n', '--line-numbering', action='store_true',
                        dest='line_numbering', default=defs.line_numbering,
                        help="""
                        emit line numbering markers
                        """)
    parser.add_argument('-N', '--line-numbering-mode', metavar='MODE',
                        choices=['full', 'nocontlines'],
                        default=defs.line_numbering_mode,
                        dest='line_numbering_mode',
                        help="""
                        line numbering mode, 'full' (default): line numbering
                        markers generated whenever source and output lines are out
                        of sync, 'nocontlines': line numbering markers omitted
                        for continuation lines
                        """)
    parser.add_argument('--line-marker-format', metavar='FMT',
                        choices=['cpp', 'gfortran5', 'std'],
                        dest='line_marker_format',
                        default=defs.line_marker_format,
                        help="""
                        line numbering marker format,  currently 'std', 'cpp' and
                        'gfortran5' are supported, where 'std' emits #line pragmas
                        similar to standard tools, 'cpp' produces line directives as
                        emitted by GNU cpp, and 'gfortran5' cpp line directives with a
                        workaround for a bug introduced in GFortran 5. Default: 'cpp'.
                        """)
    parser.add_argument('-l', '--line-length', type=int, metavar='LEN',
                        dest='line_length', default=defs.line_length,
                        help="""
                        maximal line length (default: 132), lines modified by the
                        preprocessor are folded if becoming longer
                        """)
    parser.add_argument('-f', '--folding-mode', metavar='MODE',
                        choices=['smart', 'simple', 'brute'], dest='folding_mode',
                        default=defs.folding_mode,
                        help="""
                        line folding mode, 'smart' (default): indentation context
                        and whitespace aware, 'simple': indentation context aware,
                        'brute': mechnical folding
                        """)

    parser.add_argument('-F', '--no-folding', action='store_true',
                        dest='no_folding', default=defs.no_folding,
                        help="""
                        suppress line folding
                        """)
    parser.add_argument('--indentation', type=int, metavar='IND',
                        dest='indentation', default=defs.indentation,
                        help="""
                        indentation to use for continuation lines (default 4)
                        """)
    parser.add_argument('--fixed-format', action='store_true',
                        dest='fixed_format', default=defs.fixed_format,
                        help="""
                        produce fixed format output (any settings for options
                        --line-length, --folding-method and --indentation are ignored)
                        """)
    parser.add_argument('--encoding', metavar='ENC', default=defs.encoding,
                        help="""
                        character encoding for reading/writing files. Default: 'utf-8'.
                        Note: reading from stdin and writing to stdout is encoded
                        according to the current locale and is not affected by this setting.
                        """)
    parser.add_argument('-p', '--create-parents', action='store_true',
                        dest='create_parent_folder',
                        default=defs.create_parent_folder,
                        help="""
                        create parent folders of the output file if they do not exist
                        """)
    parser.add_argument('--file-var-root', metavar='DIR',
                        dest='file_var_root',
                        default=defs.file_var_root,
                        help="""
                        in variables _FILE_ and _THIS_FILE_, use relative paths with DIR
                        as root directory. Note: the input file and all included files
                        must be in DIR or in a directory below.
                        """)

    return parser


def run_fypp():
    """Run the Fypp command line tool."""
    parser = get_option_parser()
    opts, leftover = parser.parse_known_args()
    infile = leftover[0] if len(leftover) > 0 else '-'
    outfile = leftover[1] if len(leftover) > 1 else '-'
    try:
        tool = Fypp(opts)
        tool.process_file(infile, outfile)
    except FyppStopRequest as exc:
        sys.stderr.write(_formatted_exception(exc))
        sys.exit(USER_ERROR_EXIT_CODE)
    except FyppFatalError as exc:
        sys.stderr.write(_formatted_exception(exc))
        sys.exit(ERROR_EXIT_CODE)
