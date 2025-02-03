"""Tests for check_chapters.py ."""  # noqa: INP001
# ruff: noqa: S101 RUF001 RUF003 D103

from collections.abc import Callable

from check_chapters import (
    fix_common_typos,
    fix_ellipsis,
    fix_emph,
    fix_hyphens,
    fix_latex,
    fix_line,
    fix_linebreaks_speach,
    fix_MrMrs,
    fix_numbers,
    fix_punctuation,
    fix_spaces,
    fix_spell,
)
from check_chapters_settings import settings


def test_it(fct: Callable, pairs: list[tuple[str, str]]) -> None:
    for text, expected_output in pairs:
        # test of isolated function
        assert fct(text) == expected_output, f"'{fct(text)}' != '{expected_output}'"
        # test in complete fix_line context
        assert fix_line(text) == expected_output, (
            f"'{fix_line(text)}' != '{expected_output}'"
        )


for lang in ["EN", "DE"]:
    settings["lang"] = lang

    #
    # fix_common_typos
    #
    pairs = [
        ("Test Mungo's King's Cross", "Test Mungo’s King’s Cross"),
        ("Test", "Test"),
    ]
    if lang == "EN":
        pairs.extend(
            [
                ("I'm happy", "I’m happy"),
                ("can't be", "can’t be"),
            ]
        )
    elif lang == "DE":
        pairs.extend(
            [
                ("Junge-der-überlebt-hat", "Junge-der-überlebte"),
                ("Fritz'sche Gesetz", "Fritz’sche Gesetz"),
                ("Fritz'schen Gesetz", "Fritz’schen Gesetz"),
                ("Fritz'scher Gesetz", "Fritz’scher Gesetz"),
            ]
        )
    test_it(fix_common_typos, pairs)

    #
    # fix_ellipsis
    #
    pairs = [
        ("foo…bar", "foo…bar"),
        ("foo … bar", "foo…bar"),
        ("foo… bar", "foo…bar"),
        ("foo …bar", "foo…bar"),
        ("foo, …", "foo, …"),
    ]
    test_it(fix_ellipsis, pairs)

    #
    # fix_emph
    #
    pairs = [
        (r"That’s not \emph{true!}", r"That’s not \emph{true}!"),
        (r"she got \emph{magic,} can you", r"she got \emph{magic}, can you"),
        ("asdf", "asdf"),
    ]
    if lang == "EN":
        pairs.extend(
            [
                (
                    r"briefly. \emph{Hopeless.} Both",
                    r"briefly. \emph{Hopeless.} Both",  # . unchanged
                ),
                ("asdf", "asdf"),
            ]
        )
    elif lang == "DE":
        pairs.extend(
            [
                (
                    r"briefly. \emph{Hopeless.} Both",
                    r"briefly. \emph{Hopeless}. Both",  # . now out
                ),
                ("asdf", "asdf"),
            ]
        )
        test_it(fix_emph, pairs)

    #
    # fix_hyphens
    #
    pairs = [
        ("2-3-4", "2–3–4"),
        (" —,", "—,"),
        (" —.", "—."),
        (" —!", "—!"),
        (" —?", "—?"),
        # start of line
        ("— asdf", "—asdf"),
        ("- asdf", "—asdf"),
        ("-asdf", "—asdf"),
    ]
    if lang == "DE":
        pairs.extend(
            [
                # end of line
                ("Text —", "Text—"),
                # start of quote
                ("Text—„", "Text— „"),
                ("Text —„", "Text— „"),
                ("Text „ —Quote", "Text „—Quote"),
                ("Text „ — Quote", "Text „—Quote"),
                ("Text—„— Quote", "Text— „—Quote"),
                # end of quote
                ("Text -“asdf", "Text—“ asdf"),
                ("Text —“", "Text—“"),
            ]
        )
    test_it(fix_hyphens, pairs)

    #
    # fix_latex
    #
    pairs = [
        ("begin at new line\\begin{em}", "begin at new line\n\\begin{em}"),
        ("end at new line\\end{em}", "end at new line\n\\end{em}"),
        ("new line after \\\\ asdf", "new line after \\\\\nasdf"),
        ("no new line after \\\\", "no new line after \\\\"),
    ]
    test_it(fix_latex, pairs)

    #
    # fix_linebreaks_speach
    #
    if lang == "DE":
        pairs = [
            (" „Hello", "\n„Hello"),
            (" „hello", " „hello"),
            ("„hello", "„hello"),
        ]
        test_it(fix_linebreaks_speach, pairs)

    #
    # fix_MrMrs
    #
    pairs = [
        ("Mr. H. Potter", "Mr~H.~Potter"),
        ("it’s Doctor now, not Miss.", "it’s Doctor now, not Miss."),
    ]
    if lang == "DE":
        pairs.extend(
            [
                ("Mr. Potter", "Mr~Potter"),
                ("Mrs. Potter", "Mrs~Potter"),
                ("Miss. Potter", "Miss~Potter"),
                ("Dr. Potter", "Dr~Potter"),
                ("Dr Potter", "Dr~Potter"),
                ("Mr Potter", "Mr~Potter"),
                ("Mr. and Mrs. Davis", "Mr~and Mrs~Davis"),
            ]
        )
    test_it(fix_MrMrs, pairs)

    #
    # fix_numbers
    #
    if lang == "DE":
        pairs = [
            ("Es ist 12:23 Uhr.", "Es ist 12:23~Uhr."),
            ("asdf", "asdf"),
        ]
        test_it(fix_numbers, pairs)

    #
    # fix_punctuation
    #
    pairs = [
        ("!!", "!"),
        ("??", "?"),
        ("! !", "!"),
        ("..", "."),
        (",,", ","),
    ]
    test_it(fix_punctuation, pairs)

    #
    # fix_spaces
    #
    pairs = [
        ("Hallo  Harry", "Hallo Harry"),
        ("tabs\tto\t\tspace", "tabs to space"),
        ("trailing spaces  ", "trailing spaces"),
        ("  ", ""),
        ("multiple  spaces", "multiple spaces"),
    ]
    test_it(fix_spaces, pairs)

    #
    # fix_spell
    #
    if lang == "DE":
        pairs = [
            (r"‚Lumos‘", r"\spell{Lumos}"),
            (r"„Lumos“", r"\spell{Lumos}"),
            (r"„\emph{Lumos}“", r"\spell{Lumos}"),
            (r"\emph{„Lumos“}", r"\spell{Lumos}"),
            (r"\emph{Lumos!}", r"\spell{Lumos}"),
            (r"„\spell{Lumos}“", r"\spell{Lumos}"),
        ]
        test_it(fix_spell, pairs)
