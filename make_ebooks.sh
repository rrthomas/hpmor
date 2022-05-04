#!/bin/sh

cd ebook
python3 ./1_latex2html.py && sh ./2_html2epub.sh
