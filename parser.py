from dataclasses import dataclass
from dataclasses_json import dataclass_json
from parsec import *
import re

from typing import Any, Generator, Optional, TypeVar, Generic


T = TypeVar('T')
ParserCombinator = Generator[Parser, Any, T]

whitespace = regex(r'\s*', re.MULTILINE)

def lexeme(s: str) -> Parser:
    return string(s) << whitespace


class ParseObject(object):
    pass

@dataclass_json
@dataclass
class StageDirection(ParseObject):
    direction: str


@dataclass_json
@dataclass
class Scene(ParseObject):
    description: str


@dataclass_json
@dataclass
class Role(ParseObject):
    name: str
    note: Optional[str]


@dataclass_json
@dataclass
class Line(ParseObject):
    role: Role
    dialog: str


@generate
def stagedir() -> ParserCombinator[StageDirection]:
    yield lexeme('(')
    text = yield many(none_of(')'))
    yield lexeme(')')

    return StageDirection(direction=''.join(text))


@generate
def scene() -> ParserCombinator[Scene]:
    yield lexeme('[')
    text = yield many(none_of(']'))
    yield lexeme(']')

    return Scene(description=''.join(text))


def note() -> Parser:
    @generate
    def try_note() -> ParserCombinator[str]:
        yield lexeme('[')
        note = yield many(none_of(']'))
        yield lexeme(']')

        return ''.join(note)

    @generate
    def failed() -> ParserCombinator[None]:
        yield lexeme('')

        return None

    return try_note ^ failed


@generate
def raw_role() -> ParserCombinator[Role]:
    raw_name = yield many(none_of(':['))
    role_note = yield note()

    name = ''.join(raw_name).strip()

    return Role(name=name, note=role_note)


@generate
def log() -> ParserCombinator[Optional[Line]]:
    raw_text = yield many(none_of(''))
    text = ''.join(raw_text).strip()

    def is_log(t: str) -> bool:
        phrases = [
            'star date',
            'stardate',
            'log'
        ]
        return any(phrase in t.lower() for phrase in phrases)

    if is_log(text):
        return Line(role=Role(name='UNKNOWN', note=None),
                    dialog=text)
    else:
        return None


@generate
def line() -> ParserCombinator[Line]:
    role = yield raw_role
    yield lexeme(':')
    line = yield many(none_of(''))

    return Line(role=role, dialog=''.join(line))


raw_line = stagedir ^ scene ^ line ^ log
