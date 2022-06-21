#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd `dirname $0` && pwd)
cd $script_dir/..

cd ebook
python3 ./1_latex2html.py && sh ./2_html2epub.sh
