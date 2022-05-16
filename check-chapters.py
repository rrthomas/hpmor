#!/usr/bin/env python3

# by Torben Menke https://entorb.net

# checks chapter .tex files for known issues and propose fixes
# reads hpmor.tex for list of uncommented/relevant/e.g. translated) chapter files
# ignores all lines starting with '%'
# improvements are proposed via chapters/*-autofix.tex files

# configuration in check-chapters.json
# lang: EN, DE, FR, ...
# raise_error: true -> script exits with error, used for autobuild of releases
# print_diff: true : print line of issues

import glob
import os
import re
import json
import difflib

# TODO:
# \latersection must be at newline

# shall we modify the source file?
# USE WITH CAUTION!!!
inline_fixing = False
inline_fixing = True


with open("check-chapters.json", mode="r", encoding="utf-8") as fh:
    settings = json.load(fh)


def get_list_of_chapter_files() -> list:
    list_of_chapter_files = []
    # read list of relevant chapter files from hpmor.tex
    with open("hpmor.tex", mode="r", encoding="utf-8") as fh:
        lines = fh.readlines()
    lines = [elem for elem in lines if elem.startswith("\include{chapters/")]
    for line in lines:
        fileName = re.search("^.*include\{(chapters/.+?)\}.*$", line).group(1)
        list_of_chapter_files.append(fileName + ".tex")
    return list_of_chapter_files


