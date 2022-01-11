import pytest

from wordleologist import WordleTrainer, ColorRange, ColorBox

def test_wt_extant():
    w = WordleTrainer()
    assert w is not None

def test_cr_extant():
    cr = ColorRange()
    assert cr is not None

def test_cb_extant():
    cb = ColorBox()
    assert cb is not None
