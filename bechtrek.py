from bs4 import BeautifulSoup
import parsec
from pprint import pprint
import sys

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
    for line in dialog:
        result = parser.raw_line.parse(line)

        print(result)

    return 0


if __name__ == '__main__':
    sys.exit(main())
