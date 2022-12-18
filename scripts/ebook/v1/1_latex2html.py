#!/usr/bin/env python3
# by Torben Menke https://entorb.net
"""
Converter script.

reads latex code in ../chapters
converts to html
as preparation for conversion into epub format
output dir: output/

run from within ebook dir via
python3 1_latex2html.py
"""
import glob
import os
import re
import sys
from datetime import date

# Notes
# footnotes are converted to inline text
# these intro parts are skipped:
#  Based on the characters of J. K. ROWLING
#  CONTENT WARNINGS
# Omake chapters are included in-place, not at appendix

today = date.today()

# chdir to script dir
os.chdir(os.path.dirname(sys.argv[0]))

dir_tex_source = "../chapters/"
dir_tmp = "tmp"
dir_out = "output"
for my_dir in (dir_tmp, dir_out):
    os.makedirs(my_dir, exist_ok=True)


html_preamble = f"""
<h2>Preamble of this e-book</h2>
<p>The original version of this great book 'Harry Potter and the Methods of Rationality' by Eliezer Yudkowsky is:<br/>
<a href="https://www.hpmor.com">https://www.hpmor.com</a></p>
<p>This e-book is based on the typesetting and revised text from:<br/>
<a href="https://github.com/rrthomas/hpmor">https://github.com/rrthomas/hpmor</a></p>
<p>This e-book was created at: {today}</p>
<p>The latest version can be found at:<br/>
<a href="https://github.com/rrthomas/hpmor/releases/latest/">https://github.com/rrthomas/hpmor/releases/latest/</a></p>
<p>Source code of the converter script can be found at:<br/>
<a href="https://github.com/rrthomas/hpmor/ebook/">https://github.com/rrthomas/hpmor/ebook/</a></p>
"""

# <p>This book is not my work, I just converted the text into e-book formats.</p>
# <p>Have fun on your journey, <br/><i>Torben Menke</i></p>


css = """
div.letter {
    font-style: italic;
    margin-left: 1em;
}
div.verse {
    margin-left: 1em;
}
div.playdialog {
    text-indent: -1em;
    margin-left: 2em;
}
div.headlines {
}
div.center {
    text-align: center;
}
div.center_sc {
    text-align: center;
    font-variant: small-caps;
}
div.later {
    text-align: center;
}
div.emph {
    font-style: italic;
}
div.chapterOpeningAuthorNote {
    font-style: italic;
}
div.chapterOpeningQuote {
    font-style: italic;
}
span.abbrev{
    text-transform: lowercase;
    font-variant: small-caps;
}
span.prophesy{
    font-variant: small-caps;
}
span.scream{
    text-transform: uppercase;
}
span.shout{
    font-variant: small-caps;
}
span.parsel{
    font-style: italic;
}
span.headline_header{
}
span.headline{
    font-style: italic;
}
span.headline_label{
    font-variant: small-caps;
}
span.smallcaps{
    font-variant: small-caps;
}
span.uppercase{
    text-transform: uppercase;
}
"""

# inline instead, since easier for conversion to epub
# with open(f'output/hpmor-{lang}.css', mode='w',
#           encoding='utf-8', newline='\n') as fh:
#     fh.write(css)

