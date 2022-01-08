import pytest

from wordleologist import Wordle

def test_extant():
    w = Wordle()
    assert w is not None

