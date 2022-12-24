#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd $(dirname $0) && pwd)
cd $script_dir/..

# latexmk hpmor

# latexmk hpmor-1
# latexmk hpmor-2
# latexmk hpmor-3
# latexmk hpmor-4
# latexmk hpmor-5
# latexmk hpmor-6

# make all
latexmk
