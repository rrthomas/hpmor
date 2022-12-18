#!/usr/bin/env python3
# by Torben Menke https://entorb.net
"""
Modify flattened .tex file.
"""
import datetime as dt
import os
import re
import sys

os.chdir(os.path.dirname(sys.argv[0]) + "/../..")

source_file = "tmp/hpmor-epub-2-flatten.tex"
target_file = "tmp/hpmor-epub-3-flatten-mod.tex"

print("=== 3. modify flattened file ===")


with open(source_file, encoding="utf-8", newline="\n") as fhIn:
    cont = fhIn.read()

# \today
date_str = dt.date.today().strftime("%d.%m.%Y")
cont = cont.replace("\\today{}", date_str)

# writtenNote env -> \writtenNoteA
cont = re.sub(
    r"\s*\\begin\{writtenNote\}\s*(.*?)\s*\\end\{writtenNote\}",
    r"\\writtenNoteA{\1}",
    cont,
    flags=re.DOTALL,
)

# fix chapterOpeningAuthorNote
cont = re.sub(
    r"(\\begin\{chapterOpeningAuthorNote\}\n)(.*?\n)(\\end\{chapterOpeningAuthorNote\}\n)",
    r"\1E.~Y.:~\2\\newline\\rule[1ex]{\\textwidth}{.1pt}\\newline%\n\3",
    cont,
    flags=re.DOTALL,
)

# some cleanup
cont = cont.replace("\\hplettrineextrapara", "")

# additional linebreaks in verses of chapter 64
cont = cont.replace("\\\\\n\n", "\n\n")

# manual pagebreaks
cont = re.sub(r"\\clearpage(\{\}|)\n?", "", cont)

# \vskip 1\baselineskip plus .5\textheight minus 1\baselineskip
cont = re.sub(r"\\vskip .*\\baselineskip", "", cont)

# remove \settowidth{\versewidth}... \begin{verse}[\versewidth]
cont = re.sub(
    r"\n[^\n]*?\\settowidth\{\\versewidth\}[^\n]*?\n(\\begin\{verse\}\[\\versewidth\])",
    r"\n\\begin{verse}",
    cont,
)

# remove \settowidth
cont = re.sub(
    r"\\settowidth\{[^\}]*\}\{([^\}]*)\}",
    r"\1",
    cont,
    flags=re.DOTALL,
)

# remove \multicolumn
# \multicolumn{2}{c}{\scshape \uppercase{Schöne Unterwäsche}}\\
cont = re.sub(
    r"\\multicolumn\{[^\}]*\}\{[^\}]*\}\{(.*?)\}(\\\\|\n)",
    r"\1\2",
    cont,
    # flags=re.DOTALL,
)

# fix „ at start of chapter
# \lettrine[ante=„] -> „\lettrine
# \lettrinepara[ante=„] -> „\lettrine
cont = re.sub(
    r"\\(lettrine|lettrinepara)\[ante=(.)\]",
    r"\2\\lettrine",
    cont,
)

# align*
cont = cont.replace("\\begin{align*}", "")
cont = cont.replace("\\end{align*}", "")
cont = cont.replace("}&\\hbox{", "}\\hbox{")

# OMakeIV sections
# \OmakeIVsection{My Little Pony: Friendship is Science}
cont = re.sub(r"\\OmakeIVsection(\[[^\]]*\]|)\{(.*)\}\n+", r"\\section{\2}\n", cont)

cont = re.sub(
    r"\\OmakeIVspecialsection[^\n]+\{RingBearer\}.*?\n\n",
    r"\\section{Lord of the Rationality}\n",
    cont,
    flags=re.DOTALL,
)
cont = re.sub(
    r"\\OmakeIVspecialsection[^\n]+\{NarniaBLL\}.*?\n\n",
    r"\\section{The Witch and the Wardrobe}\n",
    cont,
    flags=re.DOTALL,
)
cont = re.sub(
    r"\\OmakeIVspecialsection[^\n]+\{Thundercats\}.*?\n\n",
    r"\\section{ThunderSmarts}\n",
    cont,
    flags=re.DOTALL,
)

cont = re.sub(
    r"\\OmakeIVspecialsection[^\n]+\{Twilight\}.*?\n\n",
    r"\\section{Utilitarian Twilight}\n",
    cont,
    flags=re.DOTALL,
)

with open(target_file, mode="w", encoding="utf-8", newline="\n") as fhOut:
    fhOut.write(cont)
