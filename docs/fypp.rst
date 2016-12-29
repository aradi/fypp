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
natively supports the output of line numbering directives, which are used by
many compilers to generate compiler messages with correct line numbers. Unlike
most cpp/fpp-like preprocessors or the coco preprocessor, Fypp also supports
iterations, multiline macros, continuation lines in preprocessor directives and
automatic line folding. It generally tries to extend the modern Fortran language
with metaprogramming capabilities without tempting you to use it for tasks which
could/should be done in Fortran itself.

The project is `hosted on bitbucket <http://bitbucket.org/aradi/fypp>`_ with
documentation available on `readthedocs.org
<http://fypp.readthedocs.org>`_. Fypp is released under the *BSD 2-clause
license*.

This document describes Fypp Version 1.3-dev.


Features
========

Below you find a summary over Fypps main features. Each of them is described
more in detail in the individual sections further down.

* Definition, evaluation and removal of variables::

    #:if DEBUG > 0
      print *, "Some debug information"
    #:endif

    #:set LOGLEVEL = 2

    #:del LOGLEVEL

* Macro definitions and macro calls::

    #:def assertTrue(cond)
    #:if DEBUG > 0
    if (.not. ${cond}$) then
      print *, "Assert failed in file ${_FILE_}$, line ${_LINE_}$"
      error stop
    end if
    #:endif
    #:enddef assertTrue

    ! Invoked via direct call (needs no quotation)
    @:assertTrue size(myArray) > 0

    ! Invoked as Python expression (needs quotation)
    $:assertTrue('size(myArray) > 0')


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

    logical, parameter :: hasMpi = #{if defined('MPI')}#.true.#{else}#.false.#{endif}#

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

    #:def debug_code(code)
      #:if DEBUG > 0
        $:code
      #:endif
    #:enddef debug_code

    #:call debug_code
      if (size(array) > 100) then
        print *, "DEBUG: spuriously large array"
      end if
    #:endcall debug_code

    #:call lambda s: s.upper()
    this will be converted to upper case
    #:endcall

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

* Line numbering directives in output::

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

For a manual install, you can download the source code from the `Fypp project
website <http://bitbucket.org/aradi/fypp>`_ ::

  git clone https://aradi@bitbucket.org/aradi/fypp.git

The project follows `Vincent Driessens git workflow
<http://nvie.com/posts/a-successful-git-branching-model/>`_, so in order to
obtain

* the latest **stable** version, check out the `master` branch::

    cd fypp
    git co master

* the latest **development** snapshot, check out the `develop` branch::

    cd fypp
    git co develop


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

Fypp has three types of preprocessor directives, two of them having a line and
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

* Direct call directive, only available as line form, starting with ``@:`` (at
  colon)::

    @:mymacro a < b

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

In all control directives and in the direct call directive, the whitespace
separating the name of the directive or the name of the callable from the
following parameters is obligatory. Therefore, the following example is
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
it for Fypp). Also, note, that variable names, macros etc. are in Python (and
therefore also for Fypp) case sensitive.

When you access a variable in an expression, it must have been already defined
before, either via command line options or via preprocessor directives. For
example the directive ::

  #:if DEBUG > 0

can only be evaluated, if the variable `DEBUG` had been already defined before.

Python expressions are evaluted in an isolated Python environment, which
contains a restricted set of Python built-in functions and a few predefined
variables and functions (see below). There are no modules loaded by default, and
for safety reasons, no modules can be loaded once the preprocessing has started.


Initializing the environment
----------------------------

If a Python module is required for the preprocessing, it can be imported before
the preprocessing starts via the command line option (``-m``)::

  fypp -m time

The example above would allow to process the line::

  character(*), parameter :: comp_date = "${time.strftime('%Y-%m-%d')}$"

If more than one module is needed, each of them can imported with an individual
``-m`` option::

  fypp -m time -m math

Initial values for preprocessor variables can be set via the command line option
(``-D``) at startup::

  fypp -DDEBUG=0 -DWITH_MPI

