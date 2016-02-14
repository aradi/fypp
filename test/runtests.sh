#!/bin/bash
testdir="$(dirname $0)"
root="../"
export PYTHONPATH="$root/src:$PYTHONPATH"
cd $testdir
python3 -m unittest discover 
