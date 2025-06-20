***************
Getting started
***************

Installing
==========

Fypp needs a working Python 3 interpreter (Python 3.5 or above).

When you install Fypp, you obtain the command line tool ``fypp`` and the Python
module ``fypp.py``. Latter you can import if you want to access the
functionality of Fypp directly from within your Python scripts.


Installing via conda
--------------------

The last stable release of Fypp can be easily installed as conda package by
issuing ::

  conda install -c conda-forge fypp


Installing via pip
------------------

You can also use Pythons command line installer ``pip`` in order to download the
stable release from the `Fypp page on PyPI <http://pypi.python.org/pypi/fypp>`_
and install it on your system.

If you want to install Fypp into the module system of the active Python 3
interpreter (typically the case when you are using a Python virtual
environment), issue ::

  pip3 install fypp

Alternatively, you can install Fypp into the user space (under `~/.local`) with
::

  pip3 install --user fypp


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
