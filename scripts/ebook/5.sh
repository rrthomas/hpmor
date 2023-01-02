#!/bin/sh

# based on work by yeKcim
# https://github.com/yeKcim/hpmor/tree/master/ebook

echo === 5. LaTeX -\> HTML via pandoc ===

# ensure we are in the hpmor root dir
script_dir=$(dirname $0)
cd $script_dir/../..

source_file="tmp/hpmor-epub-4-flatten-parsel.tex"
target_file="tmp/hpmor-epub-5-html-unmod.html"

# extract title and author from hp-header.tex
title=$(grep "pdftitle=" layout/hp-header.tex | awk -F '[{}]' '{print $2}')
author=$(grep "pdfauthor=" layout/hp-header.tex | awk -F '[{}]' '{print $2}')

pandoc --standalone --from=latex+latex_macros $source_file -o $target_file --metadata title="$title" --metadata author="$author"
