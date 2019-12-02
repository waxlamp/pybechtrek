# import re
from parsec import *


whitespace = regex(r'\s*', re.MULTILINE)

lexeme = lambda x: string(x) << whitespace

@generate
def stagedir():
    yield lexeme('(')
    text = yield many(none_of(')'))
    yield lexeme(')')

    return f'stagedir: {"".join(text)}'


@generate
def scene():
    yield lexeme('[')
    text = yield many(none_of(']'))
    yield lexeme(']')

    return f'scene: {"".join(text)}'


def note():
    @generate
    def try_note():
        yield lexeme('[')
        note = yield many(none_of(']'))
        yield lexeme(']')

        return ''.join(note)

    @generate
    def failed():
        yield lexeme('')

        return None

    return try_note ^ failed


@generate
def raw_role():
    raw_name = yield many(none_of(':['))
    role_note = yield note()

    name = ''.join(raw_name).strip()

    return f'role({name}, {role_note})'


@generate
def log():
    raw_text = yield many(none_of(''))
    text = ''.join(raw_text).strip()

    def is_log(t):
        phrases = [
            'star date',
            'stardate',
            'log'
        ]
        return any(phrase in t.lower() for phrase in phrases)

    if is_log(text):
        return f'log: {text}'


@generate
def line():
    role = yield raw_role
    yield lexeme(':')
    line = yield many(none_of(''))

    return f'line: {role}, {"".join(line)}'


raw_line = stagedir ^ scene ^ line ^ log
