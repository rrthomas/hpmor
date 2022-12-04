#!/usr/bin/env python3
# by Torben Menke https://entorb.net
"""
Check chapter .tex files for known issues and propose fixes.

reads hpmor.tex for list of uncommented/relevant/e.g. translated) chapter files
ignores all lines starting with '%'
improvements are proposed via chapters/*-autofix.tex files
configuration in check-chapters.json
lang: EN, DE, FR, ...
raise_error: true -> script exits with error, used for autobuild of releases
print_diff: true : print line of issues
"""
import difflib
import glob
import json
import os
import re
import sys

# ensure we are in hpmor root dir
dir_root = os.path.dirname(sys.argv[0]) + "/.."
os.chdir(dir_root)


# pos lookahead: (?=...)
# neg lookahead: (?!...)
# pos lookbehind (?<=...)
# neg lookbehind (?<!...)

# TODO:
# \latersection must be at newline
# add \spell macro

# TO chars manually find and replace
# *, ", ', », «, ”,

# continue sentence in lower case
# (,“[^„]+„)([A-Z]) -> \1\l\2

# shall we modify the source file?
# USE WITH CAUTION!!!
inline_fixing = False
# inline_fixing = True


# read settings from check-chapters.json
with open(
    os.path.dirname(sys.argv[0]) + "/check-chapters.json",
    encoding="utf-8",
) as fh:
    settings = json.load(fh)


def get_list_of_chapter_files() -> list:
    """
    Read hpmor.tex .

    extract list of (not-commented out) chapter files
    returns list of filesnames
    """
    list_of_chapter_files = []
    with open("hpmor.tex", encoding="utf-8") as fh:
        lines = fh.readlines()
    lines = [elem for elem in lines if elem.startswith(r"\include{chapters/")]
    for line in lines:
        fileName = re.search(r"^.*include\{(chapters/.+?)\}.*$", line).group(1)
        list_of_chapter_files.append(fileName + ".tex")
    return list_of_chapter_files