The assigned value for a given variable is evaluated in Python. If no value is
provided, `None` is assigned.

When complex initialization is needed (e.g. user defined Python functions should
be defined), initialization scripts can be specified via the command line option
``-i``::

  fypp -i ini1.py -i ini2.py

The preprocessor executes the content of each initialization script in the
isolated environment via Pythons `exec()` command before processing any
input. If modules had been also specified via the ``-m`` option, they are
imported before the execution of the initialization scripts. The module imports,
the initialization and the evaluation of the Python expressions during the
processing all use the same global scope (as if they were part of one single
module). Therefore, any globals defined at initialization can be accessed when
evaluating Python expressions during input processing. Additionally, functions
defined during initialization can access global variables defined during the
processing, provided the variables have been defined, before the function is
invoked.

When importing modules with the ``-m`` option, the module search path consists
of the current directory, the directories in the `PYTHONPATH` environment
variable and the standard Python module paths. When executing an initialization
file via the ``-i`` option, the current directory in the module search path is
replaced by the directory containing the initialization file. Modules in
initialization files must be imported into the global scope, directly when the
initialization files are executed, as once all initialization files have been
processed, module imports are not possible any more.


Predefined variables and functions
==================================

Variables
---------

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
counterparts ``_THIS_FILE_`` and ``_THIS_LINE_`` only in cases, where the output
of an expression evaluation is diverted, so that it can be written at a later
stage. This typically happens during macro evaluations or when the arguments are
rendered for the ``call`` directive. In such cases, the variables
``_THIS_FILE_`` and ``_THIS_LINE_`` specify the position, where the expression
containing this variables is defined, while the variables ``_FILE_`` and
``_LINE_`` refer to the position in the processed file, from where the diverted
construct was called (and where the result of the evaluation will be inserted
later). For example, the input ::

  #:def macro()
  IN MACRO: _THIS_LINE_=${_THIS_LINE_}$, _LINE_=${_LINE_}$
  #:enddef macro

  GLOBAL: _THIS_LINE_=${_THIS_LINE_}$, _LINE_=${_LINE_}$ | ${macro()}$

yields after being processed by Fypp::

  GLOBAL: _THIS_LINE_=5, _LINE_=5 | IN MACRO: _THIS_LINE_=2, _LINE_=5    


Functions
---------

Following predefined functions are available:

* ``defined(VARNAME)``: Returns ``True`` if a variable with a given name has
  been already defined. The variable name must be provided as string::

    #:if defined('WITH_MPI')

* ``getvar(VARNAME, DEFAULTVALUE)``: Returns the value of a variable or a
  default value if the variable is not defined. The variable name must be
  provided as string::

    #:if getvar('DEBUG', 0)

* ``setvar(VARNAME, VALUE)``: Sets a variable to given value. It is identical to
  the ``#:set`` control directive. The variable name must be provided as
  string::

    $:setvar('i', 12)
    print *, "VAR I: ${i}$"

  If the left hand side of the assignment is a tuple of variables, the
  corresponding Python string representation of the tuple should be used as
  variable name::

    $:setvar('i, j', (1, 2))
    print *, "VAR I: ${i}$, VAR J: ${j}$"

* ``delvar(VARNAME)``: Removes a variable or a macro definition from the local
  scope. It is identical to the ``#:del`` control directive. The variable name
  must be provided as string::
    
    $:delvar('i')

  Analogous to the ``setvar`` function, also variable tuples can be deleted::

    $:delvar('i, j')



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
  
For backwards compatibility reason, also a `setvar` directive is recognized by
Fypp. It has identical syntax and functionality to the `set` directive, but the
equal sign between variable and value must be omitted. Its usage is not
recommended, as it may become obsolated in the future.


`del` directive
==================

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

If a variable is passed to the ``del`` directive, which is not defined in the
current scope, it will be simply ignored. So the example above would not trigger
any errors, if the variables ``X`` and ``Y`` were not defined before.