html_start = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="author" content="Eliezer Yudkowsky" />
<title>Harry Potter and the Methods of Rationality</title>
<style>
{css}
</style>
</head>
<body>
"""
# <link rel='stylesheet' href='hpmor-{lang}.css'/>


html_end = """</body>\n</html>"""


counter_chapter = 0
# counter_footnotes = 0


def simplify_tex(s: str) -> str:
    # end of line: CRLF-> LF
    s = s.replace("\r\n", "\n")
    # remove Latex comments
    s = re.sub(r"(?<!\\)%.*\n", "\n", s)

    # commands to remove
    s = re.sub(
        r"\\lettrine\{(.)\}\{(.*?)\}",
        r"\1\2",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r"\\lettrine\[ante=(.+?)\]\{(.)\}\{(.*?)\}",
        r"\1\2\3",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r"\\lettrinepara\{(.)\}\{(.*?)\}",
        r"\1\2",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r"\\lettrinepara\[ante=(.+?)\]\{(.)\}\{(.*?)\}",
        r"\1\2\3",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # add linebreaks to \item and \begin
    s = re.sub(r"(?<!\n)\\(begin|end|item)\b", r"\n\\\1", s)

    # OmakeIVsection -> section
    s = re.sub(r"\\OmakeIVsection\[.*?\]\{", r"\\section{", s)
    s = s.replace("\\OmakeIVsection{", "\\section{")
    # \latersection -> section
    s = s.replace("\\latersection{", "\\section{")
    # OmakeIVspecialsection
    s = re.sub(
        r"\\makeatletter\n\\newcommand{\\OmakeIVspecialsection}.*?\\chapter{Omake Files IV, Alternate Parallels}",
        r"\\chapter{Omake Files IV, Alternate Parallels}\n",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # Lord of the Rationality
    s = re.sub(
        r"\\OmakeIVspecialsection.*?\\raisebox\{-.32ex\}\{Y\}\}",
        r"\\section{Lord of the Rationality}",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # The Witch and the Wardrobe
    s = s.replace(
        "\\OmakeIVspecialsection[5]{\\fontspec[ExternalLocation]{NarniaBLL}456}",
        "\\section{The Witch and the Wardrobe}",
    )
    # ThunderSmarts
    s = s.replace(
        "\\OmakeIVspecialsection[2]{\\fontspec[ExternalLocation]{Thundercats}ThunderSmarts}",
        "\\section{ThunderSmarts}",
    )
    # Utilitarian Twilight
    s = s.replace(
        "\\OmakeIVspecialsection{\\fontspec[ExternalLocation]{Twilight}Utilitarian Twilight\\protect\\footnotemark}",
        "\\section{Utilitarian Twilight}",
    )

    # remove multiple spaces
    s = re.sub(r"  +", r" ", s)
    return s


def tex2html(s: str) -> str:

    #
    # Bulk text replacements
    # Chapter 00 - Preface
    if "Author’s introduction" in s:
        s = re.sub(
            r"\\begin\{itemize\}(.*?)\\end\{itemize\}",
            r"<ul>\n\1\n</ul>",
            s,
            flags=re.DOTALL | re.IGNORECASE,
        )
        s = re.sub(
            r"\\item (.*)$",
            r"<li>\1</li>",
            s,
        )

    #
    # Transfiguration is not permanent! in Chapter 15
    s = re.sub(
        r"\\begin\{center\}(.+?Transfiguration is not permanent!.+?)\\end\{center\}",
        r'<div class="center">Transfiguration is not permanent!</div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    was = "{\n\\begin{center}\n\\includegraphics[scale=0.125]{images/Deathly_Hallows_Sign.pdf}\n\\end{center}\n}"
    s = s.replace(was, "")

    # paper notes in Chapter 13
    if "Asking the Wrong Questions" in s:
        # \begin{align*} -> writtenNote
        myMatches = re.finditer(
            r"\\begin\{align\*\}.+?\\end\{align\*\}",
            s,
            flags=re.DOTALL | re.IGNORECASE,
        )
        for myMatch in myMatches:
            was = myMatch.group(0)
            womit = was
            womit = womit.replace("align*", "writtenNote")
            womit = re.sub(r"\\hbox\{(.*?)\}", r"\1", womit)
            womit = re.sub(r"\\intertext\{(.*?)\}", r"\1<br/>", womit, flags=re.DOTALL)
            womit = re.sub(r"\\multicolumn\{2\}\{c\}\{(.*?)\}", r"\1", womit)
            womit = womit.replace("\\scshape", "")
            womit = womit.replace("\\centering", "")
            womit = womit.replace("&", "")
            womit = womit.replace("[1.5ex]", "")
            s = s.replace(was, womit)
        s = re.sub(
            r"\\begin\{center\}\s*\\scshape (\\MakeUppercase\{Warning\}.*?)\\end\{center\}",
            r"\\begin{writtenNote}\1\\end{writtenNote}",
            s,
            flags=re.DOTALL | re.IGNORECASE,
        )
        s = re.sub(
            r"\\begin\{center\}\s*\\scshape(\nAttempt failed.*?)\\end\{center\}",
            r"\\begin{writtenNote}\1\\end{writtenNote}",
            s,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # notes in chapter 22
    if "The Scientific Method" in s:
        s = re.sub(
            r"\\begin\{center\}\\itshape\n\{\\scshape (Observation:)\}(.*?)\\end\{center\}",
            r"\\begin{writtenNote}\\textsc{\1}\2\\end{writtenNote}",
            s,
            flags=re.DOTALL | re.IGNORECASE,
        )
        s = s.replace("{\\scshape Hypotheses:}", "\\textsc{Hypotheses:}")
        s = s.replace("{\\scshape Tests:}", "\\textsc{Tests:}")

    # notes in chapter 23
    if "Belief in Belief" in s:
        s = re.sub(
            r"\\begin\{centering\}\n\\begin\{samepage\}\n\\scshape (Observation:)(.*?)\\end\{centering\}",
            r"\\begin{writtenNote}\\textsc{\1}<br/>\2\\end{writtenNote}",
            s,
            flags=re.DOTALL | re.IGNORECASE,
        )
        s = re.sub(
            r"\n\\itshape (Wizardry isn’t as powerful now as it was when Hogwarts was founded.)\s*\\end\{samepage\}",
            r"\1",
            s,
        )
        s = s.replace("\\scshape Hypotheses:\n\n", "\\textsc{Hypotheses:}")
        s = s.replace("\\scshape Tests:", "\\textsc{Tests:}")
        s = s.replace("\\itshape\n", "")
        s = s.replace(r"{\scshape Result:}", "<br/>Result:")

    #
    # cleanup
    # commands to remove completely
    #
    # commands with empty parameters
    s = re.sub(r"\\(footnotemark|hyp|noindent)\{\}", "", s)
    # commands without parameters
    s = re.sub(
        r"\\(protect|footnotemark|authorsnotefootnotemark|clearpage|newpage|penalty-10|penalty\d*|noindent)\b",
        "",
        s,
    )
    # commands without parameters but followed by linebreaks
    s = re.sub(
        r"\\(hplettrineextrapara|savetrivseps|firmlist|footnotemark|restoretrivseps)\n",
        r"",
        s,
    )

    # vspace*{...}
    s = re.sub(r"\\(vspace)\*\{.*?\}\n?", r"", s)
    # commands with 1 parameters
    # s = re.sub(r"\\(vspace)\{.*?\}\n?", r"", s)

    # commands with 2 parameters
    s = re.sub(r"\\(setlength|settowidth)\{.*?\}\{.*?\}\n?", r"", s)
    # commands to remove the optional parameters from
    s = re.sub(
        r"(\\section|chapter|partchapter)\[.*?\]",
        r"\1",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # some stuff to drop
    s = s.replace("\\linebreak\\", "")
    s = s.replace("\\vspace*{\\fill}\n", "")
    s = s.replace("\\vskip 0pt plus 4\\baselineskip", "")
    s = s.replace(
        "\\vskip 1\\baselineskip plus .5\\textheight minus 1\\baselineskip",
        "",
    )

    # some simple replacings
    s = s.replace("~", "&nbsp;")
    s = s.replace("\\\\", "<br/>")
    s = s.replace("\\$", "$")
    s = s.replace("\\%", "%")
    s = s.replace("\\&", "&")
    s = s.replace("\\#", "#")
    s = s.replace("\\-", "-")
    s = s.replace("\\@", "&nbsp;")

    s = s.replace("\\emdashhyp", "—")
    s = s.replace("\\censor{Hermione}", "xxx")
    s = s.replace("$\\times$", "&times;")
    # s = s.replace("\\times", "&times;")
    s = s.replace(r"\@.", ".")
    s = s.replace(r"$\mbox{P}=\mbox{NP}$", "<i>P</i>=<i>NP</i>")
    s = s.replace(r"\mbox{“Salazar’s—”}", "“Salazar’s—”")
    s = s.replace("170–{140}", "170–140")

    # env to delete the optional parameters from
    s = re.sub(r"\\begin\{(verse)\}\[[^\]]+\]", r"\\begin{\1}", s)

    # spaces at start of line
    s = re.sub("\n +", "\n", s)
    # remove $ if not \$
    # FIXME: this is not working properly for " $.01$ "
    # s = re.sub("(?<!\\\\)$", "", s)

    #
    # START OF REPLACEMENTS
    #

    # \chapters
    # s = s.replace("\chapter*", "\chapter")
    s = re.sub(r"\\chapter\*\{(.*?)\}", r"<h2>\1</h2>", s)

    s = s.replace(r"\section*", r"\section")
    myMatches = re.finditer(r"(\\chapter\{([^\}]+)\})", s)
    for myMatch in myMatches:
        was = myMatch.group(1)
        womit = convert_chapter(myMatch.group(2))
        s = s.replace(was, womit)
    myMatches = re.finditer(r"(\\partchapter\{(.+?)\}\{(.+?)\})", s)
    for myMatch in myMatches:
        was = myMatch.group(1)
        womit = convert_chapter(myMatch.group(2) + ", Part " + myMatch.group(3))
        s = s.replace(was, womit)
    # \namedpartchapter{The Stanford Prison Experiment}{TSPE}{VI}{Constrained Optimization}
    myMatches = re.finditer(
        r"(\\namedpartchapter\{([^\}]+)\}\{([^\}]+)\}\{([^\}]+)\}\{([^\}]+)\})",
        s,
    )
    for myMatch in myMatches:
        was = myMatch.group(1)
        womit = convert_chapter(
            myMatch.group(2) + ", Part " + myMatch.group(4) + ": " + myMatch.group(5),
        )
        s = s.replace(was, womit)

    # simple commands without parameters
    # \am and pm
    s = re.sub(r"\\([ap])m\b", r"&nbsp;\1.m.", s, flags=re.DOTALL | re.IGNORECASE)
    # \SPHEW
    s = s.replace("\\SPHEW", "\\abbrev{SPHEW}")

    # simple commands with 1 parameter not containing other commands
    # custum spans
    s = re.sub(
        r"\\(abbrev|prophesy|scream|shout)\{([^\}\\]+)\}",
        r'<span class="\1">\2</span>',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # emph
    s = re.sub(
        r"\\emph\{([^\}\\]+)\}",
        r"<i>\1</i>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # \sout = strike through
    s = re.sub(
        r"\\(sout)\{([^\}\\]+?)\}",
        r"<s>\2</s>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # \url
    s = re.sub(
        r"\\(url)\{([^\}\\]+?)\}",
        r'<a href="\2">\2</a>',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # \href
    # \href{https://www.youtube.com/watch?v=UHZQEtG8xYo}{UHZQEtG8xYo on YouTube}
    s = re.sub(
        r"\\(href)\{([^\}]+?)\}\{([^\}]+?)\}",
        r'<a href="\1">\2</a>',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # \textbf
    s = re.sub(
        r"\\(textbf)\{([^\}\\]+)\}",
        r"<b>\2</b>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # \textsc
    s = re.sub(
        r"\\(textsc)\{([^\}\\]+)\}",
        r'<span class="smallcaps">\2</span>',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # custum spans 2nd run
    s = re.sub(
        r"\\(abbrev|prophesy|scream|shout)\{([^\}\\]+)\}",
        r'<span class="\1">\2</span>',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # uppercase
    s = re.sub(
        r"\\(MakeUppercase|inlineheadline)\{([^\}\\]+)\}",
        r'<span class="uppercase">\2</span>',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # emph 2nd run
    s = re.sub(
        r"\\emph\{([^\}\\]+)\}",
        r"<i>\1</i>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # \section{...} -> h3
    s = re.sub(
        r"\\(section)\{([^\}\\]+)\}",
        r"<h3>\2</h3>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # emph
    # emph in emph
    s = re.sub(
        r"\\emph\{([^\\\}]+)\\emph\{([^\\\}]+)\}([^\\\}])\}",
        r"<i>\1</i>\2<i>\3</i>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # environments
    s = s.replace("\\begin{writtenNote}\\centering", "\\begin{writtenNote}")

    # letter writtenNote
    s = re.sub(
        r"\\begin\{writtenNote\}(.+?)\\end\{writtenNote\}",
        r'<div class="letter"><p>\1</p></div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # letterAddress
    s = re.sub(
        r"\\letterAddress\{([^\}\\]+)\}",
        r"\1",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # letterClosing
    s = re.sub(
        r"\\letterClosing\[([^\]]+)\]\{([^\}\\]+)\}",
        r"\1<br/>\2",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r"\\letterClosing\{([^\}\\]+)\}",
        r"\1",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{em} and emph
    s = re.sub(
        r"\\begin\{(em|emph)\}(.+?)\\end\{\1\}",
        r'<div class="emph">\2</div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{center} and centering
    s = re.sub(
        r"\\begin{(center)}\s*\\scshape(.+?)\\end\{\1\}",
        r'<div class="center_sc">\2</div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r"\\begin\{(center|centering)\}(.+?)\\end\{\1\}",
        r'<div class="center">\2</div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{samepage} -> ""
    s = re.sub(
        r"\\begin\{samepage\}(.+?)\\end\{samepage\}",
        r"\1\n",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{verse}
    s = re.sub(
        r"\\begin\{verse\}(.+?)\\end\{verse\}",
        r'<div class="verse">\1</div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{playdialog}
    s = re.sub(
        r"\\begin\{playdialog\}(.+?)\\end\{playdialog\}",
        r'<div class="playdialog">\1</div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{chapterOpeningAuthorNote}
    s = re.sub(
        r"\\begin\{chapterOpeningAuthorNote\}\s*(.+?)\s*\\end\{chapterOpeningAuthorNote\}",
        r'<div class="chapterOpeningAuthorNote">E. Y.: “\1”</div><hr/>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{chapterOpeningQuote}
    s = re.sub(
        r"\\begin\{chapterOpeningQuote\}\s*(.+?)\s*\\end\{chapterOpeningQuote\}",
        r'<div class="chapterOpeningQuote">“\1”</div><hr/>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # \begin{headlines}
    s = re.sub(
        r"\\begin\{headlines\}(.+?)\\end\{headlines\}",
        r'<div class="headlines">\1</div>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r"\\header\{(.+?)\}",
        r'<span class="headline_header">\1</span>',
        s,
        flags=re.DOTALL,
    )
    s = re.sub(
        r"\\label\{(.+?)\}",
        r'<span class="headline_label">\1</span>',
        s,
        flags=re.DOTALL,
    )
    s = re.sub(
        r"\\headline\{(.+?)\}",
        r'<span class="headline_headline">\1</span>',
        s,
        flags=re.DOTALL,
    )

    # \begin{enumerate} -> ol
    s = re.sub(
        r"\\begin\{enumerate\}\[(.)\.\](.+?)\\end\{enumerate\}",
        r'<ol type="\1">\2</ol>\n',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r"\\begin\{enumerate\}(.+?)\\end\{enumerate\}",
        r"<ol>\1</ol>\n",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    s = re.sub(r"\s*\\item(.+?)\n", r"<li>\1</li>\n", s)

    # \parsel
    myMatches = re.finditer(r"(\\parsel\{([^\}\\]+)\})", s)
    for myMatch in myMatches:
        was = myMatch.group(1)
        womit = convert_parsel(myMatch.group(2))
        s = s.replace(was, womit)

    # \later
    s = re.sub(
        r"\\later\b",
        r'<div class="later">*</div>',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # footnotes_authorsnotetext
    myMatches = re.finditer(
        r"(\\authorsnotetext\{([^\}\\]+?)\})",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for myMatch in myMatches:
        was = myMatch.group(1)
        womit = f" [Author's Note: <i>{myMatch.group(2).strip()}</i>] "
        # womit = convert_footnotes(myMatch.group(2), authorsnote=True)
        s = s.replace(was, womit)

    # footnotetext
    myMatches = re.finditer(
        r"(\\footnotetext\{([^\}\\]+?)\})",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for myMatch in myMatches:
        was = myMatch.group(1)
        womit = f" [Author's Note: <i>{myMatch.group(2).strip()}</i>] "
        # womit = convert_footnotes(myMatch.group(2), authorsnote=False)
        s = s.replace(was, womit)

    # leftovers
    s = re.sub(r"\{\s*\}", r"", s, flags=re.DOTALL)
    s = re.sub(r"\[\s*\]", r"", s, flags=re.DOTALL)

    # Latex spaces, etc
    s = s.strip()

    s = s.replace("\n\n", "</p>\n<p>")
    # fixing p's
    s = s.replace("<p>\n", "<p>")
    s = s.replace("</h2></p>", "</h2>")
    s = s + "</p>\n"
    s = s.replace("<p><h3>", "<h3>")
    s = s.replace("</h3></p>", "</h3>")
    s = s.replace("<p><div ", "<div ")
    s = s.replace("</div></p>", "</div>")

    s = re.sub(r"</i>\]\s*</p>", "</i>] ", s, flags=re.DOTALL)

    s = s.replace("<p></p>\n", "")
    # multiple spaces
    s = re.sub(r"  +", r" ", s)
    return s


def convert_chapter(s: str) -> str:
    global counter_chapter
    counter_chapter += 1
    # chapter class is used in calibre to detect chapters
    out = f'<h2 class="chapter">{counter_chapter}. {s}</h2>'
    return out


def convert_parsel(s: str) -> str:
    s = s.replace("SS", "ẞ").replace("S", "SS").replace("ẞ", "SSS")
    s = s.replace("ss", "ß").replace("s", "ss").replace("ß", "sss")
    s = s.replace("&nbssp;", "&nbsp;")
    out = f'<span class="parsel">{s}</span>'
    return out


# def convert_footnotes(s: str, authorsnote: bool = False) -> str:
#
# epub:type="noteref" only works for EPUB version 3.
# at https://manual.calibre-ebook.com/generated/en/ebook-convert.html#epub-output-options
# it is suggested
# "EPUB 2 is the most widely compatible, only use EPUB 3 if you know you actually need it."
# so I decided to uses inline author comments instead
#
#     # \authorsnotetext{I do this in my own home.}
#     # ->
#     # <a epub:type="noteref" href="#fn1">1</a>
#     # <aside epub:type="footnote" id="fn1">
#     # <p>Author’s note: I do this in my own home.</p>
#     # </aside>
#     # if authorsnote = False -> <p>I do this in my own home.</p>
#     global counter_footnotes
#     counter_footnotes += 1
#     s_authorsnote = ""
#     if authorsnote:
#         s_authorsnote = "Author’s note: "
#     out = f""" <a epub:type="noteref" href="#fn{counter_footnotes}"><sup>{counter_footnotes}</sup></a>
# <aside epub:type="footnote" id="fn{counter_footnotes}">
# {s_authorsnote}{s}
# </aside> """
#     return out


