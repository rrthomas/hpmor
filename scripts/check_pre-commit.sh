#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(dirname $0)
cd $script_dir/..

pip3 install pre-commit
pre-commit run -a
