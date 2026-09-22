#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(dirname "$0")
cd "$script_dir/.." || exit 1

latexmk -C
rm -rf tmp
