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

* All macro definitions are within a ``#:mute`` -- ``#:endmute`` pair in order to
  prevent the appearance of disturbing empty lines (the lines between the macro
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


