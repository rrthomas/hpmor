#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(dirname $0)
cd $script_dir/..

# TODO:
# image on last page

sh scripts/ebook/step_1.sh
sh scripts/ebook/step_2.sh
python3 scripts/ebook/step_3.py
python3 scripts/ebook/step_4.py
sh scripts/ebook/step_5.sh
python3 scripts/ebook/step_6.py
sh scripts/ebook/step_7.sh
echo optionally run scripts/ebook/step_8.sh to compare HTML to latest release
