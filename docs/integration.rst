***********************************
Integration into build environments
***********************************

Fypp can be integrated into build environments like any other preprocessor. If
your build environment is Python-based, you may consider to access its
functionality directly via its API instead of calling it as an external script
(see the :ref:`api-documentation`).


CMake
=====

One possible way of invoking the Fypp preprocessor within the CMake build
framework is demonstrated below (thanks to Jacopo Chevallard for providing the
very first version of this example)::

  ### Pre-process: .fpp -> .f90 via Fypp

  # Create a list of the files to be preprocessed
  set(fppFiles file1.fpp file2.fpp file3.fpp)

  # Pre-process
  foreach(infileName IN LISTS fppFiles)

      # Generate output file name
      string(REGEX REPLACE ".fpp\$" ".f90" outfileName "${infileName}")

      # Create the full path for the new file
      set(outfile "${CMAKE_CURRENT_BINARY_DIR}/${outfileName}")

      # Generate input file name
      set(infile "${CMAKE_CURRENT_SOURCE_DIR}/${infileName}")

      # Custom command to do the processing
      add_custom_command(
          OUTPUT "${outfile}"
          COMMAND fypp "${infile}" "${outfile}"
          MAIN_DEPENDENCY "${infile}"
          VERBATIM)

      # Finally add output file to a list
      set(outFiles ${outFiles} "${outfile}")

  endforeach(infileName)


Make
====

In traditional make based system you can define an appropriate preprocessor
rule in your ``Makefile``::

  .fpp.f90:
          fypp $(FYPPFLAGS) $< $@

or for GNU make::

  %.f90: %.fpp
          fypp $(FYPPFLAGS) $< $@


Waf
===

For the `waf` build system the Fypp source tree contains extension modules in
the folder ``tools/waf``. They use Fypps Python API, therefore, the ``fypp``
module must be accessible from Python. Using those waf modules, you can
formulate a Fypp preprocessed Fortran build like the example below::

  def options(opt):
      opt.load('compiler_fc')
      opt.load('fortran_fypp')

  def configure(conf):
      conf.load('compiler_fc')
      conf.load('fortran_fypp')

  def build(bld):
      sources = bld.path.ant_glob('*.fpp')
      bld(
          features='fypp fc fcprogram',
          source=sources,
          target='myprog'
      )

Check the documentation in the corresponding waf modules for further details.
