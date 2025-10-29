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

Python expressions are evaluated in an isolated Python environment, which
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

* ``_SYSTEM_``: Name of the system Fypp runs on, as returned by Pythons
  ``platform.system()`` function (e.g. ``Linux``, ``Windows``, ``Darwin``, etc.)

* ``_MACHINE_``: Name of the current machine Fypp runs on, as returned by
  Pythons ``platform.machine()`` function (e.g. ``x86_64``)

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

Initial values for preprocessor variables can be set at startup using the
command-line options ``-D`` (``--define``), ``-E`` (``--define-eval``), or
``-S`` (``--define-str``). These options differ in how they interpret the
provided value and what default is used when the value is omitted.

When using the ``-E`` option, the value is evaluated as a Python expression. If
no value is provided, the variable is set to the Python singleton ``None``. For
example::

  fypp -EDEBUG=0 -EWITH_MPI

initializes the variable ``DEBUG`` with the integer ``0`` and ``WITH_MPI`` with
``None``.

Since values are evaluated as Python expressions, string literals must be
explicitly quoted. For example::

  fypp -EMYSTR=Hello

would attempt to assign the value of an existing variable ``Hello`` to
``MYSTR``, which results in an error if ``Hello`` is not defined. To assign the
string literal ``"Hello"``, proper quoting is required::

  fypp -EMYSTR="Hello"

In environments where outer quotes are automatically removed (such as shells or
some build systems), the quoting can become cumbersome. In such cases,
additional escaping or nested quoting may be necessary::

  fypp -EMYSTR='"Hello"'

To simplify this, Fypp provides the ``-S`` option. This option treats the value
as a plain string literal without evaluation. If no value is provided, the
variable is initialized to the empty string ``""``. Using this option, quoting
is not required, so the above example becomes::

  fypp -SMYSTR=Hello

Finally, the ``-D`` option, which is commonly used by build systems for
initializing preprocessor variables, is configurable. Its behavior is controlled
by the ``--define-mode`` option, which accepts two modes:

- ``eval`` (default): values are interpreted as Python expressions (like ``-E``)
- ``str``: values are treated as string literals (like ``-S``)

For example::

  fypp --define-mode=eval -DMYSTR="Hello"
  fypp --define-mode=str -DMYSTR=Hello

both assing the string ``"Hello"`` to ``MYSTR``.

Note: The ``--define-mode`` option controls the behavior of *all* ``-D``
options, but leaves the ``-S`` and ``-E`` options unaffected. The execution
order of the ``-D``, ``-S``, and ``-E`` options is well-defined, but not
guaranteed to remain consistent across versions. If your variable
initializations depend on the order (e.g., referencing a previously defined
variable in a later initialization expression), use only one type of definition
option consistently. The order of initializations within the same option type is
preserved.


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

The `del` directive can also be used to delete macro definitions::

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

The `for` directive expects a loop variable expression and an iterable
separated by the ``in`` keyword. The code within the `for` directive is outputed
for every iteration with the current value of the loop variable, which can be
inserted using eval directives. The loop variable expression must be either a
name or a list of names joined by comma (``,``). In the latter case, the
iterable must consist of iterable items (e.g. tuples), which will be then
unpacked into the loop variables. (The number of the loop variables and the
number of the components of each iterated item must be identical.)::

  #:set kinds = ['sp', 'dp']
  #:set names = ['real', 'dreal']
  #! create kinds_names as [('sp', 'real'), ('dp', 'dreal')]
  #:set kinds_names = list(zip(kinds, names))

  #! Access by indexing
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
of positional or keyword arguments (variadic macros) using the ``*`` and ``**``
argument prefixes. The corresponding arguments will contain the unprocessed
positional and keywords arguments as a list and a dictionary, respectively::

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

Macros can be invoked recursively. Together with the variadic arguments, this
enables the realization of variadic templates (similar to C++) [1]_::

  #:def horner(x, a, b, *args)
  #:set res = "({} * {} + ({}))".format(a, x, b)
  #:if len(args) > 0
    #:set res = horner(x, res, args[0], *args[1:])
  #:endif
    $:res
  #:enddef

Calling the ``horner`` macro with ::

  poly = @{horner(x, 2, -3, 4, -5, 6)}@

would result in the Horner scheme with the specified coefficients::

  poly = ((((2 * x + (-3)) * x + (4)) * x + (-5)) * x + (6))


Scopes
------

Scopes in general follow the Python convention: Within the macro, all variables
from the encompassing scope are available (as `DEBUG` in the example above), and
additionally those which were passed as arguments. If a variable is defined
within the macro, it will be only accessible within the macro. If a variable
with the same name already exists in the encompassing scope, it will be shadowed
by it for the time of the macro substitution. For example preprocessing the code
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
     starting at the beginning of the line preceded by optional
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
should be also preceded by a named `contains` or `nextarg` directive declared
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
callable and an opening parenthesis (``(``). Everything after that up to the
closing parenthesis (``)``) is passed as *string argument* to the callable. The
closing parenthesis may only be followed by whitespace characters.

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
files are included, as the resulting output would eventually contain a lot of
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


.. _stop-directive:

`stop` directive
================

The `stop` directive can be used to report an error and stop the preprocessor
before all input has been consumed. This can be useful in cases, where some
external conditions (e.g. user defined variables) do not meet certain
criteria. The directive expects a Python expression, which will be converted to
string and written to standard error. After writing the error message Fypp exits
immediately with a non-zero exit code (see :ref:`exit-codes`)::

    #! Stop the code if DEBUGLEVEL is not positive
    #:if DEBUGLEVEL < 0
      #:stop 'Wrong debug level {}!'.format(DEBUGLEVEL)
    #:endif

There is no inline form of the `stop` directive.


.. _assert-directive:

`assert` directive
==================

The `assert` directive is a short form for the combination of an `if` and a
`stop` directive. It evaluates a given expression and stops the code if the
boolean value of the result is `False`. This can be very convenient, if you want
to write robust macros containing argument correctness checking::

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
standard error and terminates immediately with a non-zero exit code (see
:ref:`exit-codes`).

There is no inline form of the `assert` directive.


Comment directive
=================

Comment lines can be added by using the ``#!`` preprocessor directive. The
comment line (including the newlines at their end) will be ignored by the
prepropessor and will not appear in the output::

    #! This will not show up in the output

There is no inline form of the comment directive.


.. [1] Many thanks to Ivan Pribec for pointing out the similarity to C++
       variadic templates and bringing up the Horner scheme as example.
