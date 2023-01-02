#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(dirname $0)
cd $script_dir/..

# TODO:
# image on last page

sh scripts/ebook/1.sh
sh scripts/ebook/2.sh
python3 scripts/ebook/3.py
python3 scripts/ebook/4.py
sh scripts/ebook/5.sh
python3 scripts/ebook/6.py
sh scripts/ebook/7.sh
