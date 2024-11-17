#!/usr/bin/env python3
# by Torben Menke https://entorb.net

# ruff: noqa: S101 RUF001 RUF003 D103

"""
Check chapter .tex files for known issues and propose fixes.

reads hpmor.tex for list of uncommented/relevant/e.g. translated) chapter files
ignores all lines starting with '%'
improvements are proposed via chapters/*-autofix.tex files
configuration in check_chapters_settings.py
"""

import difflib
import re
from multiprocessing import Pool, cpu_count
from os import chdir
from pathlib import Path

from check_chapters_settings import settings

# ensure we are in hpmor root dir
chdir(Path(__file__).parents[1])
assert Path("./chapters").is_dir()


# pos lookahead: (?=...)
# neg lookahead: (?!...)
# pos lookbehind (?<=...)
# neg lookbehind (?<!...)

# in EN the quotations are “...” and ‘...’ (for quotations in quotations)
# in DE the quotations are „...“ and ‚...‘ (for quotations in quotations)
# Apostroph: ’


# TODO: \latersection must be at newline

# chars manually find and replace
# *, ", ', », «, ”,

# continue sentence in lower case
# (,“[^„]+„)([A-Z]) -> \1\l\2


def get_list_of_chapter_files() -> list[Path]:
    """
    Read hpmor.tex, extract list of (not-commented out) chapter files.

    returns list of filenames
    """
    list_of_files: list[Path] = []
    with Path("hpmor.tex").open(encoding="utf-8") as fh:
        for line in fh:
            my_match = re.search(r"^.*include\{(chapters/.+?)\}.*$", line)
            if my_match:
                include_path = my_match.group(1)
                p = Path(f"{include_path}.tex")
                if p.is_file():
                    list_of_files.append(p)
    return list_of_files


def multiline_check(s: str) -> str:
    """Check regarding linebreaks."""
    # end of line: LF only
    s = re.sub(r"\r\n?", r"\n", s)

    # more than 1 empty line
    s = re.sub(r"\n\n\n+", r"\n\n", s)

    if settings["lang"] != "EN":
        # line before \translatorsnote must end with %
        s = re.sub(r"(?<!%)\n(\\translatorsnote)", r"%\n\1", s)
    return s


