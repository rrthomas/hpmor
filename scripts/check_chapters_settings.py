# ruff: noqa: INP001

"""
Settings.

lang: EN, DE, FR, ...
raise_error: true -> script exits with error, used for autobuild of releases
print_diff: true : print line of issues
inline_fixing: modify the source file directly, USE WITH CAUTION
"""

settings = {
    "lang": "EN",
    "print_diff": True,
    "raise_error": True,
    "inline_fixing": False,
}
