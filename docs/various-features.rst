****************
Various features
****************


Multiline directives
====================

The line form of the control and eval directives can span arbitrary number of
lines, if Fortran-style continuation characters are used::

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

For comments starting at the beginning of the line (preceded by optional
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

If you want to prevent Fypp to interpret something as a directive, put a
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

If during compilation of this output an error occurred in the line ``use mpi``
(e.g. the mpi module can not be found), the compiler would know that this line
corresponds to line number 3 in the original file ``test.fpp`` and could emit an
according error message.

The line numbering directives can be fine tuned with the ``-N`` option, which
accepts following mode arguments:

* ``full``: Line numbering directives are emitted whenever lines are
  removed from the original source file or extra lines are added to it.

* ``nocontlines``: Same as full, but line numbering directives are omitted
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


Rendering file names as relative paths
======================================

When the input file is specified as an absolute path (e.g. during an
out-of-source build), the variables ``_FILE_`` and ``_THIS_FILE_`` will also
contain absolute paths. This might result in file names, which are unnecessary
long and might reveal unwanted information about the directory structure on the
building host.

The ``--file-var-root`` option converts the paths in ``_FILE_`` and
``_THIS_FILE_`` to relative paths with respect to a specified root folder.
Given the file `source.fpp`::

  [...]
  call fatal_error("Error in ${_FILE_}$:${_LINE_}$")

invoking with Fypp with ::

  fypp /home/user/projectdir/src/source.fpp

results in ::

  [...]
  call fatal_error("Error in /home/user/projectdir/src/source.fpp:2")

while using the ``--file-var-root`` option ::

  fypp --file-var-root=/home/user/projectdir /home/user/projectdir/src/source.fpp

yields ::

  [...]
  call fatal_error("Error in src/source.fpp:2")


.. _exit-codes:

Exit codes
==========

When run as a standalone application, Fypp returns one of the following exit
codes to the calling environment:

* 0: Preprocessing finished successfully.

* 1: Stopped due to an unexpected error.

* 2: Explicitely requested stop encountered (:ref:`stop-directive` or
  :ref:`assert-directive`).



