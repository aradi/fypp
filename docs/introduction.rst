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
<http://www.simple-is-better.org/template/pyratemp.html>`_ templating engine.
Although it shares many concepts with pyratemp, it was written from scratch
focusing on the special needs when preprocessing source code. Fypp natively
supports the output of line numbering markers, which are used by many compilers
to generate compiler messages with correct line numbers. Unlike most
cpp/fpp-like preprocessors or the coco preprocessor, Fypp also supports
iterations, multiline macros, continuation lines in preprocessor directives and
automatic line folding. It generally tries to extend the modern Fortran language
with metaprogramming capabilities without tempting you to use it for tasks which
could/should be done in Fortran itself.

The project is `hosted on github <https://github.com/aradi/fypp>`_ with
documentation available on `readthedocs.org
<http://fypp.readthedocs.org>`_. Fypp is released under the *BSD 2-clause
license*.

This document describes Fypp Version 3.2.


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

* Easily check macro parameter validity::

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
