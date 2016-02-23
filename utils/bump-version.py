#!/usr/bin/env python3
import sys
import re
import os

VERSION_PATTERN = r'\d+\.\d+(?:\.\d+)?'
FILES_PATTERNS = [ ('bin/fypp', 
                    r'^VERSION\s*=\s*([\'"]){}\1'.format(VERSION_PATTERN), 
                    "VERSION = '{}'"),
                   ('docs/index.rst',
                    r'^Version:[ ]*{}[ ]*$'.format(VERSION_PATTERN),
                    'Version: {}')
]

if len(sys.argv) < 2:
    print("Missing version string")
    sys.exit(1)
version = sys.argv[1]
match = re.match(VERSION_PATTERN, version)
if match is None:
    print("Invalid version string")
    sys.exit(1)

rootdir = os.path.join(os.path.dirname(sys.argv[0]), '..')
for fname, regexp, repl in FILES_PATTERNS:
    fname = os.path.join(rootdir, fname)
    print("Replacments in '{}': ".format(fname), end='')
    fp = open(fname, 'r')
    txt = fp.read()
    fp.close()
    newtxt, nsub = re.subn(regexp, repl.format(version), txt, 
                           flags=re.MULTILINE)
    print(nsub)
    fp = open(fname, 'w')
    fp.write(newtxt)
    fp.close()
