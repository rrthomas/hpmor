#!/bin/sh

# by Torben Menke https://entorb.net

# run from within ebook dir via
# ./2_html2epub.sh

mkdir -p tmp

echo 1. extract titlepage from PDF
cp ../hpmor.pdf tmp/

# 1.2 extract title page from PDF and convert to jpeg
# 1.2a via imagemagick
# sudo apt install imagemagick
# convert -density 150 tmp/hpmor.pdf[0] -quality 75 tmp/title-en.jpg
# imagemagick complains:
# attempt to perform an operation not allowed by the security policy

# 1.2b via ghostscript
gs -dSAFER -r600 -sDEVICE=pngalpha -dFirstPage=1 -dLastPage=1 -o tmp/title-en.png tmp/hpmor.pdf
# now imagemagick can be used for converting to the proper size
convert -density 150 tmp/title-en.png -resize 1186x1186\> -quality 75 tmp/title-en.jpg

echo 2. convert html to epub
# use calibre instead of pandoc, as pandoc loses the css style
# see https://manual.calibre-ebook.com/generated/en/ebook-convert.html
# linux: sudo apt install calibre
# windows: obtain from https://calibre-ebook.com/download_windows
echo 2.1 calibre: html to epub
ebook-convert output/hpmor.html output/hpmor.epub --no-default-epub-cover --cover tmp/title-en.jpg --authors "Eliezer Yudkowsky" --title "Harry Potter and the Methods of Rationality" --book-producer "Torben Menke" --pubdate 2015-03-14 --language en-US

echo 2.2 calibre: epub to mobi
ebook-convert output/hpmor.epub output/hpmor.mobi
