#!/usr/bin/env python3

import re

def filter_lines(layout_name, lines, **edits):

    '''filters the lines of a symbols file and returns a generator where some
    of the keybindings have been changed or appended.

    Arguments:
    layout_name -- The name of the layout in the input to which the filter
                   should be applied. It is used to match lines like
                   'xkb_symbols "dvorak" {' with a regex. If no layout matches
                   in the input no filtering is applied.
    lines -- An iterable of the input to filter.

    Keyword arguments:
    edits -- The name of a keycode to create or replace in the output and an
             iterable of the keybindings to bind it to.
             Example AC01=('a', 'A', 'aring', 'Aring')
    '''

    def to_xkb_line(keycode, keybindings, indentation='  '):
        '''creates a string of the type:
            "  key <AC01> { [ a, A, aring, Aring ] };\n"

        Arguments:
        keycode -- Something like "AC01"
        keybindings -- An iterable like ('a', 'A', 'aring', 'Aring')

        Keyword arguments:
        indentation -- inserted at start of line (default: '  ')

        '''

        return '{}key <{}> {{ [ {} ] }};\n'.format(
                indentation,
                keycode,
                ', '.join(keybindings))

    #matches strings like 'xkb_symbols "dvorak" {'
    rx_start_of_layout = re.compile(r'\s*xkb_symbols\s*"{}"'.format(
        layout_name))
    line = next(lines)
    # Yield everything preceding the target layout unaltered
    while not rx_start_of_layout.search(line):
        yield line
        line = next(lines)

    indentation = '' 
    #matches string like "};"
    rx_end_of_layout = re.compile(r'^[^{]*}\s*;\s')
    # matches strings like "  key <AC01> { [ a, A ] };"
    rx_key_definition = re.compile(r'(\s*)(key\s*<\s*)([^\s>]*)')
    # Filter each line within the target layout
    while len(edits) > 0 and not rx_end_of_layout.search(line):
        keycode = None
        rx_search = rx_key_definition.search(line)
        if rx_search:
            indentation, _, keycode = rx_search.groups()
        yield to_xkb_line(keycode, edits.pop(keycode), indentation) \
                if keycode in edits \
                else line
        line = next(lines)

    # When at the end of the layout definition yield all the keyboard
    # definitions that have yet to be inserted. Sort the keys so the output
    # stays consistent.
    for keycode in sorted(edits.keys()):
        yield to_xkb_line(keycode, edits.pop(keycode), indentation)

    # Yield everything following the target layout unaltered
    yield line
    while True:
        yield next(lines)

if __name__ == '__main__':

    layout_name = 'dvorak'
    edits = {
        'AC01': ('a', 'A', 'aring', 'Aring'),
        'AC02': ('o', 'O', 'odiaeresis', 'Odiaeresis'),
        'AC03': ('e', 'E', 'adiaeresis', 'Adiaeresis'),
        'LSGT': ('dead_diaeresis', 'dead_abovering'),
        'CAPS': ('Escape',),
    }

    import sys
    assert len(sys.argv) < 3
    filename = sys.argv[len(sys.argv) - 1]
    with open(filename) as _file:
        lines = _file if len(sys.argv) > 1 else sys.stdin
        for line in filter_lines(layout_name, lines, **edits):
            print(line, end='')