def process_file(file_in: Path) -> bool:
    """
    Check file for known issues.

    returns issues_found = True if we have a finding
    a proposed fix is written to chapters/*-autofix.tex
    """
    issues_found = False
    cont = file_in.read_text(encoding="utf-8")

    cont_orig = cont
    cont = multiline_check(s=cont_orig)
    if cont != cont_orig:
        issues_found = True
    del cont_orig

    # now split per line
    cont_lines_orig = cont.split("\n")
    del cont
    cont_lines_new: list[str] = []
    for line in cont_lines_orig:
        line_orig = line
        # keep commented-out lines as they are
        if re.match(r"^\s*%", line):
            cont_lines_new.append(line)
        else:
            # check not commented-out lines
            line = fix_line(s=line)  # noqa: PLW2901
            cont_lines_new.append(line)
            if issues_found is False and line_orig != line:
                issues_found = True
    if issues_found:
        # write proposal to *-autofix.tex
        print(" issues found!")
        file_out = file_in.parent / (file_in.stem + "-autofix.tex")

        # USE WITH CAUTION!!!
        if settings["inline_fixing"]:
            file_out = file_in
            issues_found = False

        with file_out.open(mode="w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(cont_lines_new))

        if settings["print_diff"]:
            with (
                file_in.open(encoding="utf-8") as file1,
                file_out.open(encoding="utf-8") as file2,
            ):
                diff = difflib.ndiff(file1.readlines(), file2.readlines())
            delta = "".join(x for x in diff if x.startswith(("+ ", "- ")))
            print(file_in.name + "\n" + delta)

    return issues_found


def fix_line(s: str) -> str:
    """Apply all fix functions to each line."""
    # simple and safe
    s = fix_spaces(s)
    s = fix_common_typos(s)
    s = fix_ellipsis(s)
    s = fix_latex(s)
    s = fix_MrMrs(s)
    s = fix_numbers(s)
    s = fix_punctuation(s)
    s = fix_spaces(s)

    # advanced stuff
    s = fix_emph(s)
    s = fix_hyphens(s)
    s = fix_quotations(s)

    # force linebreaks before speech marks
    if settings["lang"] == "DE":
        s = fix_linebreaks_speech(s)

    # add spell macro
    if settings["lang"] == "DE":
        s = fix_spell(s)

    # spaces, again
    s = fix_spaces(s)
    return s


def fix_spaces(s: str) -> str:
    """Fix spaces."""
    # invisible strange spaces
    s = re.sub(r" +", " ", s)
    # tabs to space
    s = re.sub(r"\t+", " ", s)
    # trailing spaces
    s = re.sub(r" +$", "", s)
    # remove spaces from empty lines
    s = re.sub(r"^\s+$", "", s)
    # multiple spaces (excluding start of new line)
    s = re.sub(r"(?<!^)  +", " ", s)
    return s


def fix_ellipsis(s: str) -> str:
    """Fix spaces around ellipsis."""
    # ... -> …
    s = s.replace("...", "…")
    # remove all spaces around ellipsis
    s = re.sub(r" *… *", r"…", s)

    # after punctuation: add space
    s = re.sub(r"(?<=[\.\?!:,;])…", r" …", s)
    return s


def fix_latex(s: str) -> str:
    # Latex: \begin and \end{...} at new line
    s = re.sub(r"([^\s%]+)\s*\\(begin|end)\{", r"\1\n\\\2{", s)
    # Latex: \\ not followed by text
    s = re.sub(r"\\\\\s*(?!($|\[|%))", r"\\\\\n", s)
    if settings["lang"] != "EN":
        # \translatorsnote in newline
        s = re.sub(r"(?<!^)(\\translatorsnote)", r"%\n\1", s)
    return s


def fix_linebreaks_speech(s: str) -> str:
    """
    Add linebreaks before speech marks.

    not in use in EN
    """
    if settings["lang"] == "EN":
        return s

    if settings["lang"] == "DE":
        s = re.sub(r" „([A-Z])", r"\n„\1", s)

    return s


def fix_MrMrs(s: str) -> str:  # noqa: N802
    # Mr / Mrs
    s = s.replace("Mr. H. Potter", "Mr~H.~Potter")
    # s = s.replace("Mr. Potter", "Mr~Potter")
    if settings["lang"] == "DE":
        s = re.sub(r"\b(Mr|Mrs|Miss|Dr)\b\.?\s+(?!”)", r"\1~", s)
    # Dr.~ -> Dr~Potter etc.
    s = re.sub(r"\b(Mr|Mrs|Miss|Dr)\b\.~", r"\1~", s)
    return s


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
        s = s.replace("Junge-der-überlebt-hatte", "Junge-der-überlebte")
        s = s.replace("Junge-der-überlebt-hat", "Junge-der-überlebte")
        s = s.replace("Jungen-der-überlebt-hat", "Jungen-der-überlebte")
        s = s.replace("Junge, der lebte", "Junge-der-überlebte")
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


def fix_quotations(s: str) -> str:  # noqa: C901, PLR0912, PLR0915
    # in EN the quotations are “...” and ‘...’ (for quotations in quotations)
    # in DE the quotations are „...“ and ‚...‘ (for quotations in quotations)

    # TODO: add tests

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

    # space at opening "
    if settings["lang"] == "EN":
        s = re.sub(r"“ +", r"“", s)
    if settings["lang"] == "DE":
        s = re.sub(r"„ +", r"„", s)

    # space before closing “
    if settings["lang"] == "EN":
        s = re.sub(r" +”", r"”", s)
    if settings["lang"] == "DE":
        s = re.sub(r" +“", r"“", s)

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
    if settings["lang"] == "DE":
        s = re.sub(r"‚\\emph{([^}]+)}‘", r"‚\1‘", s)
        s = re.sub(r"\\emph{‚([^}]+)‘}", r"‚\1‘", s)

    # comma at end of emph and quotation
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

    # EN closing quotations
    if settings["lang"] == "DE":
        s = re.sub("”", "“", s)
        # s = re.sub("’", "’", s)

    # TODO: check for uneven quotations
    # if settings["lang"] == "DE":
    #     s = re.sub(r"(„[^“]+„)", r"<FIXME: quotations \1>", s)
    #     s = re.sub(r"(`)", r"<FIXME: quotations: \1>", s)

    #     if "\\\\" not in s:
    #         if s.count("„") != s.count("“"):
    #             s = "<FIXME: quotation „/“ mismatch> " + s
    #         if s.count("‚") != s.count("‘"):
    #             s = "<FIXME: quotation ‚/‘ mismatch> " + s

    return s


# assert fix_quotations("\parsel{Ich sehe nichts}“,")== "\parsel{Ich sehe nichts},“"


def fix_emph(s: str) -> str:
    # space at start of emph -> move before emph
    s = re.sub(r"(\\emph{) +", " \1", s)

    # move punctuation out of lowercase 1-word-emph
    # ... \emph{WORD.} -> \emph{WORD}.
    # Note: only for , and .
    if settings["lang"] == "EN" and "lettrinepara" not in s:
        # not \lettrinepara{W}{\emph{hat?}}:
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
    # if settings["lang"] == "EN":
    #     s = re.sub(r" [\-—]$", r"—", s) # rrthomas voted againt it
    if settings["lang"] == "DE":
        # end of line
        s = re.sub(r" [\-—]$", r"—", s)
    # - at end of emph
    s = re.sub(r"(\s*)\-\}", r"—}\1", s)
    # at start of quote
    # if settings["lang"] == "EN":
    #     s = re.sub(r"—“", r"— “", s) # rrthomas voted againt it
    if settings["lang"] == "DE":
        s = re.sub(r"\s*—„", r"— „", s)
        s = re.sub(r"„\s*—\s*", r"„—", s)

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


def fix_punctuation(s: str) -> str:
    """Fix 2x same punctuation: ,.!?:;"""  # noqa: D400, D415
    s = re.sub(r"([,\.!\?:;])\s*\1", r"\1", s)
    return s


def fix_spell(s: str) -> str:
    if settings["lang"] == "EN":
        # no spell macro in EN yet
        return s
    spells = {
        "Accio",
        "Alohomora",
        # "Avada Kedavra", not here, since sometimes in emph ok.
        "Aguamenti",
        "Cluthe",
        "Colloportus",
        "Contego",
        "Crystferrium",
        "Diffindo",
        "Deligitor prodeas",
        "Dulak",
        "Elmekia",
        "Episkey",
        "Expecto Patronum",
        "Expelliarmus",
        "Finite Incantatem",
        "Finite",
        "Flipendo",
        "Frigideiro",
        "Glisseo",
        "Gom jabbar",
        "Hyakuju montauk",
        "Homenum Revelio",
        "Impedimenta",
        # "Imperius", not as spell, as often used in text
        "Incendium",
        "Inflammare",
        "Innervate",
        "Jellify",
        "Lagann",
        "Lucis Gladius",
        "Luminos",
        "Lumos",
        "Mahasu",
        "Obliviate",
        "Oogely boogely",
        "Prismatis",
        "Polyfluis Reverso",
        "Protego",
        "Protego Maximus",
        "Quiescus",
        "Quietus",
        "Ravum Calvaria",
        "Rennervate",
        "Scourgify",
        "Steleus",
        "Ratzeputz",
        "Silencio",
        "Somnium",
        "Stupefy",
        "Stupor",
        "Thermos",
        "Tonare",
        "Ventriliquo",
        "Veritas Oculum",
        "Ventus",
        "Wingardium Leviosa",
    }
    spells_str = "(" + "|".join(spells) + ")"

    if settings["lang"] == "EN":
        for spell in spells:
            s = s.replace("‘" + spell + "’", "\\spell{" + spell + "}")
    if settings["lang"] == "DE":
        # \emph{spell}
        s = re.sub(r"\\emph{„?" + spells_str + r"[!\.“]?}", r"\\spell{\1}", s)
        # „\emph{spell}“
        s = re.sub(r"„\\emph{„?" + spells_str + r"[!\.]?“?}", r"\\spell{\1}“", s)
        # ‚spell‘
        s = re.sub(r"‚" + spells_str + r"!?‘", r"\\spell{\1}", s)
        # „spell“
        s = re.sub(r"„" + spells_str + r"!?“", r"\\spell{\1}", s)
        # " spell "
        # 2 false positives
        # s = re.sub(r"(?<= )" + spells_str + r"(?= )(?!\1)", r"\\spell{\1}", s)

    # \spell without !
    s = re.sub(r"(\\spell{[^}]+)!}", r"\1}", s)
    # \spell followed by ! -> remove !
    s = re.sub(r"(\\spell{[^}]+)}!", r"\1}", s)
    # no „...“ around \spell
    s = re.sub(r"„?(\\spell{[^}]+)}“?", r"\1}", s)

    # # some false positives
    # " Alohomora "
    # for spell in spells:
    #     s = re.sub(
    #         r"( |—)" + spell + r"( |—|,|\.|!)", r"\1\\spell{" + spell + r"}\2", s
    #     )
    # Imperius not as spell
    s = s.replace("\\spell{Imperius}", "Imperius")

    return s


if __name__ == "__main__":
    # cleanup first
    for file_out in Path("chapters").glob("*-autofix.tex"):
        file_out.unlink()

    list_of_chapter_files = get_list_of_chapter_files()

    # V2: using multiprocessing
    # prepare
    num_processes = min(cpu_count(), len(list_of_chapter_files))
    pool = Pool(processes=num_processes)
    # run
    results = pool.map(process_file, list_of_chapter_files)
    any_issue_found = True in results

    # V1: single processing
    # any_issue_found = False
    # for file_in in list_of_chapter_files:
    #     print(file_in.name)
    #     issue_found = process_file(file_in=file_in)
    #     if issue_found:
    #         any_issue_found = True

    if settings["raise_error"] and any_issue_found:
        msg = "Issues found, please fix!"
        raise Exception(msg)  # noqa: TRY002
