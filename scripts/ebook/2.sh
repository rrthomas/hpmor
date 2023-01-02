#!/bin/sh

# based on work by yeKcim
# https://github.com/yeKcim/hpmor/tree/master/ebook

echo === 2. flatten .tex files ===

# ensure we are in the hpmor root dir
script_dir=$(dirname $0)
cd $script_dir/../..

source_file="scripts/ebook/hpmor-ebook.tex"
target_file="tmp/hpmor-epub-2-flatten.tex"

# flatten the .tex files to one file
latexpand $source_file -o $target_file
