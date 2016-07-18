#!/usr/bin/env python
# encoding: utf-8
# Bálint Aradi, 2016

'''Uses Fypp as Fortran preprocessor (.F90 -> .f90). Use this one (instead of 
fypp_preprocessor) if you want to preprocess Fortran sources with Fypp.

You typically trigger the preprocessing via the 'fypp' feature::

	def options(opt):
		opt.load('compiler_c')
		opt.load('compiler_fc')
		opt.load('fortran_fypp')
	
	def configure(conf):
		conf.load('compiler_c')
		conf.load('compiler_fc')
		conf.load('fortran_fypp')
	
	
	def build(bld):
		sources = bld.path.ant_glob('*.F90')
		
		bld(
			features='fypp fc fcprogram',
			source=sources,
			target='myprog'
		)

Please check the documentation in the fypp_preprocessor module for the
description of the uselib variables which may be passed to the task generator.
'''

from waflib import TaskGen
import fypp_preprocessor


################################################################################
# Configure
################################################################################

def configure(conf):
	fypp_preprocessor.configure(conf)
	

################################################################################
# Build
################################################################################

class fortran_fypp(fypp_preprocessor.fypp_preprocessor):
		
	ext_in = [ '.F90' ]
	ext_out = [ '.f90' ]


@TaskGen.extension('.F90')
def fypp_preprocess_F90(self, node):
	'Preprocess the .F90 files with Fypp.'

	f90node = node.change_ext('.f90')
	self.create_task('fortran_fypp', node, [ f90node ])
	if 'fc' in self.features:
		self.source.append(f90node)
