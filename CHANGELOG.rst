==========
Change Log
==========


Development
===========

Released: not released yet


Added
-----

* Change log file.


1.0
===

Released: 2016-04-05


Added
-----

* Optional suppression of line numbering in continuation lines.

* Optional creation of parent folders for output file.


Changed
-------

* Class Fypp independent of ArgumentParser.


Fixed
-----

* Fix false error, when include was within a directive.

* Wrong line number offset in eval directives.


0.12
====

Released: 2016-03-11


Added
-----

* Implement direct call.


Changed
-------

* Remove paranthesis from direct call.


0.11
====

Released: 2016-03-09


Added
-----

* Implement call directive.

* More precise error messages.

* Folding prevention for comment lines.

* Smart line folding, fixed format line folding.

* Python 2.7 compatibility.


Changed
-------

* Control directive prefix changed from ``@`` to ``#``.

* Rename function `default()` into `getvar()`.


Fixed
-----

* Superfluous trailing newlines in macro calls.


0.9
===

Released: 2016-02-22

Added
-----

* Basic functionality.
