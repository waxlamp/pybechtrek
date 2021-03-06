from typing import Any, Callable, Tuple


class Parser(object):
    def __lshift__(self, other: Parser) -> Parser: ...
    def __xor__(self, other: Parser) -> Parser: ...

    def parse(self, text: str) -> Tuple[Any, str]: ...


def regex(exp: str, flags: int = 0) -> Parser: ...
def string(s: str) -> Parser: ...
def generate(fn: Callable[[], Any]) -> Parser: ...
def many(p: Parser) -> Parser: ...
def one_of(s: str) -> Parser: ...
def none_of(s: str) -> Parser: ...
