.. highlight:: none

************
Introduction
************

Fypp is a Python powered preprocessor. It can be used for any programming
languages but its primary aim is to offer a Fortran preprocessor, which helps to
extend Fortran with condititional compiling and template metaprogramming
capabilities. Instead of introducing its own expression syntax, it uses Python
expressions in its preprocessor directives, offering the consistency and
versatility of Python when formulating metaprogramming tasks. It puts strong
emphasis on robustness and on neat integration into developing toolchains.

Fypp was inspired by the `pyratemp
<http://www.simple-is-better.org/template/pyratemp.html>`_ templating engine
[#]_. Although it shares many concepts with pyratemp, it was written from
scratch focusing on the special needs when preprocessing source code. Fypp
natively supports the output of line numbering markers, which are used by
many compilers to generate compiler messages with correct line numbers. Unlike
most cpp/fpp-like preprocessors or the coco preprocessor, Fypp also supports
iterations, multiline macros, continuation lines in preprocessor directives and
automatic line folding. It generally tries to extend the modern Fortran language
with metaprogramming capabilities without tempting you to use it for tasks which
could/should be done in Fortran itself.

The project is `hosted on github <https://github.com/aradi/fypp>`_ with
documentation available on `readthedocs.org
<http://fypp.readthedocs.org>`_. Fypp is released under the *BSD 2-clause
license*.

This document describes Fypp Version 2.1.


Features
========

Below you find a summary over Fypps main features. Each of them is described
more in detail in the individual sections further down.

* Definition, evaluation and removal of variables::

    #:if DEBUG > 0
      print *, "Some debug information"
    #:endif

    #:set LOGLEVEL = 2
    print *, "LOGLEVEL: ${LOGLEVEL}$"

    #:del LOGLEVEL

* Macro definitions and macro calls::

    #:def ASSERT(cond)
      #:if DEBUG > 0
        if (.not. ${cond}$) then
          print *, "Assert failed in file ${_FILE_}$, line ${_LINE_}$"
          error stop
        end if
      #:endif
    #:enddef ASSERT

    ! Invoked via direct call (argument needs no quotation)
    @:ASSERT(size(myArray) > 0)

    ! Invoked as Python expression (argument needs quotation)
    $:ASSERT('size(myArray) > 0')

* Conditional output::

    program test
    #:if defined('WITH_MPI')
      use mpi
    #:elif defined('WITH_OPENMP')
      use openmp
    #:else
      use serial
    #:endif

* Iterated output (e.g. for generating Fortran templates)::

    interface myfunc
    #:for dtype in ['real', 'dreal', 'complex', 'dcomplex']
      module procedure myfunc_${dtype}$
    #:endfor
    end interface myfunc

* Inline directives::

    logical, parameter :: hasMpi = #{if defined('MPI')}# .true. #{else}# .false. #{endif}#

* Insertion of arbitrary Python expressions::

    character(*), parameter :: comp_date = "${time.strftime('%Y-%m-%d')}$"

* Inclusion of files during preprocessing::

    #:include "macrodefs.fypp"

* Using Fortran-style continutation lines in preprocessor directives::

    #:if var1 > var2 &
        & or var2 > var4
      print *, "Doing something here"
    #:endif

* Passing (unquoted) multiline string arguments to callables::

    #! Callable needs only string argument
    #:def DEBUG_CODE(code)
      #:if DEBUG > 0
        $:code
      #:endif
    #:enddef DEBUG_CODE

    #! Pass code block as first positional argument
    #:block DEBUG_CODE
      if (size(array) > 100) then
        print *, "DEBUG: spuriously large array"
      end if
    #:endblock DEBUG_CODE

    #! Callable needs also non-string argument types
    #:def REPEAT_CODE(code, repeat)
      #:for ind in range(repeat)
        $:code
      #:endfor
    #:enddef REPEAT_CODE

    #! Pass code block as positional argument and 3 as keyword argument "repeat"
    #:block REPEAT_CODE(repeat=3)
    this will be repeated 3 times
    #:endblock REPEAT_CODE


* Preprocessor comments::

    #! This will not show up in the output
    #! Also the newline characters at the end of the lines will be suppressed

* Suppressing the preprocessor output in selected regions::

    #! Definitions are read, but no output (e.g. newlines) will be produced
    #:mute
    #:include "macrodefs.fypp"
    #:endmute

* Explicit request for stopping the preprocessor::

    #:if DEBUGLEVEL < 0
      #:stop 'Negative debug level not allowed!'
    #:endif

* Easy check for macro parameter sanity::

    #:def mymacro(RANK)
      #! Macro only works for RANK 1 and above
      #:assert RANK > 0
      :
    #:enddef mymacro

* Line numbering markers in output::

    program test
    #:if defined('MPI')
    use mpi
    #:endif
    :

  transformed to ::

    # 1 "test.fypp" 1
    program test
    # 3 "test.fypp"
    use mpi
    # 5 "test.fypp"
    :

  when variable ``MPI`` is defined and Fypp was instructed to generate line
  markers.

* Automatic folding of generated lines exceeding line length limit


***************
Getting started
***************

Installing
==========

Fypp needs a working Python interpreter. It is compatible with Python 2 (version
2.6 and above) and Python 3 (all versions).


Automatic install
-----------------

Use Pythons command line installer ``pip`` in order to download the stable
release from the `Fypp page on PyPI <http://pypi.python.org/pypi/fypp>`_ and
install it on your system::

  pip install fypp

This installs both, the command line tool ``fypp`` and the Python module
``fypp.py``. Latter you can import if you want to access the functionality of
Fypp directly from within your Python scripts.


Manual install
--------------

For a manual install, you can download the source code of the latest **stable**
release from the `Fypp project website
<https://github.com/aradi/fypp/releases>`_.

If you wish to obtain the latest **development** version, clone the projects
repository::

  git clone https://github.com/aradi/fypp.git

and check out the `master` branch.

The command line tool is a single stand-alone script. You can run it directly
from the source folder ::

  FYPP_SOURCE_FOLDER/bin/fypp

or after copying it from the `bin` folder to any location listed in your `PATH`
environment variable, by just issuing ::

  fypp

The python module ``fypp.py`` can be found in ``FYP_SOURCE_FOLDER/src``.


Testing
=======

Simple manual testing can be done by issuing the command ::

  ./test/runtests.sh

from the root of the Fypp source tree. This executes the unit tests shipped with
Fypp with the default Python interpreter in your path. If you wish to use a
specific interpreter, you can pass it as argument to the script::

  ./test/runtests.sh python3

You can also pass multiple interpreters as separate arguments. In that case
the testing will be carried out for each of them.


Testing for developers
----------------------

If you wish to contribute to Fypp, you should have `tox` installed on your
system, so that you can test the packaged project in isolated environments
before issuing a pull request.

In order to execute the unit tests with `tox`, run  ::

  tox

from the root folder of the source tree. This tries to test Fypp with various
different python interpreters. If you want to limit testing to selected
interpeters only, select the environment with the appropriate command line
switch, e.g. ::

  tox -e py34



Running
=======

The Fypp command line tool reads a file, preprocesses it and writes it to
another file, so you would typically invoke it like::

  fypp source.fpp source.f90

which would process `source.fpp` and write the result to `source.f90`.  If
input and output files are not specified, information is read from stdin and
written to stdout.

The behavior of Fypp can be influenced with various command line options. A
summary of all command line options can be obtained by::

  fypp -h


*********************
Preprocessor language
*********************


General syntax
==============

Fypp has three types of preprocessor directives, all of them having a line and
an inline form:

*  Control directives

   * Line form, starting with ``#:`` (hashmark colon)::

       #:if 1 > 2
         Some code
       #:endif

   * Inline form, enclosed between ``#{`` and ``}#``::

       #{if 1 > 2}#Some code#{endif}#

* Eval directives

  * Line form, starting with ``$:`` (dollar colon)::

      $:time.strftime('%Y-%m-%d')

  * Inline form, enclosed between ``${`` and ``}$``::

      print *, "Compilation date: ${time.strftime('%Y-%m-%d')}$"

* Direct call directive

  * Line form, starting with ``@:`` (at colon)::

      @:mymacro(a < b)

  * Inline form, enclosed between ``@{`` and ``}@``::

      print *, @{mymacro(a < b)}@

The line form must always start at the beginning of a line (preceded by optional
whitespace characters only) and it ends at the end of the line. The inline form
can appear anywhere, but if the construct consists of several directives
(e.g. ``#{if ...}#`` and ``#{endif}#``), all of them must appear on the same
line. While both forms can be used at the same time, they must be consistent for
a particular construct, e.g. a directive opened as line directive can not be
closed by an inline directive and vica versa.

Whitespaces in preprocessor commands are ignored if they appear after the
opening colon or curly brace or before the closing curly brace. So the following
examples are pairwise equivalent::

  #:if 1 > 2
  #: if 1 > 2

  #{if 1 > 2}#
  #{ if 1 > 2 }#

  $:time.strftime('%Y-%m-%d')
  $: time.strftime('%Y-%m-%d')

  ${time.strftime('%Y-%m-%d')}$
  ${ time.strftime('%Y-%m-%d') }$

Starting whitespaces before line directives are ignored, enabling you to choose
any indentation strategy you like for the directives::

  program test
    :
    do ii = 1, nn
      print *, ii
    #:if DEBUG > 0
      print *, "Some debug info about iteration ${ii}$"
    #:endif
      print *, "Normal code"
    end do
    :
  end program test

Preprocessor directives can be arbitrarily nested::

  #:if DEBUG > 0
    #:if DO_LOGGING
      ...
    #:endif
  #:endif

Every open directive must be closed before the end of the file is reached.

In all control directives, the whitespace separating the name of the directive
from the following parameter is obligatory. Therefore, the following example is
syntactically incorrect::

  #! Incorrect due to missing whitespace after 'if'
  #:if(1 > 2)


Expression evaluation
=====================

Python expressions can occur either as part of control directives, like ::

  #:if DEBUG > 0
  #:for dtype in ['real(dp)', 'integer', 'logical']

or directly inserted into the code using eval directives. ::

  $:time.strftime('%Y-%m-%d')
  print *, "${time.strftime('%Y-%m-%d')}$"

Expressions are always evaluated by using Pythons ``eval()`` builtin and must
be, therefore, syntactically and semantically correct Python
expressions. Although, this may require some additional quotations as compared
to other preprocessor languages ::

  #:if defined('DEBUG')  #! The Python function defined() expects a string argument
  #:for dtype in ['real(dp)', 'integer', 'logical']  #! dtype runs over strings

it enables consistent expressions with (hopefully) least surprises (once you
know, how to formulate the expression in Python, you exactly know, how to write
it for Fypp). Also, note, that variable names, macros etc. are for Python (and
therefore also for Fypp) case sensitive.

When you access a variable in an expression, it must have been already defined
before, either via command line options or via preprocessor directives. For
example the directive ::

  #:if DEBUG > 0

can only be evaluated, if the variable `DEBUG` had been already defined before.


Python sandbox
==============

Python expressions are evaluted in an isolated Python environment, which
contains a restricted set of Python built-in functions and a few predefined
variables and functions (see below). There are no modules loaded by default, and
for safety reasons, no modules can be loaded once the preprocessing has
started, but can be loaded at startup if needed.

Predefined variables
--------------------

The isolated Python environment for the expression evaluation contains following
predefined global variables:

* ``_THIS_LINE_``: number of current line

* ``_THIS_FILE_``: name of current file

* ``_LINE_``: number of current line in the processed input file

* ``_FILE_``: name of processed input file ::

    print *, "This is line nr. ${_LINE_}$ in file '${_FILE_}$'"

* ``_DATE_``: current date in ISO format

* ``_TIME_``: current time::

    print *, "Rendering started ${_DATE_}$ ${_TIME_}$"

The predefined variables ``_FILE_`` and ``_LINE_`` differ from their
counterparts ``_THIS_FILE_`` and ``_THIS_LINE_`` only within macros. When a
macro is executed, the variables ``_THIS_FILE_`` and ``_THIS_LINE_`` specify the
position, where the expression containing these variables is located, while the
variables ``_FILE_`` and ``_LINE_`` refer to the position in the processed file,
from where the macro was called (and where the result of the evaluation will be
inserted later). For example, the input ::

  #:def macro()
  IN MACRO: _THIS_LINE_=${_THIS_LINE_}$, _LINE_=${_LINE_}$
  #:enddef macro

  GLOBAL: _THIS_LINE_=${_THIS_LINE_}$, _LINE_=${_LINE_}$ | ${macro()}$

yields after being processed by Fypp::

  GLOBAL: _THIS_LINE_=5, _LINE_=5 | IN MACRO: _THIS_LINE_=2, _LINE_=5

If from within a macro an other macro is called, the variables ``_FILE_`` and
``_LINE_`` will keep their original values, while ``_THIS_FILE_`` and
``_THIS_LINE_`` will be continuously updated within the nested macro as well.


Predefined functions
--------------------

Following predefined functions are available:

* ``defined(VARNAME)``: Returns ``True`` if a variable with a given name has
  been already defined. The variable name must be provided as string::

    #:if defined('WITH_MPI')

* ``getvar(VARNAME, DEFAULTVALUE)``: Returns the value of a variable or a
  default value if the variable is not defined. The variable name must be
  provided as string::

    #:if getvar('DEBUG', 0)

* ``setvar(VARNAME, VALUE)``: Sets a variable to given value. It is identical to
  the `set directive`_. The variable name expression has the same format as in
  the ``#:set`` directive, but must be quoted::

    $:setvar('i', 12)
    print *, "VAR I: ${i}$"

  Multiple assignments may be specified as subsequent argument pairs::

    $:setvar('i', 1, 'j', 2)
    print *, "VAR I: ${i}$, VAR J: ${j}$"

* ``delvar(VARNAME)``: Removes a variable or a macro definition from the local
  scope. It is identical to the `del directive`_. The variable name
  expression must be provided as in the ``#:del`` directive, but must be quoted::

    $:delvar('i')

  Additional variable name expressions may be specified as subsequent arguments::

    $:delvar('i', 'j')


* ``globalvar(VARNAME)``: Adds a given variable as global variable to the
  current scope.  It is identical to the `global directive`_. The variable name
  expression must be provided as in the ``#:global`` directive, but must be
  quoted::

    $:globalvar('i')

  Multiple variable name expressions may be specified as subsequent arguments.


Initializing variables
----------------------

Initial values for preprocessor variables can be set via the command line option
(``-D``) at startup::

  fypp -DDEBUG=0 -DWITH_MPI

The assigned value for a given variable is evaluated in Python. If no value is
provided, `None` is assigned.


Importing modules at startup
----------------------------

.. warning:: Modules imported at startup have access to the full
   **unrestricted** Python environment and can execute any Python code. Import
   only trustworthy modules!

If a Python module is required for the preprocessing, it can be imported before
the preprocessing starts via the command line option (``-m``)::

  fypp -m time

The example above would allow to process the line::

  character(*), parameter :: comp_date = "${time.strftime('%Y-%m-%d')}$"

If more than one module is needed, each of them can imported with an individual
``-m`` option::

  fypp -m time -m math

When importing modules with the ``-m`` option, the module search path consists
of the current directory, the directories in the `PYTHONPATH` environment
variable and the standard Python module paths. Further lookup paths can be
specified using the option ``-M``::

  fypp -M mymoddir1 -M mymoddir2 -m mymodule -m mymodule2

The module directories are looked up in the order they are specified *before*
searching at the default locations. Modules are imported also in the order of
their specification at the command line.

Each module imported at startup has its own name space. Entities in the imported
modules can be accessed during the preprocessing in the usual pythonic
way. After importing the module ``mymodule`` as in the example above, entities
in the module could be accessed as::

  ${mymodule.SOME_CONSTANT}$

  $:mymodule.SOME_CONSTANT

  $:mymodule.some_function()

  @:mymodule.some_function()

  #:call mymodule.some_function
  #:endcall mymodule.some_function

  #:block mymodule.some_function
  #:endblock mymodule.some_function



Eval directive
==============

A result of a Python expression can be inserted into the code by using eval
directives ``$:`` (line form) or ``${`` and ``}$`` (inline form). The expression
is evaluated using Python's built-in function `eval()`. If it evaluates to
`None`, no output is produced. Otherwise the result is converted to a string and
written to the output. The eval directive has both, a line and an inline
variant::

 $:somePythonFunction()
 print *, "DEBUG LEVEL: ${DEBUG}$"

.. warning:: Lines containing eval directive(s) will be folded using
   Fortran continuation lines when getting longer than a specified maximum. They
   must, therefore, not contain anything which could lead to invalid source
   code, when being folded at an arbitrary position (e.g. Fortran comments).


`set` directive
==================

The value of a variable can be set during the preprocessing via the `set`
directive. (Otherwise, variables can be also declared and defined via command
line options.) The first argument is the name of the variable (unquoted),
followed by an optional Python expression. If the Python expression is present,
it must be separated by an equal sign from the variable name. If the Python
expression and the equal sign are not present, the variable is set to `None`::

  #:set DEBUG
  #:set LOG = 1
  #:set LOGLEVEL = LOGLEVEL + 1

Note, that in the last example the variable `LOGLEVEL` must have been already
defined in advance.

The `set` directive also accepts assignments to variable tuples, provided the
right hand side of the assignment is compatible with the variable tuple::

  #:set VAR1, VAR2 = 1, 2
  #:set (VAR1, VAR2) = 1, 2

The parantheses around the variable list (second example) are optional.

The `set` directive can be also used in the inline form::

  #{set X = 2}#print *, ${X}$

Similar to the line form, the separating equal sign is optional here as well.


`del` directive
===============

A variable (or macro) definition can be removed from the current scope by the
`del` directive::

  #:set X = 12
  #! X available, with value 12
  :
  #:del X
  #! X not available any more

The variable name expression syntax is identical to the one used for the `set`
directive, so that also variable tuples can be deleted::

  #! Removes the variables X and Y from local scope
  #:del X, Y

The variable passed to the ``del`` directive must exist and be erasable. So the
example above would trigger an error, if the variables ``X`` and ``Y`` were not
defined before.

The `del` directive can also be used to delete macro defintions::

  #:def echo(TXT)
  ${TXT}$
  #:enddef
  @:echo(HELLO)
  #:del echo
  #! Following line throws an error as macro echo is not available any more
  @:echo(HELLO)

The `del` directive can be also used in the inline form::

  #{del X}#


`if` directive
==============

Conditional output can be generated using the `if` directive. The condition must
be a Python expression, which can be converted to a `bool`. If the condition
evaluates to `True`, the enclosed code is written to the output, otherwise it is
ignored.

::

  print *, "Before"
  #:if DEBUG > 0
  print *, "Debug code"
  #:endif
  print *, "After"

would result in

::

  print *, "Before"
  print *, "Debug code"
  print *, "After"

if the Python expression ``DEBUG > 0`` evaluates to `True`, otherwise in

::

  print *, "Before"
  print *, "After"

For more complex scenarios ``elif`` and ``else`` branches can be
used as well::

    #:if DEBUG >= 2
    print *, "Very detailed debug info"
    #:elif DEBUG >= 1
    print *, "Less detailed debug info"
    #:else
    print *, "No debug info"
    #:endif

The `if` directive is also available as inline directive::

  print *, "COMPILATION MODE: #{if DEBUG > 0}#DEBUG#{else}#PRODUCTION#{endif}#"


`for` directive
===============

Fortran templates can be easily created by using the `for` directive. The
following example creates a function for calculating the sine square for both
single and double precision reals::

  #:set real_kinds = ['sp', 'dp']

  interface sin2
  #:for rkind in real_kinds
    module procedure sin2_${rkind}$
  #:endfor
  end interface sin2

  #:for rkind in real_kinds
  function sin2_${rkind}$(xx) result(res)
    real(${rkind}$), intent(in) :: xx
    real(${rkind}$) :: res

    res = sin(xx) * sin(xx)

  end function sin2_${rkind}$
  #:endfor

The `for` directive expects a Python loop variable expression and an iterable
separated by the ``in`` keyword. The code within the `for` directive is outputed
for every iteration with the current value of the loop variable, which can be
inserted using eval directives. If the iterable consists of iterables
(e.g. tuples), usual indexing can be used to access their components, or a
variable tuple to unpack them directly in the loop header::

  #:set kinds = ['sp', 'dp']
  #:set names = ['real', 'dreal']
  #! create kinds_names as [('sp', 'real'), ('dp', 'dreal')]
  #:set kinds_names = list(zip(kinds, names))

  #! Acces by indexing
  interface sin2
  #:for kind_name in kinds_names
    module procedure sin2_${kind_name[1]}$
  #:endfor
  end interface sin2

  #! Unpacking in the loop header
  #:for kind, name in kinds_names
  function sin2_${name}$(xx) result(res)
    real(${kind}$), intent(in) :: xx
    real(${kind}$) :: res

    res = sin(xx) * sin(xx)

  end function sin2_${name}$
  #:endfor


The `for` directive can be used also in its inline form::

  print *, "Numbers: #{for i in range(5)}#${i}$#{endfor}#"



`def` directive
===============

Parametrized macros can be defined with the `def` directive. This defines a
regular callable in Python, which returns the rendered content of the macro body
when called. The macro arguments are converted to local variables containing the
actual arguments as values. The macro can be called from within an
eval-directive, via the `call` and `block` control directives and via their
abreviated form, the direct call.

Given the macro definition ::

  #:def ASSERT(cond)
  #:if DEBUG > 0
  if (.not. (${cond}$)) then
    print *, "Assert failed!"
    error stop
  end if
  #:endif
  #:enddef

the following three calls ::

  #! call macro by evaluating a Python expression
  $:ASSERT('x > y')

  #! call macro by using the call directive (see below)
  #:call ASSERT
  x > y
  #:endcall ASSERT

  #! call macro by using the block directive (see below)
  #:block ASSERT
  x > y
  #:endblock ASSERT

  #! call macro by using the direct call directive (see below)
  @:ASSERT(x > y)

would all yield ::

  if (.not. (x > y)) then
    print *, "Assert failed!"
    error stop
  end if

if the variable `DEBUG` had a value greater than zero or an empty string
otherwise.

It is possible to declare default values for the positional arguments of a
macro. If for a given positional argument such a value is provided, then default
values must be provided for all following arguments as well. When the macro is
called, missing positional arguments will be replaced by their default value::

  #:def macro(X, Y=2, Z=3)
  X=${X}$, Y=${Y}$, Z=${Z}$
  #:enddef macro

  $:macro(1)   #! Returns "X=1, Y=2, Z=3"

Similar to Python, it is also possible to define macros with a variable number
of positional or keyword arguments using the ``*`` and ``**`` argument
prefixes. The corresponding arguments will contain the unprocessed positional
and keywords arguments as a list and a dictionary, respectively::

  #:def macro(X, *VARPOS, **VARKW)
  pos: ${X}$
  varpos: #{for ARG in VARPOS}#${ARG}$, #{endfor}#
  varkw: #{for KEYWORD in VARKW}#${KEYWORD}$->${VARKW[KEYWORD]}$, #{endfor}#
  #:enddef macro

Calling the example macro above with ::

  $:macro(1, 2, 3, kw1=4, kw2=5)

yields::

  pos: 1
  varpos: 2, 3,
  varkw: kw1->4, kw2->5,


Scopes
------

Scopes in general follow the Python convention: Within the macro, all variables
from the encompassing scope are available (as `DEBUG` in the example above), and
additionally those which were passed as arguments. If a variable is defined
within the macro, it will be only accessible within the macro. If a variable
with the same name already exists in the encompassing scope, it will be shadowed
by it for the time of the macro subsitution. For example preprocessing the code
snippet ::

  #:def macro(x)
  print *, "Local XY: ${x}$ ${y}$"
  #:set y = -2
  print *, "Local XY: ${x}$ ${y}$"
  #:enddef

  #:set x = 1
  #:set y = 2
  print *, "Global XY: ${x}$ ${y}$"
  $:macro(-1)
  print *, "Global XY: ${x}$ ${y}$"

would result in ::

  print *, "Global XY: 1 2"
  print *, "Local XY: -1 2"
  print *, "Local XY: -1 -2"
  print *, "Global XY: 1 2"


For better readability, you can repeat the name of the macro (but not its
argument list) at the corresponding enddef directive::

  #:def ASSERT(cond)
    #:if DEBUG > 0
      if (.not. (${cond}$)) then
        print *, "Assert failed!"
        error stop
      end if
    #:endif
  #:enddef ASSERT


The `def` directive has no inline form.

.. warning:: The content of macros is usually inserted via an eval directive and
     is accordingly subject to eventual line folding. Macros should,
     therefore, not contain any inline Fortran comments. (Comments
     starting at the beginning of the line preceeded by optional
     whitespaces only are OK, though). Use preprocessor comments
     (``#!``) instead.


`block` and `call` directives
=============================

When a Python callable (regular Python function, macro etc.) needs a string
argument of larger size (e.g. source code), it can be called using the `call` or
the `block` directives to avoid extra quoting of the text argument and to enable
passing of multiline arguments in a comfortable way::

  #:def DEBUG_CODE(code)
    #:if DEBUG > 0
      $:code
    #:endif
  #:enddef DEBUG_CODE

  #:block DEBUG_CODE
    if (a < b) then
      print *, "DEBUG: a is less than b"
    end if
  #:endblock DEBUG_CODE

  #:call DEBUG_CODE
    if (a < b) then
      print *, "DEBUG: a is less than b"
    end if
  #:endcall DEBUG_CODE

The `block` and the `call` directives are equivalent. The two alternative forms
exists in order to allow for more readable meta-code depending on the context.

The `block` and `call` directives take the name of the callable as argument. The
lines between the opening and closing directives will be rendered and then
passed as positional *string* arguments to the callable. The name of the
callable can be repeated in the `endblock` and `endcall` directives for enhanced
readability::

  #! This form is probably somewhat more natural to read
  #:block DEBUG_CODE
    if (a < b) then
      print *, "DEBUG: a (${a}$) is less than b (${b}$)"
    end if
  #:endblock DEBUG_CODE

  #:call DEBUG_CODE
    if (a < b) then
      print *, "DEBUG: a (${a}$) is less than b (${b}$)"
    end if
  #:endcall DEBUG_CODE

If the callable needs more than one string arguments, the `contains` directive
(for `block`) or the `nextarg` directive (for `call`) can be used to separate
the arguments from each other::

  #:def CHOOSE_CODE(debug_code, nondebug_code)
    #:if DEBUG > 0
      $:debug_code
    #:else
      $:nondebug_code
    #:endif
  #:enddef CHOOSE_CODE

  #:block CHOOSE_CODE
    if (a < b) then
        print *, "DEBUG: a is less than b"
    end if
  #:contains
    print *, "No debugging"
  #:endcall CHOOSE_CODE

  #! This form is probably somewhat more natural to read
  #:call CHOOSE_CODE
    if (a < b) then
        print *, "DEBUG: a is less than b"
    end if
  #:nextarg
    print *, "No debugging"
  #:endcall CHOOSE_CODE

The lines in the body of the `block` and `call` directives may contain
directives themselves. However, any variable defined within the body of the
`block` and `call` directives will be a local variable existing only during the
evaluation of that branch of the directive (and not being available when the
callable is called with the evaluated string as argument).

The `contains` and `nextarg` directives may be followed by an optional argument
name. In that case the text following will be passed as keyword argument to the
callable. If the first argument should be also passed as keyword argument, it
should be also preceeded by a named `contains` or `nextarg` directive declared
in the line immediately following the `block` or `call` directive. If an
argument is passed as a keyword argument, all following arguments must be passed
as keyword arguments as well::

  #:block CHOOSE_CODE
  #:contains nondebug_code
    print *, "No debugging"
  #:contains debug_code
    if (a < b) then
        print *, "DEBUG: a is less than b"
    end if
  #:endblock CHOOSE_CODE

  #:call CHOOSE_CODE
  #:nextarg nondebug_code
    print *, "No debugging"
  #:nextarg debug_code
    if (a < b) then
        print *, "DEBUG: a is less than b"
    end if
  #:endcall CHOOSE_CODE

Additional to passing the content of the `block` or `call` directives body as
string argument, further arguments of arbitrary type can be passed by specifying
them directly in the header of the directive. Among others, this can be very
comfortable when the callable needs also non-string type of arguments::

  #! Argument 'repeat' should be an integer, not string
  #:def REPEAT_CODE(code, repeat)
    #:for ind in range(repeat)
      $:code
    #:endfor
  #:enddef REPEAT_CODE

  #! Code block as positional argument and 3 as keyword argument "repeat"
  #:block REPEAT_CODE(repeat=3)
  this will be repeated 3 times
  #:block REPEAT_CODE

  #! Code block as positional argument and 3 as keyword argument "repeat"
  #:call REPEAT_CODE(repeat=3)
  this will be repeated 3 times
  #:endcall REPEAT_CODE

The arguments must be specified between parantheses and are evaluated as Python
expressions. The arguments specified in the directive (both, in the header and
in the body) are passed to the callable in the following order:

#. positional arguments in the header

#. positional arguments in the body

#. keyword arguments in the header

#. keyword arguments in the body

Callables without arguments can also be called with the `block` and `call`
directives, provided the `endblock` and `endcall` directives immediately follows
the opening directive. If there are empty lines between the opening and the
closing directives, they will be interpreted as a positional argument::

  #:def macro_noarg()
  NOARGS
  #:enddef macro_noarg

  #:def macro_arg1(arg1)
  ARG1:${arg1}$
  #:enddef macro_arg1

  #! Calling macro without arguments
  #:block macro_noarg
  #:endblock macro_noarg

  #! Calling macro without arguments
  #:call macro_noarg
  #:endcall macro_noarg

  #! Calling macro with one positional (empty) argument
  #! Note the empty line between block and endblock
  #:block macro_arg1

  #:endblock macro_arg1

  #! Calling macro with one positional (empty) argument
  #! Note the empty line between call and endcall
  #:call macro_arg1

  #:endcall macro_arg1

The `block` and `call` directives can also be used in their inline form. As this
easily leads to code being hard to read, it should be usually avoided::

  ! Rather ugly
  print *, #{block CHOOSE_CODE}# a(:) #{contains}# size(a) #{endblock}#

  ! Rather ugly as well
  print *, #{call CHOOSE_CODE}# a(:) #{nextarg}# size(a) #{endcall}#

  ! This form is more readable
  print *, ${CHOOSE_CODE('a(:)', 'size(a)')}$

  ! Alternatively, you may use a direct call (see next section)
  print *, @{CHOOSE_CODE(a(:), size(a))}@

If the callable only requires short text arguments, the more compact direct call
directive should be used as an alternative (see next section).


Direct call directive
=====================

In order to enable compact (single line) calls while still maintaining code
readability, the `block` and `call` directives have an alternative form, the
direct call directive::

  #:def ASSERT(cond)
    #:if DEBUG > 0
      if (.not. (${cond}$)) then
        print *, "Assert failed!"
        error stop
      end if
    #:endif
  #:enddef ASSERT

  @:ASSERT(size(aa) >= size(bb))

The direct call directive starts with ``@:`` followed by the name of a Python
callable and an opening paranthesis (``(``). Everything after that up to the
closing paranthesis (``)``) is passed as *string argument* to the callable. The
closing paranthesis may only be followed by whitespace characters.

When the callable needs more than one argument, the arguments must be separated
by a comma (``,``)::

  #:def ASSERT_EQUAL(received, expected)
    if (${received}$ /= ${expected}$) then
      print *, "ASSERT_EQUAL failed (${received}$ /= ${expected}$)!"
      error stop
    end if
  #:enddef ASSERT_EQUAL

  @:ASSERT_EQUAL(size(coords, dim=2), size(atomtypes))

.. note:: In order to be able to split the argument string of a direct call
          correctly, Fypp assumes that all provided arguments represent valid
          Fortran expressions with balanced quotes (``'`` or ``"``) and balanced
          brackets (``()``, ``[]`` and ``{}``) outside of quoted regions. The
          argument string is only split around commas which are outside of any
          quoted or bracketed regions.

Arguments can be optionally enclosed within curly braces in order to avoid
argument splitting at unwanted places or to improve readability. The outermost
curly braces will be removed from the arguments before they are passed to the
callable::

  #! Passes "a**2 + b**2" and "c**2" as string arguments to ASSERT_EQUAL
  @:ASSERT_EQUAL({a**2 + b**2}, c**2)

Keywords arguments can be passed by prefixing them with the keyword name
and an equal sign::

  @:ASSERT_EQUAL(expected=size(atomtypes), received=size(coords, dim=2))
  @:ASSERT_EQUAL(expected=c**2, received={a**2 + b**2})

If the equal sign is followed immediately by an other equal sign, the argument
will be recognized as positional and not as keyword argument. This exception
allows for passing valid Fortran code containing the comparison operator
(``==``) without the need for special bracketing. In other cases, however,
bracketing may be needed to avoid recognition as keyword argument::

  #! Passes string "a == b" as first positional argument
  @:ASSERT(a == b)

  #! Passes string "=b" as keyword argument "a"
  @:ASSERT(a={=b})

  #! Passes string "b" as keyword argument "a"
  @:someMacro(a = b)

  #! Passes "a = b" as positional argument
  @:someMacro({a = b})

The direct call directive may contain continuation lines::

  @:ASSERT_EQUAL(size(coords, dim=2), &
      & size(atomtypes))

The arguments are parsed for further inline eval directives (but not for any
inline control or direct call directives), making variable substitutions in the
arguments possible::

  #:set MYSIZE = 2
  @:ASSERT_EQUAL(size(coords, dim=2), ${MYSIZE}$)

Whitespaces around the arguments of the direct call are stripped, but not the
whitespaces within the optional curly braces around the argument::

  #! Calls a macro without arguments
  @:macro_without_args()

  #! Calls a macro with no arguments (whitespace between () is stripped):
  @:macro_without_args( )

  #! Calls a macro with empty string as argument
  @:macro_with_one_arg({})

  #! Calls a macro with one space as argument
  @:macro_with_one_arg({ })

The direct call directive can also be used in its inline form::

  #! Using CHOOSE_CODE() macro defined in previous section
  print *, @{CHOOSE_CODE(a(:), size(a))}@


`global` directive
==================

Global variables are by default read-only in local scopes (e.g. within
macros). This can be changed for selected variables by using the `global`
directive::

  #:def set_debug(value)
    #:global DEBUG
    #:set DEBUG = value
  #:enddef set_debug

  #:set DEBUG = 1
  $:DEBUG
  $:set_debug(2)
  $:DEBUG

In the example above, without the `global` directive, the `set` directive would
have created a local variable within the macro, which had shadowed the global
variable and was destroyed at the end of the macro execution. With the `global`
directive the `set` refers to the variable in the global scope. The
variable in the global scope does not need to exist yet, when the `global`
directive is executed. It will be then created at the first `set` directive, or
remain non-existing if no assignment is made in the current scope.

A variable can only made global, if it was not created in the local scope
yet. Therefore, the following code would throw an exception::

  #:def set_debug(value)
    #! DEBUG variable created in local scope
    #:set DEBUG = value

    #! Invalid: variable DEBUG already exists in local scope
    #:global DEBUG
  #:enddef set_debug

  # Throws exception
  $:set_debug(2)


`include` directive
===================

The `include` directive allows you to collect your preprocessor macros and
variable definitions in separate files and include them whenever needed. The
include directive expects a quoted string with a file name::

  #:include 'mydefs.fypp'

If the file name is relative, it is interpreted relative to the folder where the
processed file is located (or to the current folder, if Fypp reads from
stdin). Further lookup paths can be added with the ``-I`` command line option.

The `include` directive does not have an inline form.


`mute` directive
================

Empty lines between Fypp definitions makes the code easier to read. However,
being outside of Fypp-directives, those empty lines will be written unaltered to
the output. This can be especially disturbing if various macro definition
files are included, as the resulting output would eventually contian a lot of
empty lines. With the `mute` directive, the output can be suspended. While
everything is still processed as normal, no output is written for the code
within the `mute` directive::

  #:mute

  #:include "mydefs1.fypp"
  #:include "mydefs2.fypp"

  #:def test(x)
  print *, "TEST: ${x}$"
  #:enddef test

  #:endmute
  $:test('me')

The example above would only produce ::

  print *, "TEST: me"

as output without any newlines.

The `mute` directive does not have an inline form.


`stop` directive
================

The `stop` directive can be used to report an error and stop the preprocessor
before all input has been consumed. This can be useful in cases, where some
external conditions (e.g. user defined variables) do not meet certain
criteria. The directive expects a Python expression, which will be converted to
string and written to standard error. After writing the error message Fypp exits
immediately with a non-zero exit code (see `Exit Codes`_)::

    #! Stop the code if DEBUGLEVEL is not positive
    #:if DEBUGLEVEL < 0
      #:stop 'Wrong debug level {}!'.format(DEBUGLEVEL)
    #:endif

There is no inline form of the `stop` directive.


`assert` directive
==================

The `assert` directive is a short form for the combination of an `if` and a
`stop` directive. It evaluates a given expression and stops the code if the
boolean value of the result is `False`. This can be very convenient, if you want
to write robust macros containing sanity checks for their arguments::

  #:def mymacro(RANK)
    #! Macro only works for RANK 1 and above
    #:assert RANK > 0
    :
  #:enddef mymacro

Given the macro definition above, the macro call ::

  $:mymacro(1)

would pass the `assert` directive in the third line, while the call ::

  $:mymacro(0)

would cause Fypp to stop at it.

When the expression in an `assert` directive evaluates to `False`, Fypp reports
the failed assertion (the condition, the file name and the line number) on
standard error and terminates immediately with a non-zero exit code (see `Exit
Codes`_).

There is no inline form of the `assert` directive.


Comment directive
=================

Comment lines can be added by using the ``#!`` preprocessor directive. The
comment line (including the newlines at their end) will be ignored by the
prepropessor and will not appear in the ouput::

    #! This will not show up in the output

There is no inline form of the comment directive.


****************
Various features
****************


Multiline directives
====================

The line form of the control and eval directives can span arbitrary number of
lines, if Fortran-style continuation charachters are used::

  #:if a > b &
      & or b > c &
      & or c > d
  $:somePythonFunction(param1, &
      &param2)

The line break at the first line must be in the expression, not in the opening
delimiter characters or in the directive name. Similar to Fortran, the
continuation character at the beginning of each continuation line may be left
away, but then all whitespaces at the beginning of the respective continuation
line will be part of the expression.

Inline directives must not contain any continuation lines.


Line folding
============

The Fortran standard only allows source lines up to 132 characters. In order to
emit standard conforming code, Fypp folds all lines in the output which it had
manipulated before (all lines containing eval directives). Lines which were
just copied to the output are left unaltered. The maximal line length can be
chosen by the ``-l`` command line option. The indentation of the continuation
lines can be tuned with the ``--indentation`` option, and the folding strategy
can be selected by the ``-f`` option with following possibilities:

* ``brute``: Continuation lines are indented relative to the beginning of
  the line, and each line is folded at the maximal line position.

* ``simple``: Like ``brute``, but continuation lines are indented with respect
  of the indentation of the original line.

* ``smart``: Like ``simple``, but Fypp tries to fold the line at a whitespace
  character in order to prevent split tokens. To prevent continuation lines
  becoming too short, it defaults to ``simple`` if no whitespace occurs in the
  last third of the line.

The ``-F`` option can be used to turn off line folding.


.. warning:: Fypp is not aware of the Fortran semantics of the lines it folds.

Fypp applies the line folding mechanically (only considering the position of the
whitespace characters). Lines containing eval directives and lines within macro
definitions should, therefore, not contain any Fortran style comments (started
by ``!``) *within* the line, as folding within the comment would result in
invalid Fortran code. For comments within such lines, Fypps comment directive
(``#!``) can be used instead::

  #:def macro()
  print *, "DO NOT DO THIS!"  ! Warning: Line may be folded within the comment
  print *, "This is OK."  #! Preprocessor comment is safe as it will be stripped

For comments starting at the beginning of the line (preceeded by optional
whitespace characters only) the folding is suppressed, though. This enables you
to define macros with non-negligible comment lines (e.g. with source code
documentation or OpenMP directives)::

  #:def macro(DTYPE)
  !> This functions calculates something (version ${DTYPE}$)
  !! \param xx  Ingoing value
  !! \return  Some calculated value.
  ${DTYPE}$ function calcSomething(xx)
  :
  end function calcSomething
  #:enddef macro


Escaping
========

If you want to prevent Fypp to interprete something as a directive, put a
backslash (``\``) between the first and second delimiter character. In case of
inline directives, do it for both, the opening and the closing delimiter::

  $\: 1 + 2
  #\{if 1 > 2}\#
  @\:myMacro arg1

Fypp will not recognize the escaped strings as directives, but will remove the
backslash between the delimiter characters in the output. If you put more than
one backslash between the delimiters, only one will be removed.


Line numbering markers
======================

In order to support compilers in emitting messages with correct line numbers
with respect to the original source file, Fypp can put line number directives
(a.k.a. line markers) in its output. This can be enabled by using the command
line option ``-n``. Given a file ``test.fpp`` with the content ::

  program test
  #:if defined('MPI')
  use mpi
  #:else
  use openmpi
  #:endif
  :
  end program test

the command ::

  fypp -n -DMPI test.fpp

produces the output ::

  # 1 "test.fpp" 1
  program test
  # 3 "test.fpp"
    use mpi
  # 7 "test.fpp"
  :
  end program test

If during compilation of this output an error occured in the line ``use mpi``
(e.g. the mpi module can not be found), the compiler would know that this line
corresponds to line number 3 in the original file ``test.fpp`` and could emit an
according error message.

The line numbering directives can be fine tuned with the ``-N`` option, which
accepts following mode arguments:

* ``full``: Line numbering directives are emitted whenever lines are
  removed from the original source file or extra lines are added to it.

* ``nocontlines``: Same as full, but line numbering directives are ommitted
  before continuation lines. (Some compilers, like the NAG Fortran compiler,
  have difficulties with line numbering directives before continuation lines).

Note: Due to a bug introduced in GFortran 5 (being also present in major
versions 6), a workaround is needed for obtaining correct error messages when
compiling preprocessed files with those compilers. Please use the command line
option ``--line-marker-format 'gfortran5'`` in those cases.


Scopes
======

Fypp uses a scope concept very similar to Pythons one. There is one global scope
(like in Python modules), and temporary local scopes may be created in special
cases (e.g. during macro calls).

The global scope is the one, which Fypp normaly uses for defining objects. All
imports specified on the command line are carried out in this scope And all
definitions made by the `set` and `def` directives in the processed source file
defines entities in that scope, unless they appear within a `block`, a `call` or
a `def` directive.

Addtional temporary local scopes are opened, whenever

* a macro defined by the `def` directive is called, or

* the body of the `block` or `call` directive is evaluated in order to render
  the text, which will be passed to the callable as argument.

Any entity defined in a local scope is only visible within that scope and is
unaccessible once the scope has been closed. For example the code snippet::

  #:set toupper = lambda s: s.upper()
  #:call toupper
  #:set NUMBER = 9
  here is the number ${NUMBER}$
  #:endcall toupper
  $:defined('NUMBER')

results after preprocessing in ::

  HERE IS THE NUMBER 9
  False

as the variable ``NUMBER`` defined in the local scope is destroyed, when the
scope is closed (the `endcall` directive has been reached).


Lookup rules
------------

When Fypp tries to resolve a name, the lookup rules depend on the scope, in
which the query appears:

* global scope (outside of any `def` or `call` directives): only the global
  scope is searched.

* local scope (within the body of a `call` or `def` directive): first, the
  active local scope is searched. Then the scope embedding it (the scope which
  contains the directive) is searched. Then further embedding scopes are
  searched until finally also the global scope has been checked. The search is
  immediately terminated, if the name has been found in a scope.

Note, that all variables outside of the active scope are read-only. If a
variable with the same name is created in the active scope, it will shadow the
original definition. Once the scope is closed, the variable regains it original
value. For example::

  #:set toupper = lambda s: s.upper()
  #:set X = 1
  #:call toupper
  #:set X = 2
  value ${X}$
  #:endcall toupper
  value ${X}$

results in ::

  VALUE 2
  value 1

Also note, that if a name can not be resolved in the active scope during a macro
evaluation, the relevant embedding scope for the next lookup is the scope, where
the macro has been defined (where the `def` directive occurs), and *not* the
scope, from which the macro is being called. The following snippet demonstrates
this::

  #! GLOBAL SCOPE
  #:set toupper = lambda s: s.upper()
  #:call toupper
  #! LOCAL SCOPE 1

  #:def macro1()
  #! LOCAL SCOPE 2A
  value of x: ${X}$
  #:enddef macro1

  #! LOCAL SCOPE 1

  #:def macro2()
  #! LOCAL SCOPE 2B
  #:set X = 2
  $:macro1()
  #:enddef macro2

  #! LOCAL SCOPE 1
  #:set X = 1
  $:macro2()
  #:endcall

  #! GLOBAL SCOPE

After processing the code above one obtains ``VALUE OF X: 1``. Although in the
local scope 2B, from where the macro ``macro1()`` is called, the value of X is
defined to be ``2``, the relevant scopes for the lookup of X during the macro
evaluation are the local scope 2A of ``macro1()`` (where the eval-directive for
X is located), the local scope 1 (where the `def` directive for ``macro1()``
occurs) and the global scope (which embeds local scope 1). Therefore, at the
macro evaluation the value ``1`` will be substituted as this is the value of X
in scope 1, and scope 1 is the first scope in the lookup order, which provides a
value for X.


Exit codes
==========

When run as a standalone application, Fypp returns one of the following exit
codes to the calling environment:

* 0: Preprocessing finished successfully.

* 1: Stopped due to an unexpected error.

* 2: Explicitely requested stop encountered (`stop directive`_ or `assert
  directive`_).



********
Examples
********

Asserts and debug code
======================

In this example a simple "assert"-mechanism (as can be found in many programming
languages) should be implemented, where run-time checks can be included or
excluded depending on preprocessor variable definitions. Apart of single
assert-like queries, we also want to include larger debug code pieces, which can
be removed in the production code.

First, we create an include file (``checks.fypp``) with the appropriate macros::

  #:mute

  #! Enable debug feature if the preprocessor variable DEBUG has been defined
  #:set DEBUG = defined('DEBUG')


  #! Stops the code, if the condition passed to it is not fulfilled
  #! Only included in debug mode.
  #:def ASSERT(cond, msg=None)
    #:if DEBUG
      if (.not. (${cond}$)) then
        write(*,*) 'Run-time check failed'
        write(*,*) 'Condition: ${cond.replace("'", "''")}$'
        #:if msg is not None
          write(*,*) 'Message: ', ${msg}$
        #:endif
        write(*,*) 'File: ${_FILE_}$'
        write(*,*) 'Line: ', ${_LINE_}$
        stop
      end if
    #:endif
  #:enddef ASSERT


  #! Includes code if in debug mode.
  #:def DEBUG_CODE(code)
    #:if DEBUG
  $:code
    #:endif
  #:enddef DEBUG_CODE

  #:endmute

Remarks:

* All macro defintions are within a ``#:mute`` -- ``#:endmute`` pair in order to
  prevent the appearence of disturbing empty lines (the lines between the macro
  definitions) in the file which includes ``checks.fypp``.

* The preprocessor variable ``DEBUG`` will determine, whether the checks
  and the debug code is left in the preprocessed code or not.

* The content of both macros, ``ASSERT`` and ``DEBUG_CODE``, are only included
  if the variable ``DEBUG`` has been defined.

* We also want to print out the failed condition for more verbose output. As the
  condition may contains apostrophes, we use Python's string replacement method
  to escape them.

With the definitions above, we can use the functionality in any Fortran source
after including ``checks.fypp``::

  #:include 'checks.fypp'

  module testmod
    implicit none

  contains

    subroutine someFunction(ind, uplo)
      integer, intent(in) :: ind
      character, intent(in) :: uplo

      @:ASSERT(ind > 0, msg="Index must be positive")
      @:ASSERT(uplo == 'U' .or. uplo == 'L')

      ! Do something useful here
      ! :

      #:block DEBUG_CODE
        print *, 'We are in debug mode'
        print *, 'The value of ind is', ind
      #:endblock DEBUG_CODE

    end subroutine someFunction

  end module testmod

Now, the file ``testmod.fpp`` can be preprocessed with Fypp. When the variable
``DEBUG`` is not set::

  fypp testmod.fpp testmod.f90

the resulting routine will not contain the conditional code::

  subroutine someFunction(ind, uplo)
    integer, intent(in) :: ind
    character, intent(in) :: uplo




    ! Do something useful here
    ! :



  end subroutine someFunction

On the other hand, if the ``DEBUG`` variable is set::

  fypp -DDEBUG testmod.fpp testmod.f90

the run-time checks and the debug code will be there::

    subroutine someFunction(ind, uplo)
      integer, intent(in) :: ind
      character, intent(in) :: uplo

  if (.not. (ind > 0)) then
    write(*,*) 'Run-time check failed'
    write(*,*) 'Condition: ind > 0'
    write(*,*) 'Message: ', "Index must be positive"
    write(*,*) 'File: testmod.fpp'
    write(*,*) 'Line: ', 12
    stop
  end if
  if (.not. (uplo == 'U' .or. uplo == 'L')) then
    write(*,*) 'Run-time check failed'
    write(*,*) 'Condition: uplo == ''U'' .or. uplo == ''L'''
    write(*,*) 'File: testmod.fpp'
    write(*,*) 'Line: ', 13
    stop
  end if

      ! Do something useful here
      ! :

      print *, 'We are in debug mode'
      print *, 'The value of ind is', ind

    end subroutine someFunction


Generic programming
===================

The example below shows how to create a generic function ``maxRelError()``,
which gives the maximal elementwise relative error for any pair of arrays with
ranks from 0 (scalar) to 7 in single or double precision. The Fortran module
(file ``errorcalc.fpp``) contains the interface ``maxRelError`` which maps to
all the realizations with the different array ranks and precisions::

  #:def ranksuffix(RANK)
  $:'' if RANK == 0 else '(' + ':' + ',:' * (RANK - 1) + ')'
  #:enddef ranksuffix

  #:set PRECISIONS = ['sp', 'dp']
  #:set RANKS = range(0, 8)

  module errorcalc
    implicit none

    integer, parameter :: sp = kind(1.0)
    integer, parameter :: dp = kind(1.0d0)

    interface maxRelError
    #:for PREC in PRECISIONS
      #:for RANK in RANKS
        module procedure maxRelError_${RANK}$_${PREC}$
      #:endfor
    #:endfor
    end interface maxRelError

  contains

  #:for PREC in PRECISIONS
    #:for RANK in RANKS

    function maxRelError_${RANK}$_${PREC}$(obtained, reference) result(res)
      real(${PREC}$), intent(in) :: obtained${ranksuffix(RANK)}$
      real(${PREC}$), intent(in) :: reference${ranksuffix(RANK)}$
      real(${PREC}$) :: res

    #:if RANK == 0
      res = abs((obtained - reference) / reference)
    #:else
      res = maxval(abs((obtained - reference) / reference))
    #:endif

    end function maxRelError_${RANK}$_${PREC}$

    #:endfor
  #:endfor

  end module errorcalc

The macro ``ranksuffix()`` defined at the beginning receives a rank as argument
and returns a string, which is either the empty string (rank 0) or the
appropriate number of dimension placeholder separated by commas and within
parantheses (e.g. ``(:,:)`` for rank 2). The string expression is calculated as
a Python expression, so that we can make use of the powerful string manipulation
routines in Python and write it as a one-line routine.

If we preprocess the Fortran source file ``errorcalc.fpp`` with Fypp::

  fypp errorcalc.fpp errorcalc.f90

the resulting file ``errorcalc.f90`` will contain a module with the generic
interface ``maxRelError()``::

  interface maxRelError
      module procedure maxRelError_0_sp
      module procedure maxRelError_1_sp
      module procedure maxRelError_2_sp
      module procedure maxRelError_3_sp
      module procedure maxRelError_4_sp
      module procedure maxRelError_5_sp
      module procedure maxRelError_6_sp
      module procedure maxRelError_7_sp
      module procedure maxRelError_0_dp
      module procedure maxRelError_1_dp
      module procedure maxRelError_2_dp
      module procedure maxRelError_3_dp
      module procedure maxRelError_4_dp
      module procedure maxRelError_5_dp
      module procedure maxRelError_6_dp
      module procedure maxRelError_7_dp
  end interface maxRelError

The interface maps to the appropriate functions::

  function maxRelError_0_sp(obtained, reference) result(res)
    real(sp), intent(in) :: obtained
    real(sp), intent(in) :: reference
    real(sp) :: res

    res = abs((obtained - reference) / reference)

  end function maxRelError_0_sp


  function maxRelError_1_sp(obtained, reference) result(res)
    real(sp), intent(in) :: obtained(:)
    real(sp), intent(in) :: reference(:)
    real(sp) :: res

    res = maxval(abs((obtained - reference) / reference))

  end function maxRelError_1_sp


  function maxRelError_2_sp(obtained, reference) result(res)
    real(sp), intent(in) :: obtained(:,:)
    real(sp), intent(in) :: reference(:,:)
    real(sp) :: res

    res = maxval(abs((obtained - reference) / reference))

  end function maxRelError_2_sp

  :

The function ``maxRelError()`` can be, therefore, invoked with a pair of arrays
with various ranks or with a pair of scalars, both in single and in double
precision, as required.

If you prefer not to have preprocessor loops around long code blocks, the
example above can be also written by defining a macro first and then calling
the macro within the loop. The function definition would then look as follows::

  contains

  #:def maxRelError_template(RANK, PREC)
    function maxRelError_${RANK}$_${PREC}$(obtained, reference) result(res)
      real(${PREC}$), intent(in) :: obtained${ranksuffix(RANK)}$
      real(${PREC}$), intent(in) :: reference${ranksuffix(RANK)}$
      real(${PREC}$) :: res

    #:if RANK == 0
      res = abs((obtained - reference) / reference)
    #:else
      res = maxval(abs((obtained - reference) / reference))
    #:endif

    end function maxRelError_${RANK}$_${PREC}$
  #:enddef maxRelError_template

  #:for PREC in PRECISIONS
    #:for RANK in RANKS
      $:maxRelError_template(RANK, PREC)
    #:endfor
  #:endfor

  end module errorcalc


***********************************
Integration into build environments
***********************************

Fypp can be integrated into build environments like any other preprocessor. If
your build environment is Python-based, you may consider to access its
functionality directly via its API instead of calling it as an external script
(see the `API documentation`_).

Make
====

In traditional make based system you can define an appropriate preprocessor
rule in your ``Makefile``::

  .fpp.f90:
          fypp $(FYPPFLAGS) $< $@

or for GNU make::

  %.f90: %.fpp
          fypp $(FYPPFLAGS) $< $@


Waf
===

For the `waf` build system the Fypp source tree contains extension modules in
the folder ``tools/waf``. They use Fypps Python API, therefore, the ``fypp``
module must be accessable from Python. Using those waf modules, you can
formulate a Fypp preprocessed Fortran build like the example below::

  def options(opt):
      opt.load('compiler_fc')
      opt.load('fortran_fypp')

  def configure(conf):
      conf.load('compiler_fc')
      conf.load('fortran_fypp')

  def build(bld):
      sources = bld.path.ant_glob('*.fpp')
      bld(
          features='fypp fc fcprogram',
          source=sources,
          target='myprog'
      )

Check the documentation in the corresponding waf modules for further details.


CMake
=====

One possible way of invoking the Fypp preprocessor within the CMake build
framework is demonstrated below (thanks to Jacopo Chevallard for providing the
very first version of this example)::

  ### Pre-process: .fpp -> .f90 via Fypp

  # Create a list of the files to be preprocessed
  set(fppFiles file1.fpp file2.fpp file3.fpp)

  # Pre-process
  foreach(infileName IN LISTS fppFiles)

      # Generate output file name
      string(REGEX REPLACE ".fpp\$" ".f90" outfileName "${infileName}")

      # Create the full path for the new file
      set(outfile "${CMAKE_CURRENT_BINARY_DIR}/${outfileName}")

      # Generate input file name
      set(infile "${CMAKE_CURRENT_SOURCE_DIR}/${infileName}")

      # Custom command to do the processing
      add_custom-command(
          OUTPUT "${outfile}"
          COMMAND fypp "${infile}" "${outfile}"
          MAIN_DEPENDENCY "${infile}"
          VERBATIM)

      # Finally add output file to a list
      set(outFiles ${outFiles} "${outfile}")

  endforeach(infileName)


*****************
API documentation
*****************

Additional to its usage as a command line tool, Fypp can also be operated
directly from Python. This can be especially practical, when Fypp is used in a
Python driven build environment (e.g. waf, Scons). Below you find the detailed
documentation of the API Fypp offers.


fypp module
===========

.. automodule:: fypp


Fypp
====

.. autoclass:: Fypp
   :members:


FyppOptions
===========

.. autoclass:: FyppOptions
   :members:


get_option_parser()
===================

.. autofunction:: get_option_parser()


FyppError
=========

.. autoclass:: FyppError
   :members:


*****
Notes
*****

.. [#] I am indebted to pyratemps author Roland Koebler for some helpful
       discussions.
