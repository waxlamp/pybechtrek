from bs4 import BeautifulSoup
import os
import parsec
from pprint import pprint
import sys
import tempfile

import parser

from typing import Sequence, Optional, List, cast


def get_editor() -> str:
    return os.environ.get('EDITOR', 'vi')


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


def edit(line: str) -> str:
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

        os.system(f'{get_editor()} {name}')

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


def stitch(lines: Sequence[str]) -> List[str]:
    out: List[str] = []
    for line in lines:
        if line.startswith('join:'):
            line = line.split('join:')[1]
            out[-1] += line
        else:
            out.append(line)

    return out


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: bechtrek.py <scriptfilehtml>', file=sys.stderr)
        return 1

    # Open the script file.
    htmlscriptfile = sys.argv[1]
    with open(htmlscriptfile, encoding='ISO-8859-1') as f:
        htmlscript = f.read()

    # Parse it.
    doc = BeautifulSoup(htmlscript, features='html.parser')

    # Grab the episode title.
    title = get_title(doc)
    print(title)

    # Grab the dialog lines.
    dialog = get_dialog(doc)

    # Attempt to parse each line; open an editor and let the user fix any
    # problems that are found.
    modified = []
    for line in dialog:
        try:
            result = parse_with_correction(line)
        except StopProcessing:
            print('ending processing early', file=sys.stderr)
            return 1

        modified.append(result)

    # Execute any "join" commands inserted into the script process.
    modified = stitch(modified)

    # Re-parse the corrected lines.
    parse = cast(List[parser.ParseObject], [parser.raw_line.parse(line) for line in modified])

    # Dump to stdout.
    for p in parse:
        print(p.encode())

    return 0


if __name__ == '__main__':
    sys.exit(main())
