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
most cpp/fpp preprocessors or the coco preprocessor, Fypp also supports
iterations, multiline macros, continuation lines in preprocessor directives and
automatic line folding. It generally tries to extend the modern Fortran language
with some useful features without tempting you to use it for tasks which
could/should be done in Fortran itself.

The project is `hosted on bitbucket <http://bitbucket.org/aradi/fypp>`_ with
documentation available on `readthedocs.org
<http://fypp.readthedocs.org>`_. Fypp is released under the *BSD 2-clause
license*.

This document describes Fypp Version 1.0.


Features
========

Below you find a summary over Fypps main features. Each of them is described in
more detail in individual sections further down.

* Definition and evaluation of preprocessor variables::

    #:if DEBUG > 0
      print *, "Some debug information"
    #:endif

    #:setvar LOGLEVEL 2

* Macro defintions and macro calls (apart of minor syntax differences similar to
  scoped intelligent Fortran macros, which probably will once become part of the
  Fortran standard)::

    #:def assertTrue(cond)
    if (.not. ${cond}$) then
      print *, "Assert failed in file ${_FILE_}$, line ${_LINE_}$"
      error stop
    end if
    #:enddef

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
    #:for dtype in [ 'real', 'dreal', 'complex', 'dcomplex' ]
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

* Passing multiline string arguments to macros::

    #:def debug_code(code)
      #:if DEBUG > 0
        $:code
      #:endif
    #:enddef
    
    #:call debug_code
      if (size(array) > 100) then
        print *, "DEBUG: spuriously large array"
      end if
    #:endcall

* Preprocessor comments::

    #! This will not show up in the output
    #! Also the newline characters at the end of the lines will be suppressed

* Suppressing the preprocessor output in selected regions::

    #! Definitions are read, but no output (e.g. newlines) will be produced
    #:mute
    #:include "macrodefs.fypp"
    #:endmute
    

***************
Getting started
***************

Installing
==========

Fypp needs a working Python interpreter, either version 2.7 or version 3.2 or
above.

Automatic install
-----------------

You can use Pythons installer `pip` to install the last stable release of Fypp
on your system::

  pip install fypp

This installs the command line tool ``fypp`` as well as the Python module
``fypp``. Latter you can import if you want to access the functionality of Fypp
directly from within your Python scripts.


Manual install
--------------

Alternatively, you can download the source code from the `Fypp project website
<http://bitbucket.org/aradi/fypp>`_ ::

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


Testing
=======

You can test Fypp on your system by running ::

  ./test/runtests.sh

in its source tree. This will execute various unit tests to check whether Fypp
works as expected. If you want to run the tests with a specific Python
interpreter, you can specify it as argument to the script::

  ./test/runtests.sh python3.2


Running
=======

The Fypp command line tool reads a file, preprocesses it and writes it to
another file, so you would typically invoke it like::

  fypp source.F90 source.f90

