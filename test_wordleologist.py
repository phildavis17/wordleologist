import pytest

from wordleologist import WordleTrainer, ColorRange, ColorBox

def test_wt_extant():
    w = WordleTrainer()
    assert w is not None


