"""Tests for check_chapters.py ."""  # noqa: INP001
# ruff: noqa: RUF001, D103

from typing import TYPE_CHECKING

import pytest
from check_chapters import (
    fix_common_typos,
    fix_ellipsis,
    fix_emph,
    fix_hyphens,
    fix_latex,
    fix_line,
    fix_linebreaks_speech,
    fix_MrMrs,
    fix_numbers,
    fix_punctuation,
    fix_spaces,
    fix_spell,
)
from check_chapters_settings import settings

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_common_typos(lang: str) -> None:
    settings["lang"] = lang
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
    check_it(fix_common_typos, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_ellipsis(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("foo…bar", "foo…bar"),
        ("foo … bar", "foo…bar"),
        ("foo… bar", "foo…bar"),
        ("foo …bar", "foo…bar"),
        ("foo, …", "foo, …"),
    ]
    check_it(fix_ellipsis, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_emph(lang: str) -> None:
    settings["lang"] = lang
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
    check_it(fix_emph, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_hyphens(lang: str) -> None:
    settings["lang"] = lang
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
    check_it(fix_hyphens, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_latex(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("begin at new line\\begin{em}", "begin at new line\n\\begin{em}"),
        ("end at new line\\end{em}", "end at new line\n\\end{em}"),
        ("new line after \\\\ asdf", "new line after \\\\\nasdf"),
        ("no new line after \\\\", "no new line after \\\\"),
    ]
    check_it(fix_latex, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_linebreaks_speech(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        (" „Hello", "\n„Hello"),
        (" „hello", " „hello"),
        ("„hello", "„hello"),
    ]
    check_it(fix_linebreaks_speech, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_mr_mrs(lang: str) -> None:
    settings["lang"] = lang
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
    check_it(fix_MrMrs, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_numbers(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("Es ist 12:23 Uhr.", "Es ist 12:23~Uhr."),
        ("asdf", "asdf"),
    ]
    check_it(fix_numbers, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_punctuation(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("!!", "!"),
        ("??", "?"),
        ("! !", "!"),
        ("..", "."),
        (",,", ","),
    ]
    check_it(fix_punctuation, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_spaces(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("Hallo  Harry", "Hallo Harry"),
        ("tabs\tto\t\tspace", "tabs to space"),
        ("trailing spaces  ", "trailing spaces"),
        ("  ", ""),
        ("multiple  spaces", "multiple spaces"),
    ]
    check_it(fix_spaces, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_spell(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        (r"‚Lumos‘", r"\spell{Lumos}"),
        (r"„Lumos“", r"\spell{Lumos}"),
        (r"„\emph{Lumos}“", r"\spell{Lumos}"),
        (r"\emph{„Lumos“}", r"\spell{Lumos}"),
        (r"\emph{Lumos!}", r"\spell{Lumos}"),
        (r"„\spell{Lumos}“", r"\spell{Lumos}"),
    ]
    check_it(fix_spell, pairs)


def check_it(fct: Callable, pairs: list[tuple[str, str]]) -> None:
    for text, expected_output in pairs:
        # test of isolated function
        assert fct(text) == expected_output, f"'{fct(text)}' != '{expected_output}'"
        # test in complete fix_line context
        assert fix_line(text) == expected_output, (
            f"'{fix_line(text)}' != '{expected_output}'"
        )