def process_file(fileIn: str) -> bool:
    """
    checks file for know issues
    return issues_found = True if we have a finding
    the proposal is written to chapters/*-autofix.tex
    """
    issue_found = False
    with open(fileIn, mode="r", encoding="utf-8") as fh:
        cont = fh.read()

    # end of line
    if "\r" in cont:
        issue_found = True
        cont = re.sub(r"\r\n?", r"\n", cont)

    # more than 1 empty line
    if "\n\n\n" in cont:
        issue_found = True
        cont = re.sub(r"\n\n\n+", r"\n\n", cont)

    l_cont = cont.split("\n")
    del cont
    l_cont_2 = []
    for line in l_cont:
        lineOrig = line
        # do not modify commented out lines
        if not re.match("^\s*%", line):
            line = fix_line(s=line)
            if issue_found == False and lineOrig != line:
                issue_found = True
        l_cont_2.append(line)
    if issue_found:
        print(" issues found!")
        fileOut = fileIn.replace(".tex", "-autofix.tex")

        # inline fixing: use with CAUTION
        if inline_fixing:
            fileOut = fileIn
            issue_found = False

        with open(fileOut, mode="w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(l_cont_2))

        if settings["print_diff"]:
            file1 = open(fileIn, "r", encoding="utf-8")
            file2 = open(fileOut, "r", encoding="utf-8")
            diff = difflib.ndiff(file1.readlines(), file2.readlines())
            delta = "".join(l for l in diff if l.startswith("+ ") or l.startswith("- "))
            print(delta)

    return issue_found


def fix_line(s: str) -> str:
    # TODO:

    s1 = s
    # multiple spaces
    s = re.sub(r"(?<!^)[ \t][ \t]+", " ", s)
    # trailing spaces
    s = re.sub(r" +$", "", s)
    # # remove spaces from empty lines
    # s = re.sub(r"^\s+$", "", s)
    # # Latex: \end{...} at new line
    # s = re.sub(r"([^\s+%])\s*\\end\{", r"\1\n\\end{", s)

    # # ' ' at start of emph
    # s = s.replace("\emph{ ", " \emph{")

    # # simple
    # # ... without spaces around
    # s = s.replace(" *... *", "…")
    # s = s.replace(" … ", "…")
    # # NOT for '… ' as in ', no… “I'
    # # s = re.sub(r" *… *", r"…", s)

    # s = s.replace(" … ", "…")
    # # … at end of quotation ' …"' -> '…"'
    # s = s.replace(' …"', '…"')
    # # … at end of line
    # s = re.sub(r" …\n", r'…\n"', s)
    # # Word…"Word -> Word…" Word
    # s = re.sub(r"(\w…\")(\w)", r"\1 \2", s)

    # # Mr / Mrs
    # s = s.replace("Mr. H. Potter", "Mr~H.~Potter")
    # s = s.replace("Mr. Potter", "Mr~Potter")
    # s = re.sub(r"\b(Mr|Mrs|Miss)\b\.?~?\s*", r"\1~", s)
    # # "Dr. " -> "Dr~"
    # s = re.sub(r"\b(Dr)\b\.?~?\s*", r"\1~", s)

    # # quotations
    # if settings["lang"] == "EN":
        # # in EN the quotations are “...” and ‘...’
        # # "..." -> “...”
        # s = re.sub(r'"([^"]+)"', r"“\1”", s)

        # # ” } -> ”}
        # s = s.replace("” }", "”} ")
        # s = s.replace(
            # "  ", " "
        # )  # now fix possible new double spaces created by line above
        # s = re.sub(r" +$", r"", s)

        # # quotation marks should go outside of \emph{“...”} -> “\emph{...}”
        # s = re.sub(r"\\(emph|shout)\{“([^”]+?)”\}", r"“\\\1{\2}”", s)
        # # s = s.replace("", "”}")

        # # lone “ at end of \emph
        # s = re.sub(r"(\\emph\{[^„]+?)“\}", r"\1}“", s)

    # if settings["lang"] == "DE":
        # # in DE the quotations are „...“

        # # "..." -> „...“
        # s = re.sub(r'"([^"]+)"', r"“\1”", s)
        # s = re.sub(r"…„", r"… „", s)

        # # “ } -> “}
        # s = s.replace("“ }", "“} ")
        # s = s.replace(
            # "  ", " "
        # )  # now fix possible new double spaces created by line above
        # s = re.sub(r" +$", r"", s)

        # # fixing ' "A..."' and ' "\..."'
        # s = re.sub(r'(^|\s)"((\\|\w).*?)"', r"\1„\2“", s)

        # # at first word of chapter
        # s = re.sub(r"\\(lettrine|lettrinepara)\[ante=“\]", r"\\\1[ante=„]", s)

        # # migrate EN quotations
        # s = re.sub(r"“([^“”]+?)”", r"„\1“", s)

        # # quotation marks should go outside of \emph{„...“} -> „\emph{...}“
        # s = re.sub(r"\\(emph|shout)\{„([^“]+?)“\}", r"„\\\1{\2}“", s)

        # # lone “ at end of \emph
        # s = re.sub(r"(\\emph\{[^„]+?)“\}", r"\1}“", s)

    # # numbers
    # if settings["lang"] == "DE":
        # s = re.sub(r"(\d) (Uhr)", r"\1~\2", s)

    # # TODO: single quotes
    # # DE: ‚...‘

    # # hyphens: (space-hyphen-space) should be "—" (em dash).
    # # TODO: there is a shorter dash as well..
    # # - ->  —  and  – ->  — ?
    # s = s.replace("---", "—")
    # # mid-length dash ->  em dash (caution: false positives!)
    # # s = s.replace("–", "—")

    # # trim space around em-dash
    # s = s.replace(" — ", "—")
    # # NOT for '— ' as in ', no— “I'
    # # s = re.sub(r"— ", r"—", s)
    # # - at start of line
    # s = re.sub(r"^[\-—] *", r"—", s)
    # # - at start of line
    # s = re.sub(r" [\-—]$", r"—", s)
    # # - at end of emph
    # s = re.sub(r"(\s*)\-\}", r"—}\1", s)
    # # - at end of quote
    # if settings["lang"] == "EN":
        # s = re.sub(r"(\s*)\-”", r"—”\1", s)
    # if settings["lang"] == "DE":
        # s = re.sub(r"(\s*)\-“", r"—“\1", s)

    # # Note: good, but MANY false positives
    # # \emph{...} word \emph{...} -> \emph{... \emph{word} ...
    # # s = re.sub(r"(\\emph\{[^\}]+)\} ([^ ]+) \\emph\{", r"\1 \\emph{\2} ", s)

    # emph
    # ' ' at start of emph
    s = s.replace("\emph{ ", " \emph{")
    # move punctuation out of 1-word-emph
    # TODO: maybe only for , and .? or not if followed by “ ?
    # ... \emph{WORD.} -> \emph{WORD}.
    if settings["lang"] == "EN":
        # s = re.sub(r"\\emph\{([^ …\}]+)([,\.!\?])\}(?!”)", r"\\emph{\1}\2", s)
        s = re.sub(r"(?<!^)\\emph\{([^ …\}]+)([,\.])\}(?!”)", r"\\emph{\1}\2", s)
    if settings["lang"] == "DE":
        # s = re.sub(r"\\emph\{([^ …\}]+)([,\.!\?])\}(?!“)", r"\\emph{\1}\2", s)
        s = re.sub(r"(?<!^)\\emph\{([^ …\}]+)([,\.])\}(?!“)", r"\\emph{\1}\2", s)

    # common typos
    if settings["lang"] == "DE":
        s = s.replace("ut mir Leid", "ut mir leid")

    # multiple spaces, again
    s = re.sub(r"(?<!^)[ \t][ \t]+", " ", s)

    # trailing spaces, again
    s = re.sub(r" +$", "", s)

    return s


if __name__ == "__main__":
    # cleanup first
    for fileOut in glob.glob("chapters/*-autofix.tex"):
        os.remove(fileOut)

    list_of_chapter_files = get_list_of_chapter_files()

    any_issue_found = False
    for fileIn in list_of_chapter_files:
        print(fileIn)
        issue_found = process_file(fileIn=fileIn)
        if issue_found:
            any_issue_found = True

    if settings["raise_error"]:
        assert any_issue_found == False, "Issues found, please fix!"