def find_tex_commands(s: str) -> list:
    l = []

    myMatches = re.findall(r"\\[a-zA-Z0-9]+", s)
    for myMatch in myMatches:
        l.append(str(myMatch))

    return l


fhAll = open(  # noqa: SIM115
    f"{dir_out}/hpmor.html",
    mode="w",
    encoding="utf-8",
    newline="\n",
)
fhAll.write(html_start)
fhAll.write(html_preamble)


l_tex_commands_unhandled = []

for fileIn in sorted(glob.glob(f"{dir_tex_source}/hpmor-chapter-*.tex")):
    # for fileIn in sorted(glob.glob(f"../chapters/hpmor-chapter-100.tex")):
    (filePath, fileName) = os.path.split(fileIn)
    (fileBaseName, fileExtension) = os.path.splitext(fileName)
    fileOut = f"{dir_tmp}/{fileBaseName}.html"
    with open(fileIn, encoding="utf-8", newline="\n") as fh:
        cont = fh.read()
    cont = simplify_tex(cont)
    cont = tex2html(cont)

    l = find_tex_commands(cont)
    l_tex_commands_unhandled.extend(l)
    if len(l) > 0:
        print(
            f"WARN: there are leftover LaTeX commands in file {fileOut}:\n"
            + ", ".join(l),
        )

    with open(fileOut, mode="w", encoding="utf-8", newline="\n") as fh:
        fh.write(html_start + cont + html_end)

    if fileBaseName == "hpmor-chapter-001":
        cont = (
            "<h1 class='part'>Book 1: <br/>Harry James Potter-Evans-Verres<br/> and the Methods of Rationality</h1>\n"
            + cont
        )
    elif fileBaseName == "hpmor-chapter-022":
        cont = (
            "<h1 class='part'>Book 2: <br/>Harry James Potter-Evans-Verres<br/> and the Professor's Games</h1>\n"
            + cont
        )
    elif fileBaseName == "hpmor-chapter-038":
        cont = (
            "<h1 class='part'>Book 3: <br/>Harry James Potter-Evans-Verres<br/> and the Shadows of Death</h1>\n"
            + cont
        )
    elif fileBaseName == "hpmor-chapter-065":
        cont = (
            "<h1 class='part'>Book 4: <br/>Hermione Jean Granger<br/> and the Phoenix's Call</h1>\n"
            + cont
        )
    elif fileBaseName == "hpmor-chapter-086":
        cont = (
            "<h1 class='part'>Book 5: <br/>Harry James Potter-Evans-Verres<br/> and the Last Enemy</h1>\n"
            + cont
        )
    elif fileBaseName == "hpmor-chapter-100":
        cont = (
            "<h1 class='part'>Book 6: <br/>Harry James Potter-Evans-Verres<br/> and the Philosopher's Stone</h1>\n"
            + cont
        )

    fhAll.write(cont)

fhAll.write(html_end)
fhAll.close()

d_tex_commands_unhandled = {}
for item in l_tex_commands_unhandled:
    if item in d_tex_commands_unhandled:
        d_tex_commands_unhandled[item] += 1
    else:
        d_tex_commands_unhandled[item] = 1
# sort values reversed
for key, value in sorted(
    d_tex_commands_unhandled.items(),
    key=lambda item: item[1],
    reverse=True,
):
    print(f"{value}\t{key}")

assert (
    len(d_tex_commands_unhandled) == 0
), "Error: unhandled LaTeX commands found, see above"
