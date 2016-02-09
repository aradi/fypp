FYPP -- Python powered Fortran preprocessor
===========================================

FYPP is preprocessor for source files containing special directives. It is
specifically tailored for the Fortran programming language, offering
Fortran-friendly preprocessor directive syntax and features extending the
capabilities of usual CPP-like preprocessors. It allows great flexibility in
formulating preprocessor tasks by using Python for expression evaluation in
preprocessor directives.

Main features:

* Definition/evaluation of preprocessor variables.
* Macro definitions with more than one line of source code.
* Conditional compilation.
* Loop directives for rapid generation of Fortran templates.
* Insertion of arbitrary Python eval-expressions.
* Fortran-style continuation lines in preprocessor directives.
* Folding of preprocessed lines using continuation lines.

FYPP is released under the BSD 2-Clause License.
