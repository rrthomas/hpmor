# Make a PDF and e-book release

PROJECT=hpmor

TAG := $(shell git describe --tags)
VERSION := $(shell echo $(TAG) | sed -e 's/^v//')
EBOOKS = $(PROJECT).epub $(PROJECT).mobi $(PROJECT).fb2
ZIPFILE = $(PROJECT)-$(VERSION).zip

all: ebooks pdf

.PHONY: all

clean:
	latexmk -C

.PHONY: clean

pdf:
	latexmk

ebooks: pdf
	sh scripts/make_ebooks.sh

zip: pdf ebooks
	rm -f $(ZIPFILE) && \
	zip $(ZIPFILE) *.pdf $(EBOOKS)
