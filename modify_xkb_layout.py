#!/usr/bin/env python

import re
import sys

MODLINE = "// modified by me"
DVORAK_RE = re.compile(r'xkb_symbols\s+"dvorak"\s+{')


filename = sys.argv[1]
modify = True
with open(filename) as f:
    line = next(f)
    print(MODLINE)
    if line.strip() == MODLINE:
        for line in f:
            print(line, end='')
    else:
        print(line, end='')
    for line in f:
        if DVORAK_RE.match(line.strip()):
            print(line, end='')
            print("""\
// BEGIN MODIFIED
    name[Group1]= "English (Dvorak, modified)";
    include "us(dvorak-std)"

    key <AC01> { [ a, A, aring,       Aring      ] };
    key <AC02> { [ o, O, odiaeresis,  Odiaeresis ] };
    key <AC03> { [ e, E, adiaeresis,  Adiaeresis ] };
    key <AC09> { [ n, N, ntilde,      Ntilde     ] };
    key <AD10> { [ l, L, dead_stroke, dead_acute ] };
    key <LSGT> { [ dead_diaeresis, dead_abovering, dead_tilde, dead_stroke ] };
    key <CAPS> { [ Escape ] };
    include "level3(ralt_switch)"
};

partial alphanumeric_keys
xkb_symbols "dvorak-std" {
// END MODIFIED""")
        else:
            print(line, end='')