which would process `source.F90` and write the result to `source.f90`.  If
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
whitespace characters only) and it goes until the end of the line. The inline
form can appear anywhere, but if the construct consists of several directives
(e.g. ``#{if ...}#`` and ``#{endif}#``), all of them must appear on the same
line. While both forms can be used at the same time, for a particular construct
they must be consistent, e.g. a directive opened as line directive can not be
closed with an inline directive and vica versa.

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

Starting whitespaces before line directives are also ignored, enabling you to
choose any indentation strategy you like for the directives::

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


Expression evaluation
=====================

Python expressions can occur either as part of control directives, like ::

  #:if DEBUG > 0
  #:for dtype in [ 'real(dp)', 'integer', 'logical' ]

or directly inserted into the code using eval directives. ::

  $:time.strftime('%Y-%m-%d')
  print *, "${time.strftime('%Y-%m-%d')}$"

Experssions are always evaluated by using Pythons ``eval()`` builtin and must
be, therefore, syntactically and semantically correct Python
expressions. Although, this may require some additional quotations as compared
to other preprocessor languages ::

  #:if defined('DEBUG')  #! The Python function defined() expects a string argument
  #:for dtype in [ 'real(dp)', 'integer', 'logical' ]  #! dtype runs over strings  

it enables consistent expressions with (hopefully) least surprises (once you
know, how to formulate the expression in Python, you exactly know, how to write
it for Fypp). Also, note, that variable names, macros etc. are in Python (and
therefore als for Fypp) case sensitive.

If you access a variable in an expression, it must have been defined (either via
command line options or via preprocessor directives) before. For example ::

  #:if DEBUG > 0

can only be evaluated, if the variable `DEBUG` had been already defined. 

Python expressions are evaluted in an isolated Python environment, which
contains a restricted set of Python built-in functions and a few predefined
variables and functions (see below). There are no modules loaded by default, and
for safety reasons, no modules can be loaded once the preprocessing has started.


Initializing the environment
----------------------------

If a Python module is needed during the preprocessing, it can be imported via
the command line option (``-m``) before the preprocessing starts::

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

When complex initialization is needed (e.g. user defined Python functions are
needed during preprocessing), initialization scripts can be specified via the
command line option ``-i``::

  fypp -i ini1.py -i ini2.py

The preprocessor executes the content of each initialization script in the
isolated environment via Pythons `exec()` command before processing any
input. If modules had been also specified via the ``-m`` option, they are
imported before the initialization scripts are executed.


Predefined variables and functions
----------------------------------

The isolated Python environment for the expression evaluation contains following
predefined read-only variables:

* ``_LINE_``: number of current line

* ``_FILE_``: name of curernt file ::

    print *, "This is line nr. ${_LINE_}$ in file '${_FILE_}$'"

* ``_DATE_``: current date in ISO format

* ``_TIME_``: current time::

    print *, "Rendering started ${_DATE_}$ ${_TIME_}$"

Additionally following predefined functions are provided:

* ``defined(VARNAME)``: Returns ``True`` if a variable with a given name has
  been already defined. The variable name must be provided as string::

    #:if defined('WITH_MPI')

* ``getvar(VARNAME, DEFAULTVALUE)``: Returns the value of a variable or a
  default value if the variable is not defined. The variable name must be
  provided as string::

    #:if getvar('DEBUG', 0)

* ``setvar(VARNAME, VALUE)``: Sets a variable to given value. It is identical to
  the ``#:setvar`` control directive. The variable name must be provided as
  string::

    $:setvar('i', 12)
    print *, "VAR I: ${i}$"
  

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


`setvar` directive
==================

The value of a variable can be set during the preprocessing via the `setvar`
directive. (Otherwise, variables can be also declared and defined via command
line options.) The first argument is the name of the variable (unquoted),
followed by an optional Python expression. If latter is not present, the
variable is set to `None`::

  #:setvar DEBUG
  #:setvar LOG 1
  #:setvar LOGLEVEL LOGLEVEL + 1

Note, that in the last example the variable `LOGLEVEL` must have been already
defined in advance.

The `setvar` directive can be also used in the inline form::

  #{setvar X 2}#print *, ${X}$


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

  #:setvar real_kinds [ 'sp', 'dp' ]

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

The `for` directive expects a loop variable and an iterable expression,
separated by the ``in`` keyword. The code within the `for` directive is outputed
for every iteration with the current value of the loop variable, which can be
inserted using eval directives. If the iterable consists of iterables
(e.g. tuples), usual indexing can be used to access their components, or a
variable tuple to unpack them directly in the loop header::

  #:setvar kinds_names [ ('sp', 'real'), ('dp', 'dreal') ]

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
  #:endcall

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

Scopes in general follow the Python convention: Within the macro, all variables
from the encompassing scope are available (as `DEBUG` in the example above), and
additionally those which were passed as arguments. If a variable is defined
within the macro, it will be only accessible within the macro. If a variable
with the same name already exists in the encompassing scope, it will be shadowed
by it for the time of the macro subsitution. For example preprocessing the code
snippet ::

  #:def macro(x)
  print *, "Local XY: ${x}$ ${y}$"
  #:setvar y -2
  print *, "Local XY: ${x}$ ${y}$"
  #:enddef

  #:setvar x 1
  #:setvar y 2
  print *, "Global XY: ${x}$ ${y}$"
  $:macro(-1)
  print *, "Global XY: ${x}$ ${y}$"
  
would result in ::

  print *, "Global XY: 1 2"
  print *, "Local XY: -1 2"
  print *, "Local XY: -1 -2"
  print *, "Global XY: 1 2"

  
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

When a Python callable (e.g. regular Python function, macro) is called with
string arguments only (e.g. source code), it can be called using the `call`
directive to avoid extra quoting of the arguments::

  #:def debug_code(code)
    #:if DEBUG > 0
      $:code
    #:endif
  #:enddef

  #:call debug_code
    if (a < b) then
      print *, "DEBUG: a is less than b"
    end if
  #:endcall

The `call` directive takes the name of the callable as argument. The lines
between the opening and closing directives will be rendered and then passed as
Python string argument to the callable. If the callable has more than one
arguments, the `nextarg` directive can be used to separate the arguments from
each other::

  #:def choose_code(code_debug, code_nondebug)
    #:if DEBUG > 0
      $:code_debug
    #:else
      $:code_nondebug
    #:endif
  #:enddef

  #:call chose_code
    if (a < b) then
        print *, "DEBUG: a is less than b"
    end if
  #:nextarg
    print *, "No debugging"
  #:endcall

The lines in the body of the `call` directive may contain directives
themselves. However, any variable defined within the body of the `call`
directive will be a local variable existing only during the evaluation of that
branch of the directive (and not being available during the call itself).

The `call` directive can also be used in its inline form. As this easily leads
to code being hard to read, it should be usually avoided::

  ! Rather ugly
  print *, #{call choose_code}# a(:) #{nextarg}# size(a) #{endcall}#
  
  ! This form is more readable
  print *, ${choose_code('a(:)', 'size(a)')}$



Direct call directive
=====================

In order to enable compact (single line) calls while still maintaining code
readability, the `call` directive has an alternative short form, the direct call
directive::

  #:def assertTrue(cond)
  #:if DEBUG > 0
  if (.not. (${cond}$)) then
    print *, "Assert failed!"
    error stop
  end if
  #:endif
  #:enddef

  @:assertTrue size(aa) >= size(bb)

The direct call directive starts with ``@:`` followed by the name of a Python
callable. Everything between the callable name and the end of the line is
treated as text and is passed as string argument to the callable. When the
callable needs more than one argument, the arguments must be separated by the
character sequence ``@@``::

  #:def assertEqual(lhs, rhs)
  if (lhs != rhs) then
    print *, "AssertEqual failed!"
    error stop
  end if
  #:enddef

  @:assertEqual size(coords, dim=2) @@ size(types)

The direct call directive can contain continuation lines::

  @:assertEqual size(coords, dim=2) &
      & @@ size(types)

Note, that in contrast to the `call` directive, the text within the direct call
directive is not parsed for any further directives, but is passed as plain
string to the callable.


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
  #:enddef
  
  #:endmute
  $:test('me')

The example above would only produce ::

  print *, "TEST: me"

as output without any newlines.

The `mute` directive does not have an inline form.


Comment directive
=================

Comment lines can be added by using the ``#!`` preprocessor directive. The
comment line (including the newlines at their end) will be ignored by the
prepropessor and not appear in the ouput::

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


.. warning:: Fypp is not aware of the Fortran semantics represented by the lines
             it folds.

Fypp applies the line folding rather mechanically (only considering the the
position of the whitespace characters). Lines containing eval directives and
lines within macro definitions should, therefore, not contain any Fortran style
comments (started by ``!``) *within* the line, as folding within the comment
would result in invalid Fortran code. For comments within such lines, Fypps
comment directive (``#!``) can be used instead::

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
  #:enddef


Escaping
========

If you want to prevent Fypp to interprete something as control or eval
directive, put a backslash (``\``) between the first and second delimiter
character. In case of inline directives, do it for the opening and the
closing delimiter as well::

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
(a.k.a. linemarkers) in its output. This can be enabled by using the command
line option ``-n``. Given a file ``test.F90`` with the content ::

  program test
  #:if defined('MPI')
  use mpi
  #:else
  use openmpi
  #:endif
  :
  end program test

the command ::

  fypp -n -DMPI test.F90

produces the output ::

  # 1 "test.F90"
  program test
  # 3 "test.F90"
    use mpi
  # 7 "test.F90"
  :
  end program test

If during compilation of this output an error occured in the line ``use mpi``
(e.g. the mpi module can not be found), the compiler would know that this line
corresponds to line number 3 in the original file ``test.F90`` and could emit an
according error message.

The line numbering directives can be fine tuned with the ``-N`` option, which
accepts following mode arguments:

* ``full`` (default): Line numbering directives are emitted whenever lines are
  removed from the original source file or extra lines are added to it.

* ``nocontlines``: Same as full, but line numbering directives are ommitted
  before continuation lines. (Some compilers, like the NAG Fortran compiler,
  have difficulties with line numbering directives before continuation lines).


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
