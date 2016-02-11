#!/bin/bash
root="$(dirname $0)/.."
export PYTHONPATH="$root/src:$PYTHONPATH"
python3 -m unittest discover $root/test
