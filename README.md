# Harry Potter and the Methods Of Rationality

<https://github.com/rrthomas/hpmor>
Maintainer: Reuben Thomas <rrt@sc3d.org>

A LaTeX version of [the popular didactic fan-fiction](https://www.hpmor.com)
by Eliezer Yudkowsky, which can make e-books in PDF, ePub and Mobi formats,
and six PDF volumes that can be printed and bound. There are also dust
jackets for the printable volumes.

See [latest release](https://github.com/rrthomas/hpmor/releases/latest)
for PDF and e-book downloads.

TeXLive 2015 or later and git are required to build the book. (Note: the
book must be built from a git checkout.)

Note: the Omake Files chapters (11 and 64) have been moved to the end of the
single-file PDF. Those chapter numbers are omitted in the text, so chapter
10 is followed by chapter 12, for example. In the six-volume PDFs, all
chapters are renumbered to start from 1 at the start of a book, and there are
no appendices. Some epigraphs have been omitted but are in the source files
of the chapters.

## Files

* `hpmor.tex` - the main file
* `layout/hp-format.tex` - mostly sets up memoir
* `layout/hp-markup.tex` - logical markup commands used in the text
* `chapters/` - one file per chapter, included from `hpmor.tex` and the
  individual volumes `hpmor-N.tex`.
* `spelling-list.txt` - a list of words used to spell-check the book.
* `fonts/` - various fonts used
* `latexmkrc` - configures latexmk to run LaTeX to build the PDFs.
* `GNUMakefile` - contains targets to make a Zip of the PDFs and release
  them to GitHub. (Mostly of interest to project maintainers.) `make all`
  does the same as `latexmk` (see below), which may be useful for editor
  integration (e.g. Emacs).
* `scripts/ebook/` - e-book generation scripts

## Building the book(s)

If you do not want to install all requirements on your native system, you can run the build in a Docker container instead. See bottom of [Dockerfile](Dockerfile) for further info.

* `latexmk`: Build all PDFs. (If in doubt, just run this command and do
  something else for twenty minutes!)
* `make all`: Build a Zip of the PDFs.
* `latexmk hpmor`: Build the one-volume PDF `hpmor.pdf`
* `latexmk hpmor-N`: Build one of the six individual volumes
  `hpmor-1.pdf` to `hpmor-6.pdf`.
* `latexmk layout/hpmor-dust-jacket-N`: produce the dust jacket for Volume N,
  `hpmor-dust-jacket-N.pdf`. Note that this requires the corresponding
  volume, `hpmor-N.pdf`, to have been built first.
* `latexmk -c`: Remove files produced by building (except PDFs).
* `latexmk -C`: Remove files produced by building (including PDFs).

By default, the dust jackets assume 80gsm plain paper (this affects the
thickness of the book and hence the size of the dust jacket). This can be
configured in `layout/hp-paper-type.tex`; see `layout/papers.tex` for a
list of papers.

The exact sizes of dust jackets may vary; the current parameters were taken
from a commercial printer. They can be adjusted in `hp-dust-jacket.tex` as
desired.

Note that the back dust-flap is left for you to add your own text; edit
`layout/hp-dust-jacket.tex` and search for “PUT YOUR BACK DUST-FLAP TEXT HERE!”.
Make sure you remove the percent sign `%` at the start of the line, or your
text will not be printed. (This is a safety feature to make sure that if you
don’t change the text, the placeholder will not appear; instead, you’ll just
get a blank back flap.)

When producing a book with a dust jacket, you may well not want the front
cover as well. To suppress the front cover, use the following incantation:

`latexmk -norc -e '$options="nocover"' -r latexmkrc -g hpmor-1`

Of course, you can replace `hpmor-1` with any other volume, or leave it
out to generate all PDFs with no cover.

To build a single chapter, from the `chapters` directory use the command:

`latexmk -norc -e '$chapter="N"' -r ../latexmkrc -g hpmor-chapter-NNN`

Similarly, to build a single appendix or other non-chapter section, from the
top directory use the command:

`latexmk -norc -e '$chapterfile="FILENAME"' -r latexmkrc -g FILENAME`

## Contributing

Contributions are most welcome. These fall into the following categories:

1. Textual corrections (where the text differs from the online original
   unintentionally).
2. Textual improvements: fixing straight-up errors in the English (or
   deeper, the sense, story etc.), or “Britfixing”, i.e. replacing
   non-British usages.
3. Design and typography. Improvements to both the PDF and print versions of
   the books are encouraged. See the GitHub bug-tracker for known issues;
   also, search the sources for “FIXME”.
4. Translations. Translations are of course most welcome! A list of known
   translations and one or two hints are given below in the
   [next section](#translations).

For textual changes other than simple typo or language fixes, please
familiarise yourself with the style guide (below).

The preferred way to submit any improvement is as a GitHub pull request.
Textual corrections can also be submitted as issues in the issue tracker, or
by email to the maintainer.

For the GitHub URL, and email address of the maintainer, see above.

## Style guide

### Spelling

When spell-checking, use `spelling-list.txt` instead of your personal
dictionary, so the results are less dependent on your setup. (The system
dictionary can still of course vary from one setup to another.)

Words that are standard English or part of the Harry Potter universe, or are
otherwise of “global” relevance should be added to `spelling-list.txt`.
Exclamations (“Eeeehhhh”) and other one-offs should be added to the per-file
word lists. (There’s obviously something of a grey area in the middle, e.g.
one-off references to various real and fictional people.)

Emacs users benefit from a `.dir-locals.el` that automatically sets up
`spelling-list.txt` as the personal dictionary for all HPMOR files.

### Chapter headings

Chapters that aren’t part of a continuing series look like this:

`\chapter{The Fundamental Attribution Error}`

Chapters that are part of a continuing series look like one of these:

`\partchapter{Working in Groups}{I}`

`\namedpartchapter{Self-Actualization}{SA}{VIII}{The Sacred and the Mundane}`

The first is pretty simple; it’s just the title of the chapter followed by
which part it is.

The second looks like the title of the chapter, then the abbreviation for
the title of the chapter, then the part, then the title of the part.

### First sentences

Normally, a chapter starts like this:

`\lettrine{P}{adma} Patil had finished`

That creates the large initial letter.

If the first paragraph of the chapter is all italics, though, it looks like
this:

    \begin{em}\lettrine{T}{he} red jet of fire took Hannah full in the
    [...]
    blazing green spirals brought down their foe’s Shield Charm.\par\end{em}

### Sections

`\section{Final Aftermath:}`

### Miscellaneous

There are some other things relating to newspaper headlines and such; check
the chapters they appear in for the appropriate markup.

### Markup

These are macros defined in `layout/hp-markup.tex`. You should glance
through that file to see what commands are available, and use them instead
of direct markup; for example `\shout` rather than `\textsc`.

## Translations

To translate the book, it is recommended to fork this repository, and check
back from time to time for updates. Also, do open an issue or PR against
this file to add the translation!

It is recommended to use `polyglossia` (not `babel`).

### Known translations

Note: there are other translations of HPMOR; here are listed only
translations of this edition.

* [French](https://github.com/yeKcim/hpmor) (complete)
* [German](https://github.com/entorb/hpmor-de) (complete)
* [Esperanto](https://github.com/norwd/hpmor) (in progress)
  [![milestone details](https://img.shields.io/github/milestones/progress/norwd/hpmor/1?label=Chapters%20Completed)](https://github.com/norwd/hpmor/releases/tag/LaboroEnProgreso)

<!--  LocalWords:  hpmor tex hp txt latexmkrc latexmk GNUMakefile 80gsm '
 -->
<!--  LocalWords:  norc nocover N' NNN chapterfile FILENAME' Britfixing dir
 -->
<!--  LocalWords:  Eeeehhhh el partchapter namedpartchapter lettrine adma
 -->
<!--  LocalWords:  textsc
 -->
