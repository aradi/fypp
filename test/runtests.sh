#!/bin/bash
testdir="$(dirname $0)"
if [ $# -gt 0 ]; then
  pythons=$*
else
  pythons="python"
fi
root=".."
if [ -z "$PYTHONPATH" ]; then
  export PYTHONPATH="$root/src"
else
  export PYTHONPATH="$root/src:$PYTHONPATH"
fi
cd $testdir
failed="0"
failing_pythons=""
for python in $pythons; do
  echo "Testing with interpreter '$python'"
  $python test_fypp.py
  exitcode=$?
  if [ $exitcode != 0 ]; then
    failed="$(($failed + 1))"
    if [ -z "$failing_pythons" ]; then
      failing_pythons=$python
    else
      failing_pythons="$failing_pythons, $python"
    fi
  fi
done
echo
if [ $failed -gt 0 ]; then
  echo "Failing test runs: $failed" >&2
  echo "Failing interpreter(s): $failing_pythons" >&2
  exit 1
else
  echo "All test runs finished successfully"
  exit 0
fi
