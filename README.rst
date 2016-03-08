=============================================
Fypp — Python powered Fortran metaprogramming
=============================================

Fypp is a Python powered Fortran preprocessor. It extends Fortran with
condititional compiling and template metaprogramming capabilities. Instead of
introducing its own expression syntax, it uses Python expressions in its
preprocessor directives, offering the consistency and flexibility of Python when
formulating metaprogramming tasks. It puts strong emphasis on robustness and on
neat integration into Fortran developing toolchains.

The project is `hosted on bitbucket <http://bitbucket.org/aradi/fypp>`_.

`Detailed DOCUMENTATION <http://fypp.readthedocs.org>`_ is available on
`readthedocs.org <http://fypp.readthedocs.org>`_. 

Fypp is released under the *BSD 2-clause license*.


Main features
=============

* Definition and evaluation of preprocessor variables::

    #:if DEBUG > 0
      print *, "Some debug information"
    #:endif

    #:setvar LOGLEVEL 2

* Macro defintions and macro calls (apart of minor syntax differences similar
  to scoped intelligent Fortran macros, which probably will be once part of the
  Fortran standard)::

    #:def assertTrue(cond)
    if (.not. ${cond}$) then
      print *, "Assert failed in file ${_FILE_}$, line ${_LINE_}$"
      error stop
    end if
    #:enddef

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

* Iterated output::

    interface myfunc
    #:for dtype in [ 'real', 'dreal', 'complex', 'dcomplex' ]
      module procedure myfunc_${dtype}$
    #:endfor
    end interface myfunc

* Inline directives::

    logical, parameter :: hasMpi = #{if defined('MPI')}#.true.#{else}#.false.#{endif}#

* Insertion of arbitrary Python eval-expressions::

    character(*), parameter :: comp_date = "${time.strftime('%Y-%m-%d')}$"

* Inclusion of files during preprocessing::

    #:include "macrodefs.fypp"

* Using Fortran-style continutation lines in preprocessor directives::

    #:if var1 > var2 &
        & or var2 > var4
      print *, "Doing something here"
    #:endif

* Passing multiline arguments to macros::

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
    


Installing
==========

Fypp needs a working Python interpreter either with version 2.7 or with version
3.2 or above.

The command line tool is a single stand-alone script. You can run it directly
from the source folder ::
  
  FYPP_SOURCE_FOLDER/bin/fypp

or after copying it from the `bin` folder to any location listed in your `PATH`
environment variable, by just issuing ::

  fypp

Alternatively, you can use Pythons installer (`pip`) to install Fypp on your
system::

  pip install fypp

This installs the command line tool ``fypp`` as well as the Python module
``fypp``. Latter you can import if you want to access the functionality of Fypp
directly from within your Python scripts.



Running
=======

The Fypp command line tool reads a file, preprocesses it and writes it to
another file, so you would typically invoke it like::

  fypp source.fypp source.f90

which would process `source.fypp` and write the result to `source.f90`.  If
input and output files are not specified, information is read from stdin and
written to stdout.

The behavior of Fypp can be influenced with various command line options. A
summary of all command line options can be obtained by::

  fypp -h
