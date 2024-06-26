#!/bin/sh

# update apt list
sudo apt-get update --fix-missing

# pdf
sudo apt-get install texlive-xetex texlive-lang-greek latexmk

# ebook
sudo apt-get install pandoc calibre texlive-extra-utils imagemagick ghostscript
# texlive-extra-utils for latexpand
# imagemagick ghostscript : for pdf title page to image conversion
