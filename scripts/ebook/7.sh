#!/bin/sh

# based on work by yeKcim
# https://github.com/yeKcim/hpmor/tree/master/ebook

echo === 7. HTML -\> epub,mobi, doc ===

script_dir=$(cd $(dirname $0) && pwd)
cd $script_dir/../..

source_file="hpmor.html"
target_file="hpmor.epub"

# echo ==== 7.1a pandoc: html -\> epub====
# version 1. trying pandoc
# pandoc --standalone --from=html $source_file -o $target_file --epub-cover-image="ebook/tmp/title.jpg" --epub-chapter-level=2 --epub-embed-font="fonts/automobile_contest/Automobile Contest.ttf" --epub-embed-font="fonts/graphe/Graphe_Alpha_alt.ttf" --epub-embed-font="fonts/Parseltongue/Parseltongue.ttf" --epub-embed-font="fonts/graphe/Graphe_Alpha_alt.ttf" --epub-embed-font="fonts/gabriele_bad_ah/gabriele-bad.ttf" -c "./ebook/pandoc.css"

echo ==== 7.1b calibre: html -\> epub ====
# calibre is a bit better in ebook generation than pandoc and the result can be converted to mobi and docx
ebook-convert $source_file $target_file --language de-DE --no-default-epub-cover --cover "tmp/title.jpg" --book-producer "Torben Menke" --level1-toc "//h:h1" --level2-toc "//h:h2" --level3-toc "//h:h3"

source_file="hpmor.epub"
echo ==== 7.2 calibre: epub -\> mobi ====
# note: fonts are not included for some strange reason, so not using special fonts for headlines, writtenNotes and McGonagallWhiteBoard any more in html.css
target_file="hpmor.mobi"
ebook-convert $source_file $target_file

# echo ==== 7.3 epub -\> docx ====
# target_file="hpmor.docx"
# ebook-convert $source_file $target_file
# # pandoc --standalone $source_file -o $target_file

echo ==== 7.4 epub -\> fb2 ====
target_file="hpmor.fb2"
# ebook-convert does not support fb2
pandoc --standalone $source_file -o $target_file