The `del` directive can also be used to delete macro defintions::

  #:def echo(TXT)
  ${TXT}$
  #:enddef
  @:echo HELLO
  #:del echo
  #! Following line throws an error as macro echo is not available any more
  @:echo HELLO

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
regular Python callable, which returns the rendered content of the macro body
when called. The macro arguments are converted to local variables containing the
actual arguments as values. The macro can be either called from within an
eval-directive, via the `call` control directive or its abreviated form, the
direct call.

Given the macro definition ::

  #:def assertTrue(cond)
  #:if DEBUG > 0
  if (.not. (${cond}$)) then
    print *, "Assert failed!"
    error stop
  end if
  #:endif
  #:enddef

the following three calls ::

  $:assertTrue('x > y')

  #:call assertTrue
  x > y
  #:endcall assertTrue

  @:assertTrue x > y

would all yield ::

  if (.not. (x > y)) then
    print *, "Assert failed!"
    error stop
  end if

if the variable `DEBUG` had a value greater than zero or an empty string
otherwise.

When called from within an eval-directive, arbitrary optional parameters can be
passed additional to the regular macro arguments. The optional parameters are
converted to local variables when the macro content is rendered. For example
given the defintion of the ``assertTrue()`` macro from above, the call ::

  $:assertTrue('x > y', DEBUG=1)

would override the global value of the `DEBUG` variable within the macro.

It is possible to declare default values for the positional arguments of a
macro. If for a given positional argument such a value is provided, then default
values must be provided for all following arguments as well. When the macro is
called, missing positional arguments will be replaced by their default value::

  #:def macro(X, Y=2, Z=3)
  X=${X}$, Y=${Y}$, Z=${Z}$
  #:enddef

  $:macro(1)   #! Returns "X=1, Y=2, Z=3"

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
  
  #:def assertTrue(cond)
    #:if DEBUG > 0
      if (.not. (${cond}$)) then
        print *, "Assert failed!"
        error stop
      end if
    #:endif
  #:enddef assertTrue


The `def` directive can also be used in its short form::

  #{def l2(x)}#log(log(${x}$))#{enddef}#