def process_file(fileIn: str) -> bool:
    """
    Check a file for know issues.

    returns issues_found = True if we have a finding
    the proposal is written to chapters/*-autofix.tex
    """
    issues_found = False
    with open(fileIn, encoding="utf-8") as fh:
        cont = fh.read()

    # end of line: LF only
    if "\r" in cont:
        issues_found = True
        cont = re.sub(r"\r\n?", r"\n", cont)
    # invisible strange spaces
    if " " in cont:
        issues_found = True
        cont = re.sub(r" +", r" ", cont)

    # more than 1 empty line
    if "\n\n\n" in cont:
        issues_found = True
        cont = re.sub(r"\n\n\n+", r"\n\n", cont)

    # now split per line
    l_cont = cont.split("\n")
    del cont
    l_cont_2 = []
    for line in l_cont:
        lineOrig = line
        # keep commented-out lines as they are
        if re.match(r"^\s*%", line):
            l_cont_2.append(line)
        else:
            # check not commented-out lines
            line = fix_line(s=line)
            l_cont_2.append(line)
            if issues_found is False and lineOrig != line:
                issues_found = True
    if issues_found:
        # with proposal to *-autofix.tex
        print(" issues found!")
        fileOut = fileIn.replace(".tex", "-autofix.tex")

        # USE WITH CAUTION!!!
        if inline_fixing:
            fileOut = fileIn
            issues_found = False

        with open(fileOut, mode="w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(l_cont_2))

        if settings["print_diff"]:
            with open(fileIn, encoding="utf-8") as file1, open(
                fileOut,
                encoding="utf-8",
            ) as file2:
                diff = difflib.ndiff(file1.readlines(), file2.readlines())
            delta = "".join(l for l in diff if l.startswith("+ ") or l.startswith("- "))
            print(delta)

    return issues_found


def fix_line(s: str) -> str:
    # simple and safe
    s = fix_spaces(s)
    s = fix_latex(s)
    s = fix_dots(s)
    s = fix_MrMrs(s)
    s = fix_numbers(s)
    s = fix_common_typos(s)
    s = fix_spaces(s)

    # advanced stuff
    s = fix_quotations(s)
    s = fix_emph(s)
    s = fix_hyphens(s)

    # add spell macro
    if settings["lang"] == "DE":
        s = add_spell(s)

    # spaces, again
    s = fix_spaces(s)
    return s


def fix_spaces(s: str) -> str:
    # trailing spaces
    s = re.sub(r" +$", "", s)
    # remove spaces from empty lines
    s = re.sub(r"^\s+$", "", s)
    # multiple spaces (excluding start of new line)
    s = re.sub(r"(?<!^)[ \t][ \t]+", " ", s)
    return s


def fix_latex(s: str) -> str:
    # Latex: \begin and \end{...} at new line
    s = re.sub(r"([^\s+%])\s*\\(begin|end)\{", r"\1\n\\\2{", s)
    # Latex: \\ at new line
    s = re.sub(r"\\\\\s*(?=[^$%\[]])", r"\\\\\n", s)
    return s


def fix_dots(s: str) -> str:
    # ... -> …
    s = s.replace("...", "…")
    # ... with spaces around
    s = s.replace(" … ", "…")
    # NOT '… ' as in ', no… “I'
    # s = re.sub(r" *… *", r"…", s)

    # … at end of quotation ' …"' -> '…"'
    s = s.replace(' …"', '…"')
    # before comma
    s = s.replace(" …,", "…,")
    if settings["lang"] == "EN":
        s = s.replace(" …”", "…”")
    if settings["lang"] == "DE":
        s = s.replace(" …“", "…“")
    # … at start of line
    s = re.sub(r"^ *… *", r"…", s)
    # … at end of line
    s = re.sub(r" *… *$", r"…", s)
    # Word…"Word -> Word…" Word
    s = re.sub(r'(\w…")(\w)', r"\1 \2", s)
    # … after . or ,
    s = re.sub(r"([,\.])…", r"\1 …", s)
    return s


def fix_MrMrs(s: str) -> str:
    # Mr / Mrs
    s = s.replace("Mr. H. Potter", "Mr~H.~Potter")
    # s = s.replace("Mr. Potter", "Mr~Potter")
    if settings["lang"] == "DE":
        s = re.sub(r"\b(Mr|Mrs|Miss|Dr)\b\.?\s+(?!”)", r"\1~", s)
    # Dr.~ -> Dr~Potter
    s = re.sub(r"\b(Mr|Mrs|Miss|Dr)\b\.~", r"\1~", s)
    # "Dr. " -> "Dr~"
    # s = re.sub(r"\b(Dr)\b\.?~?\s*", r"\1~", s)
    # s = s.replace("Mr~and Mrs~", "Mr and Mrs~")
    return s


assert fix_MrMrs("Mr. H. Potter") == "Mr~H.~Potter"
if settings["lang"] == "DE":
    assert fix_MrMrs("Mr. Potter") == "Mr~Potter"
    assert fix_MrMrs("Mrs. Potter") == "Mrs~Potter"
    assert fix_MrMrs("Miss. Potter") == "Miss~Potter"
    assert fix_MrMrs("Dr. Potter") == "Dr~Potter"
    assert fix_MrMrs("Dr Potter") == "Dr~Potter"
    assert fix_MrMrs("Mr Potter") == "Mr~Potter"
    # assert fix_MrMrs("Mr. and Mrs. Davis") == "Mr and Mrs~Davis"
    assert fix_MrMrs("Mr. and Mrs. Davis") == "Mr~and Mrs~Davis"
assert fix_MrMrs("it’s Doctor now, not Miss.”") == "it’s Doctor now, not Miss.”"


def fix_numbers(s: str) -> str:
    if settings["lang"] == "DE":
        s = re.sub(r"(\d) +(Uhr)", r"\1~\2", s)
    return s


def fix_common_typos(s: str) -> str:
    if settings["lang"] == "DE":
        s = s.replace("Adoleszenz", "Pubertät")
        s = s.replace("Avadakedavra", "Avada Kedavra")
        s = s.replace("Diagon Alley", "Winkelgasse")
        s = s.replace("Hermione", "Hermine")
        s = re.sub(
            r"Junge\-der\-(überlebt\-hat|überlebte)\b",
            r"Junge-der-überlebte",
            s,
        )
        s = re.sub(r"Junge, der lebte\b", r"Junge-der-überlebte", s)
        s = s.replace("Muggelforscher", "Muggelwissenschaftler")
        s = s.replace("Stupefy", "Stupor")
        s = s.replace("Wizengamot", "Zaubergamot")
        s = s.replace("S.P.H.E.W.", r"\SPHEW")
        s = s.replace("ut mir Leid", "ut mir leid")
        # s = s.replace("das einzige", "das Einzige")
    # Apostroph
    # "word's"
    s = re.sub(r"(\w)'(s)\b", r"\1’\2", s)
    if settings["lang"] == "DE":
        s = re.sub(r"(\w)'(sche|scher|schen)\b", r"\1’\2", s)
    if settings["lang"] == "EN":
        # "wouldn't"
        s = re.sub(r"(\w)'(t)\b", r"\1’\2", s)
        # I'm
        s = re.sub(r"\bI'm\b", r"I’m", s)

    return s


assert (fix_common_typos("Test Mungo's King's Cross")) == "Test Mungo’s King’s Cross"


def fix_quotations(s: str) -> str:
    # in EN the quotations are “...” and ‘...’ (for quotations in quotations)
    # in DE the quotations are „...“ and ‚...‘ (for quotations in quotations)

    # "..." -> “...”
    if settings["lang"] == "EN":
        s = re.sub(r'"([^"]+)"', r"“\1”", s)
    if settings["lang"] == "DE":
        s = re.sub(r'"([^"]+)"', r"„\1“", s)

    # '...' -> ‘...’
    if "nglui mglw" not in s:
        if settings["lang"] == "EN":
            s = re.sub(r"'([^']+)'", r"‘\1’", s)
        if settings["lang"] == "DE":
            s = re.sub(r"'([^']+)'", r"‚\1‘", s)

    if settings["lang"] == "DE":
        # fix bad single word quotes
        # ’Ja‘ -> ‚Ja‘
        s = re.sub(r"’([^ ]+?)‘", r"‚\1‘", s)
        # migrate EN quotations
        s = re.sub(r"“([^“”]+?)”", r"„\1“", s)
        # migrate EN single quotations
        s = re.sub(r"‘([^‘’]+?)’", r"‚\1‘", s)
        # migrate FR quotations »...«
        s = re.sub(r"»([^»«]+?)«", r"„\1“", s)

        # migrate EN quotations at first word of chapter
        s = re.sub(r"\\(lettrine|lettrinepara)\[ante=“\]", r"\\\1[ante=„]", s)

    # fixing ' "Word..."' and ' "\command..."'
    if settings["lang"] == "EN":
        s = re.sub(r'(^|\s)"((\\|\w).*?)"', r"\1“\2”", s)
    if settings["lang"] == "DE":
        s = re.sub(r'(^|\s)"((\\|\w).*?)"', r"\1„\2“", s)

    # add space between … and “
    # if settings["lang"] == "EN":
    #     s = re.sub(r"…“", r"… “", s)
    if settings["lang"] == "DE":
        s = re.sub(r"…„", r"… „", s)

    # space before closing “
    if settings["lang"] == "EN":
        s = re.sub(r" +”", r"” ", s)
    if settings["lang"] == "DE":
        s = re.sub(r" +“", r"“ ", s)

    # space between "…" and "“"
    # if settings["lang"] == "EN":
    #     s = re.sub(r"…„", r"… “", s)     # rrthomas voted againt it
    if settings["lang"] == "DE":
        s = re.sub(r"…„", r"… „", s)

    # ” } -> ”}
    if settings["lang"] == "EN":
        s = s.replace("” }", "”} ")
    if settings["lang"] == "DE":
        s = s.replace("“ }", "“} ")
    # now fix possible new double spaces created by line above
    s = re.sub(r"(?<!^)[ \t][ \t]+", " ", s)
    s = re.sub(r" +$", r"", s)

    # quotation marks should go outside of emph:
    # \emph{“.....”} -> “\emph{.....}”
    if settings["lang"] == "EN":
        s = re.sub(r"\\(emph|shout)\{“([^”]+?)”\}", r"“\\\1{\2}”", s)
    if settings["lang"] == "DE":
        s = re.sub(r"\\(emph|shout)\{„([^“]+?)“\}", r"„\\\1{\2}“", s)

    # lone “ at end of \emph
    # “...\emph{.....”} -> “...\emph{.....}”
    if settings["lang"] == "EN":
        s = re.sub(r"(\\emph\{[^“]+?)”\}", r"\1}”", s)
    if settings["lang"] == "DE":
        s = re.sub(r"(\\emph\{[^„]+?)“\}", r"\1}“", s)

    # punctuation at end of quotation (and emph)
    # attention: false positives when quoting a book titles etc.
    # for EN mostly correct already
    #    if settings["lang"] == "EN":
    #        s = re.sub(r"(?<![\.,!\?;])(?<![\.,!\?;]\})”,", r",”", s)
    if settings["lang"] == "DE":
        # not, this is wrong, it is correct to have „...“,
        # s = re.sub(r"(?<![\.,!\?;])(?<![\.,!\?;]\})“,", r",“", s)
        s = re.sub(r"(?<![\.,!\?;]),“", r"“,", s)

    # nested single quote + emph
    if settings["lang"] == "EN":
        s = re.sub(r"‘\\emph{([^}]+)}’", r"‘\1’", s)
        s = re.sub(r"\\emph{‘([^}]+)’}", r"‘\1’", s)
    if settings["lang"] == "EN":
        s = re.sub(r"‚\\emph{([^}]+)}‘", r"‚\1‘", s)
        s = re.sub(r"\\emph{‚([^}]+)‘}", r"‚\1‘", s)

    # comma at end of emph&quotation
    if settings["lang"] == "EN":
        pass
        # false positives at book titles etc.
        # s = s.replace("}”,", ",}”")
        # s = s.replace("”,", ",”")
    if settings["lang"] == "DE":
        s = s.replace(",}”", "}”,")
        s = s.replace(",”", "”,")

    # space after closing “
    if settings["lang"] == "DE":
        s = re.sub(r"(“)([\w])", r"\1 \2", s)

    return s


# assert fix_quotations("\parsel{Ich sehe nichts}“,")== "\parsel{Ich sehe nichts},“"


def fix_emph(s: str) -> str:
    # space at start of emph -> move before emph
    s = re.sub(r"(\\emph{) +", " \1", s)

    # move punctuation out of lowercase 1-word-emph
    # ... \emph{WORD.} -> \emph{WORD}.
    # Note: only for , and .
    if (
        settings["lang"] == "EN" and "lettrinepara" not in s
    ):  # not \lettrinepara{W}{\emph{hat?}}:
        # s = re.sub(r"(?<!^)\\emph\{([^\}A-Z]+)([,\.])\}(?!”)", r"\\emph{\1}\2", s)
        s = re.sub(r"\\emph\{([^\}A-Z]+)([,\.;!\?])\}(?!”)", r"\\emph{\1}\2", s)
    if settings["lang"] == "DE":
        s = re.sub(r"(?<!^)\\emph\{([^ …\}]+)([,\.])\}(?!“)", r"\\emph{\1}\2", s)

    #  only after space fix ! and ?
    # " \emph{true!}" -> " \emph{true}!"
    s = re.sub(r" \\emph\{([^ …\}A-Z]+)([,\.;!\?])\}", r" \\emph{\1}\2", s)

    # Note: good, but MANY false positives
    # \emph{...} word \emph{...} -> \emph{... \emph{word} ...
    # s = re.sub(r"(\\emph\{[^\}]+)\} ([^ ]+) \\emph\{", r"\1 \\emph{\2} ", s)
    return s


assert fix_emph(r"That’s not \emph{true!}") == r"That’s not \emph{true}!"
assert fix_emph(r"she got \emph{magic,} can you") == r"she got \emph{magic}, can you"
# unchanged:
if settings["lang"] == "EN":
    assert (
        fix_emph(r"briefly. \emph{Hopeless.} Both") == r"briefly. \emph{Hopeless.} Both"
    )
if settings["lang"] == "DE":
    assert (
        fix_emph(r"briefly. \emph{Hopeless.} Both") == r"briefly. \emph{Hopeless}. Both"
    )

# if settings["lang"] == "EN":


def fix_hyphens(s: str) -> str:
    # --- -> em dash —
    s = s.replace("---", "—")
    s = s.replace("--", "—")
    # hyphens: (space-hyphen-space) should be "—" (em dash).
    # trim space around em-dash
    s = s.replace(" — ", "—")
    # shorter dash as well
    s = s.replace(" – ", "—")
    # NOT for '— ' as in ', no— “I'
    # s = re.sub(r"— ", r"—", s)
    # " - " -> "—"
    s = s.replace(" - ", "—")
    # remove space before — followed by punctuation
    s = re.sub(r" —([,\.!\?;])", r"—\1", s)

    # - at start of line
    s = re.sub(r"^[\-—] *", r"—", s)
    # - at start of line
    # if settings["lang"] == "EN":
    #     s = re.sub(r" [\-—]$", r"—", s) # rrthomas voted againt it
    if settings["lang"] == "DE":
        s = re.sub(r" [\-—]$", r"—", s)
    # - at end of emph
    s = re.sub(r"(\s*)\-\}", r"—}\1", s)
    # at start of quote
    # if settings["lang"] == "EN":
    #     s = re.sub(r"—“", r"— “", s) # rrthomas voted againt it
    if settings["lang"] == "DE":
        s = re.sub(r"—„", r"— „", s)
        s = re.sub(r"„— ", r"„—", s)

    # at end of quote
    if settings["lang"] == "EN":
        s = re.sub(r"(\s*)\-”", r"—”\1", s)
    if settings["lang"] == "DE":
        s = re.sub(r"(\s*)\-“", r"—“\1", s)

    # space-hyphen-quotation end
    if settings["lang"] == "EN":
        s = re.sub(r"\s+(—”)", r"\1", s)
    if settings["lang"] == "DE":
        s = re.sub(r"\s+(—“)", r"\1", s)

    # there is a shorter dash as well:
    # 2-4 -> 2–4 using mid length hyphen
    s = re.sub(r"(\d)\-(?=\d)", r"\1–", s)
    # NOT: mid-length dash ->  em dash (caution: false positives!)
    # s = s.replace("–", "—")
    return s


assert fix_hyphens("2-3-4") == "2–3–4"


def add_spell(s: str) -> str:
    spells = [
        "Accio",
        "Alohomora",
        # "Avada Kedavra", not here, since sometimes in emph ok.
        "Cluthe",
        "Colloportus",
        "Contego",
        "Crystferrium",
        "Diffindo",
        "Deligitor prodeas",
        "Dulak",
        "Elmekia",
        "Expelliarmus",
        "Flipendo",
        "Finite Incantatem",
        "Frigideiro",
        "Glisseo",
        "Gom jabbar",
        "Impedimenta",
        "Imperius",
        "Jellify",
        "Inflammare",
        "Luminos",
        "Mahasu",
        "Lagann",
        "Lucis Gladius",
        "Lumos",
        "Obliviate",
        "Prismatis",
        "Protego",
        "Polyfluis Reverso",
        "Quietus",
        "Ravum Calvaria",
        "Rennervate",
        "Scourgify",
        "Silencio",
        "Somnium",
        "Stupor",
        "Thermos",
        "Tonare",
        "Ventriliquo",
        "Ventus",
        "Wingardium Leviosa",
    ]

    for spell in spells:
        s2 = r"„?\\emph{„?(" + spell + r")(!?)\.?“?}“?"
        s = re.sub(s2, r"\\spell{\1\2}", s)

    # \spell followed by ! -> inline
    s = re.sub(r"(\\spell{[^}]+)}!", r"\1!}", s)
    # no „...“ around \spell
    s = re.sub(r"„?(\\spell{[^}]+)}“?", r"\1}", s)
    # \spell without !
    s = re.sub(r"(\\spell{[^}]+)!}", r"\1}", s)

    return s


if settings["lang"] == "DE":
    assert add_spell(r"„\emph{Lumos}“") == r"\spell{Lumos}"
    assert add_spell(r"\emph{„Lumos“}") == r"\spell{Lumos}"
    assert add_spell(r"\emph{Lumos!}") == r"\spell{Lumos}"
    assert add_spell(r"„\spell{Contego}“") == r"\spell{Contego}", add_spell(
        r"„\spell{Contego}“",
    )


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
        assert any_issue_found is False, "Issues found, please fix!"
