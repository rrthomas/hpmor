#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd $(dirname $0) && pwd)
cd $script_dir/..

pip3 install pre-commit
pre-commit run -a
