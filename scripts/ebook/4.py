#!/usr/bin/env python3
# by Torben Menke https://entorb.net
"""
Parselify flattened .tex file.
"""
import os
import re
import sys

os.chdir(os.path.dirname(sys.argv[0]) + "/../..")

source_file = "tmp/hpmor-epub-3-flatten-mod.tex"
target_file = "tmp/hpmor-epub-4-flatten-parsel.tex"

print("=== 4. parselify flattened file in python ===")


def convert_parsel(s: str) -> str:
    # small ss + ß -> sss ; s->ss
    s = s.replace("ss", "ß").replace("s", "ss").replace("ß", "sss")
    # capital S -> Ss ; capital SS -> SSS ; S->SS
    s = s.replace("SS", "ẞ").replace("S", "Ss").replace("ẞ", "SSS")
    # small zz -> zzz ; z->zz
    s = s.replace("zz", "ß").replace("z", "zz").replace("ß", "zzz")
    # capital Z -> Zz ; ZZ->ZZZ
    s = s.replace("ZZ", "ẞ").replace("Z", "Zz").replace("ß", "ZZZ")
    # small x -> xs
    s = s.replace("x", "xs")
    return s


with open(source_file, encoding="utf-8", newline="\n") as fhIn:
    cont = fhIn.read()


# \parsel
myMatches = re.finditer(r"(\\parsel\{([^\}\\]+)\})", cont)
for myMatch in myMatches:
    was = myMatch.group(1)
    womit = convert_parsel(myMatch.group(2))
    cont = cont.replace(was, "\\parsel{" + womit + "}")

with open(target_file, mode="w", encoding="utf-8", newline="\n") as fhOut:
    fhOut.write(cont)
