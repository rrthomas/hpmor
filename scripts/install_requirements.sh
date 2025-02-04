#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(dirname $0)
cd $script_dir/..

# update apt list
sudo apt-get update --fix-missing

# pdf
sudo apt-get install texlive-xetex texlive-lang-greek latexmk

# ebook
sudo apt-get install pandoc calibre texlive-extra-utils imagemagick ghostscript
# texlive-extra-utils for latexpand
# imagemagick ghostscript : for pdf title page to image conversion

pip install -r python-requirements.txt
