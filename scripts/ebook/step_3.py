#!/usr/bin/env python3
# by Torben Menke https://entorb.net

"""
Modify flattened .tex file.
"""

import datetime as dt
import os
import re
from pathlib import Path

os.chdir(Path(__file__).parent.parent.parent)

source_file = Path("tmp/hpmor-epub-2-flatten.tex")
target_file = Path("tmp/hpmor-epub-3-flatten-mod.tex")

if __name__ == "__main__":
    print("=== 3. modify flattened file ===")

    with source_file.open(encoding="utf-8", newline="\n") as fh_in:
        cont = fh_in.read()

    # \today
    date_str = dt.datetime.now(dt.UTC).date().strftime("%d.%m.%Y")
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
    cont = cont.replace("\\hplettrineextrapara\n", "")

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

    # fix „ at start of chapter
    # \lettrine[ante=„] -> „\lettrine
    # \lettrinepara[ante=„] -> „\lettrine
    cont = re.sub(
        r"\\(lettrine|lettrinepara)\[ante=(.)\]",
        r"\2\\lettrine",
        cont,
    )

    # OMakeIV sections
    # \OmakeIVsection{My Little Pony: Friendship is Science}
    cont = re.sub(r"\\OmakeIVsection(\[[^\]]*\]|)\{(.*)\}\n+", r"\\section{\2}\n", cont)

    cont = re.sub(
        r"\\OmakeIVspecialsection[^\n]+\{RingBearer\}.*?\n\n",
        r"\\section{Lord of the Rationality}\n",
        cont,
        flags=re.DOTALL,
        count=1,
    )
    cont = re.sub(
        r"\\OmakeIVspecialsection[^\n]+\{NarniaBLL\}.*?\n\n",
        r"\\section{The Witch and the Wardrobe}\n",
        cont,
        flags=re.DOTALL,
        count=1,
    )
    cont = re.sub(
        r"\\OmakeIVspecialsection[^\n]+\{Thundercats\}.*?\n\n",
        r"\\section{ThunderSmarts}\n",
        cont,
        flags=re.DOTALL,
        count=1,
    )

    cont = re.sub(
        r"\\OmakeIVspecialsection[^\n]+\{Twilight\}.*?\n\n",
        r"\\section{Utilitarian Twilight}\n",
        cont,
        flags=re.DOTALL,
        count=1,
    )

    # \censor
    cont = re.sub(r"\\censor\{.*?\}", r"xxxxxx", cont)

    # # remove Deathly_Hallows_Sign.pdf and other pdf images
    # # \includegraphics[scale=0.125]{images/Deathly_Hallows_Sign.pdf}
    # cont = re.sub(
    #     # r"\\includegraphics.*?\{images/Deathly_Hallows_Sign.*?\}",
    #     r"\\includegraphics.*?\.pdf\}",
    #     "",
    #     cont,
    # )

    # remove all images
    cont = re.sub(
        r"\\includegraphics\[.*?\]\{.*?\}",
        "",
        cont,
        flags=re.DOTALL,
    )

    # remove empty envs
    cont = re.sub(
        r"\\begin\{([^\}]*)\}\s*\\end\{\1}",
        "",
        cont,
        flags=re.DOTALL,
    )

    # remove end stuff
    cont = re.sub(
        r"(.*)\\end\{chapterOpeningAuthorNote\}.*?\\end\{document\}",
        r"\1\\end{chapterOpeningAuthorNote}\n\\end{document}",
        cont,
        flags=re.DOTALL,
        count=1,
    )

    with target_file.open(mode="w", encoding="utf-8", newline="\n") as fh_out:
        fh_out.write(cont)
