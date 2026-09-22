"""Unit Tests."""  # noqa: INP001

from step_6 import fix_ellipsis

test_cases = [
    # quotations
    ("foo…”", "foo…”"),
    ("“…foo", "“…foo"),
    # html
    ("foo…</p>", "foo…</p>"),
    ("<p>…foo", "<p>…foo"),
    # between 2 words
    ("foo…bar", "foo… bar"),
    ("foo …bar", "foo… bar"),
    ("foo … bar", "foo… bar"),
    ("foo… bar", "foo… bar"),
    # start of sentence
    ("foo.…bar", "foo. …bar"),
    ("foo!…bar", "foo! …bar"),
    ("foo?…bar", "foo? …bar"),
    # end of sentence
    ("foo…. bar", "foo…. bar"),
    ("foo…! bar", "foo…! bar"),
    ("foo…? bar", "foo…? bar"),
    # emph
    ("foo</em>…bar", "foo</em>… bar"),
    ("foo…<em>bar", "foo… <em>bar"),
]


def test_fix_ellipsis() -> None:
    """Test fix_ellipsis."""
    for inp, exp in test_cases:
        assert fix_ellipsis(inp) == exp, fix_ellipsis(inp)
