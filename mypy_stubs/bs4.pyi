from typing import Iterable, Iterator


class BeautifulSoup(Iterable):
    title: BeautifulSoup
    string: str
    stripped_strings: Iterator[str]

    def __init__(self, f: str, features: str): ...
    def select(self, css: str) -> BeautifulSoup: ...
    def __iter__(self) -> Iterator[BeautifulSoup]: ...
