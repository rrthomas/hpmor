#!/bin/sh

cd ebook
./1_latex2html.py && ./2_html2epub.sh
