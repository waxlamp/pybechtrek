from bs4 import BeautifulSoup
import os
import parsec
from pprint import pprint
import sys
import tempfile

import parser

from typing import Sequence, Optional


def get_title(doc: BeautifulSoup) -> Optional[str]:
    title_parts = doc.title.string.split('-')

    if len(title_parts) < 2:
        return None

    return '-'.join(title_parts[1:]).strip()


def get_dialog(doc: BeautifulSoup) -> Sequence[str]:
    elems = doc.select('table font')
    raw_lines = [item for elem in elems for item in elem.stripped_strings]

    lines = [l.replace('\n', ' ') for l in raw_lines]

    return lines


class StopProcessing(BaseException):
    pass


def edit(line):
    with tempfile.NamedTemporaryFile(mode='w+') as tmpfile:
        tmp = tmpfile.file
        name = tmpfile.name

        print(line, file=tmp)
        print('', file=tmp)
        print('##########', file=tmp)
        print('Edit the first line of this file to correct the parsing error', file=tmp)
        print('Write just the word \'join\' to join this line of text in its entirety to the previous line.', file=tmp)
        print('Write just the word \'exit\' to abandon processing this script.', file=tmp)
        tmp.flush()

        os.system(f'vim {name}')

        with open(name) as f:
            modified = f.readline()

        return modified.strip()


def parse_with_correction(line: str) -> str:
    # If the line parses just fine, then pass it through.
    result = parser.raw_line.parse(line)
    if result:
        return line

    # Otherwise, give the user a chance to fix the issue.
    modified = edit(line)

    # If the user issued a command, process it; otherwise, pass the edited line
    # through (after recurseively ensuring that it parses).
    if modified == 'exit':
        raise StopProcessing
    elif modified == 'join':
        return f'join:{line}'
    else:
        return parse_with_correction(modified)


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: bechtrek.py <scriptfilehtml>', file=sys.stderr)
        return 1

    htmlscriptfile = sys.argv[1]
    with open(htmlscriptfile, encoding='ISO-8859-1') as f:
        htmlscript = f.read()

    doc = BeautifulSoup(htmlscript, features='html.parser')

    title = get_title(doc)
    print(title)

    dialog = get_dialog(doc)
    modified = []
    for line in dialog:
        try:
            result = parse_with_correction(line)
        except StopProcessing:
            print('ending processing early', file=sys.stderr)
            return 1

        modified.append(result)

    pprint(modified)

    return 0


if __name__ == '__main__':
    sys.exit(main())
