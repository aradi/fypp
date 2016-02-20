FYPP
====

FYPP is a Python powered Fortran preprocessor. It extends Fortran with
condititional compiling and template metaprogramming capabilities. It is written
in Python and uses Python to evaluate expressions in preprocessor commands,
enabling high flexibility in formulating metaprogramming tasks. It puts strong
emphasis on robustness and on neat integration into Fortran developing
toolchains.

Main features:

* Definition/evaluation of preprocessor variables.
* Macro definitions with more than one line of source code.
* Conditional output.
* Loop directives for generation of Fortran templates.
* File inclusion
* Insertion of arbitrary Python eval-expressions.
* Fortran-style continuation lines in preprocessor directives.
* Folding of preprocessed lines using continuation lines.

See the [DOCUMENTATION](http://fypp.readthedocs.org) for more detail.

FYPP is [hosted on Bitbucket](https://bitbucket.org/aradi/fypp) and released
under the BSD 2-Clause License.