.. warning:: The content of macros is usually inserted via an eval directive and
     is accordingly subject to eventual line folding. Macros should,
     therefore, not contain any inline Fortran comments. (Comments
     starting at the beginning of the line preceeded by optional
     whitespaces only are OK, though). Use preprocessor comments
     (``#!``) instead.


`call` directive
================

When a Python callable (regular Python function, macro etc.) with at least one
argument is called with string argument(s) only (e.g. source code), it can be
called using the `call` directive to avoid extra quoting of the arguments::

  #:def debug_code(code)
    #:if DEBUG > 0
      $:code
    #:endif
  #:enddef debug_code

  #:call debug_code
    if (a < b) then
      print *, "DEBUG: a is less than b"
    end if
  #:endcall

The `call` directive takes the callable as argument. The lines between the
opening and closing directives will be rendered and then passed as Python string
argument to the callable. The name of the callable can be repeated in the
`endcall` directive for enhanced readability::

  #:call debug_code
    if (a < b) then
      print *, "DEBUG: a (${a}$) is less than b (${b}$)"
    end if
  #:endcall debug_code

If the callable has more than one arguments, the `nextarg` directive can be used
to separate the arguments from each other::

  #:def choose_code(code_debug, code_nondebug)
    #:if DEBUG > 0
      $:code_debug
    #:else
      $:code_nondebug
    #:endif
  #:enddef choose_code

  #:call chose_code
    if (a < b) then
        print *, "DEBUG: a is less than b"
    end if
  #:nextarg
    print *, "No debugging"
  #:endcall choose_code

The lines in the body of the `call` directive may contain directives
themselves. However, any variable defined within the body of the `call`
directive will be a local variable existing only during the evaluation of that
branch of the directive (and not being available when the callable is called
with the evaluated text as argument).

The `call` directive can also be used in its inline form. As this easily leads
to code being hard to read, it should be usually avoided::

  ! Rather ugly
  print *, #{call choose_code}# a(:) #{nextarg}# size(a) #{endcall}#

  ! This form is more readable
  print *, ${choose_code('a(:)', 'size(a)')}$

If the arguments are short, the more compact direct call directive can be also
used as an alternative to the line form (see next section).

The callables are not restricted to macros only, but can be arbitrary Python
expressions, which are either directly callables or after evaluation yield a
callable. Using the `lambda` construct of Python, such callables can be easily
generated during preprocessing. The following example shows how to create a
callable, which converts its argument to lower case::

  #:call lambda s: s.lower()
  THIS WILL BE CONVERTED TO LOWERCASE
  #:endcall

Alternatively, callable-generators can be defined in initialization files, as
demonstrated in the following example. Consider a Python file (``caseconv.py``),
which contains a case converter object. When an instance of it is called, it
converts the passed text to lower or upper case, depending on the flag passed at
initialization::

  class CaseConverter:

      def __init__(self, case):
          self._lower = (case == 'l')

      def __call__(self, txt):
          if self._lower:
              return txt.lower()
          else:
              return txt.upper()

Instances of ``CaseConverter`` can be created on the fly in the `call` directive
according to the needs (``example.fypp``)::

  #:call CaseConverter('l')
  THIS WILL BE CONVERTED TO LOWERCASE
  #:endcall CaseConverter

  #:call CaseConverter('u')
  this will be converted to uppercase
  #:endcall CaseConverter

To run this example, the Python file with the defintion of ``CaseConverter``
must be passed to the preprocessor as initialization file::

  fypp -i caseconv.py example.fypp

If the header of the `call` directive contains a name of a callable or a simple
Python call of the form ``callable(...)``, the name of the callable can be
repeated in the `endcall` directive, but not its arguments (see the example
above). If the `call` directive contains a more complicated Python expression,
the `endcall` directive must not contain any name (see the example with
``lambda``-function above). In those cases, however, it is recommended to use
temporary variables for better readability::

  #:set lower = lambda s: s.lower()

  #:call lower
  THIS WILL BE CONVERTED TO LOWERCASE
  #:endcall lower


Direct call directive
=====================

In order to enable compact (single line) calls while still maintaining code
readability, the `call` directive has an alternative form, the direct call
directive::

  #:def assertTrue(cond)
  #:if DEBUG > 0
  if (.not. (${cond}$)) then
    print *, "Assert failed!"
    error stop
  end if
  #:endif
  #:enddef assertTrue

  @:assertTrue size(aa) >= size(bb)

The direct call directive starts with ``@:`` followed by the name of a Python
callable. Everything between the callable name and the end of the line is
treated as argument to the callable. (Similar to the `call` directive, the
callable must have at least one argument.) When the callable needs more than one
argument, the arguments must be separated by the character sequence ``@@``::

  #:def assertEqual(lhs, rhs)
  if (${lhs}$ /= ${rhs}$) then
    print *, "assertEqual failed (${lhs}$ /= ${rhs}$)!"
    error stop
  end if
  #:enddef assertEqual

  @:assertEqual size(coords, dim=2) @@ size(types)

The direct call directive can contain continuation lines::

  @:assertEqual size(coords, dim=2) &
      & @@ size(types)

The arguments are parsed for further directives, so the inline form of the
eval and control directives can be used::

  #:set MYSIZE = 2
  @:assertEqual size(coords, dim=2) @@ ${MYSIZE}$

The direct call directive needs the name of an existing callable and does not
allow for on the fly callable-generation. However, it is possible to store the
result of the callable-generation in a temporary variable first, and call the
variable content with the direct call directive later. The example from the end
of the last section could be realized as follows::

  #:set lower = CaseConverter('l')
  #:set upper = CaseConverter('u')

  @:lower THIS WILL BE CONVERTED TO LOWERCASE
  @:upper this will be converted to uppercase
  
  

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


Line numbering directives
=========================

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


Scopes
======

Fypp uses a scope concept very similar to Pythons one. There is one global scope
(like in Python modules), and temporary local scopes may be created in special
cases (e.g. during macro calls).

The global scope is the one, which Fypp normaly uses for defining objects. All
imports specified on the command line are carried out in this scope. Also, all
the initialization files are executed within that scope. And all definitions
made by the `set` and `def` directives in the processed source file defines
entities in that scope, unless they appear within a `call` or a `def` directive.

Addtional temporary local scopes are opened, whenever

* a macro defined by the `def` directive is called, or

* the body of the `call` directive is evaluated in order to render the text,
  which will be passed to the callable as argument.

Any entity defined in a local scope is only visible within that scope and is
unaccessible once the scope has been closed. For example the code snippet::

  #:call lambda s: s.upper()
  #:set NUMBER = 9
  here is the number ${NUMBER}$
  #:endcall
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

  #:set X = 1
  #:call lambda s: s.upper()
  #:set X = 2
  value ${X}$
  #:endcall
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
  
  #:call lambda s: s.upper()
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
  #:def ensure(cond)
    #:if DEBUG
  if (.not. (${cond}$)) then
    write(*,*) 'Run-time check failed'
    write(*,*) 'Condition: ${cond.replace("'", "''")}$'
    write(*,*) 'File: ${_FILE_}$'
    write(*,*) 'Line: ', ${_LINE_}$
    stop
  end if
    #:endif
  #:enddef ensure
  
  
  #! Includes code if in debug mode.
  #:def debug_code(code)
    #:if DEBUG
  $:code
    #:endif
  #:enddef debug_code
  
  #:endmute

Remarks:

* All macro defintions are within a ``#:mute`` -- ``#:endmute`` pair in order to
  prevent the appearence of disturbing empty lines (the lines between the macro
  definitions) in the file which includes ``checks.fypp``.

* The preprocessor variable ``DEBUG`` will determine, whether the checks
  and the debug code is left in the preprocessed code or not.

* As the name ``assert`` is a reserved Python keyword, we call our run-time
  checker macro ``ensure`` instead. Additionally, we define a ``debug_code``
  macro. The content of both, ``ensure`` and ``debug_code``, are only included
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
  
      @:ensure ind > 0
      @:ensure uplo == 'U' .or. uplo == 'L'
  
      ! Do something useful here
      ! :
  
    #:call debug_code
      print *, 'We are in debug mode'
      print *, 'The value of ind is', ind
    #:endcall debug_code
  
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
framework is demonstrated below (thanks to Jacopo Chevallard for providing this
example)::

  ### Pre-process: .fpp -> .f90 via Fypp

  # Find all *.fpp files
  FILE(GLOB fppFiles RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/*.fpp")

  # Pre-process
  FOREACH(infileName ${fppFiles})

      # Generate output file name
      STRING(REGEX REPLACE ".fpp\$" ".f90" outfileName "${infileName}")

      # Create the full path for the new file
      SET(outfile "${CMAKE_CURRENT_BINARY_DIR}/${outfileName}")

      # Generate input file name
      SET(infile "${CMAKE_CURRENT_SOURCE_DIR}/${infileName}")

      # Custom command to do the processing
      ADD_CUSTOM_COMMAND(
          OUTPUT "${outfile}"
          COMMAND fypp "${infile}" "${outfile}"
          MAIN_DEPENDENCY "${infile}"
          VERBATIM
          )

      # Finally add output file to a list
      SET(outFiles ${outFiles} "${outfile}")

  ENDFOREACH(infileName)


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


Parser
======

.. autoclass:: Parser
   :members:


Builder
=======

.. autoclass:: Builder
   :members:


Renderer
========

.. autoclass:: Renderer
   :members:


Evaluator
=========

.. autoclass:: Evaluator
   :members:


Processor
=========

.. autoclass:: Processor
   :members:


FortranLineFolder
=================

.. autoclass:: FortranLineFolder
   :members:
   :special-members: __call__


*****
Notes
*****

.. [#] I am indebted to pyratemps author Roland Koebler for helpful discussions.
