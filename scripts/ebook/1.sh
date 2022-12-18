#!/bin/sh

# based on work by yeKcim
# https://github.com/yeKcim/hpmor/tree/master/ebook

echo === 1. extract cover from PDF to image===

# ensure we are in the hpmor root dir
script_dir=$(cd $(dirname $0) && pwd)
cd $script_dir/../..

mkdir -p tmp/

source_file="hpmor.pdf"
target_file="tmp/title.png"

# extract title page from PDF and convert to jpeg
# V1 via imagemagick
# sudo apt install imagemagick
# convert -density 150 tmp/hpmor.pdf[0] -quality 75 tmp/title-en.jpg
# imagemagick complains:
# attempt to perform an operation not allowed by the security policy

# V2 via ghostscript
gs -dSAFER -r600 -sDEVICE=pngalpha -dFirstPage=1 -dLastPage=1 -o $target_file $source_file

# now imagemagick can be used for converting to the proper size
source_file="tmp/title.png"
target_file="tmp/title.jpg"
convert -density 150 $source_file -resize 1186x1186\> -quality 75 $target_file
