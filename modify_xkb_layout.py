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

    def to_xkb_line(
            keycode,
            keybindings,
            indentation='  '):
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

    # matches strings like "  key <AC01> { [ a, A ] };"
    rx_key_definition = re.compile(r'(\s*)(key\s*<\s*)([^\s>]*)')
    #matches strings like 'xkb_symbols "dvorak" {'
    rx_start_of_layout = re.compile(r'\s*xkb_symbols\s*"{}"'.format(
        layout_name))
    #matches string like "};"
    rx_end_of_layout = re.compile(r'^[^{]*}\s*;\s')

    indentation = '' 
    def filter_line(line):
        ''' If the line defines a keybinding in 'edits' a keybinding based on
        the value in edits is used, otherwise the line is returned as is

        '''

        nonlocal indentation
        rx_search = rx_key_definition.search(line)
        if rx_search:
            keycode = rx_search.groups()[2]
            if keycode in edits:
                indentation = rx_search.groups()[0]
                line = to_xkb_line(
                        keycode,
                        edits.pop(keycode),
                        indentation)
        return line
    
    applying_filter = False
    for line in lines:
        if applying_filter and rx_end_of_layout.search(line):
            while len(edits) > 0:
                k, v = edits.popitem()
                yield to_xkb_line(k, v, indentation)
            applying_filter=False
        if applying_filter:
            line = filter_line(line)
        if not applying_filter:
            if len(edits) > 0 and rx_start_of_layout.search(line):
                applying_filter = True
        yield line

if __name__ == '__main__':

    layout_name = 'dvorak'
    edits = {
        'AC01': ('a', 'A', 'aring', 'Aring'),
        'AC02': ('o', 'O', 'odiaeresis', 'Odiaeresis'),
        'AC03': ('e', 'e', 'adiaeresis', 'Adiaeresis'),
        'LSGT': ('dead_diaeresis', 'dead_abovering'),
        'CAPS': ('Escape',),
    }

    import sys
    filename = sys.argv[0]
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    with open(filename) as _file:
        lines = _file if len(sys.argv) > 1 else sys.stdin
        for line in filter_lines(layout_name, lines, **edits):
            print(line, end='')
