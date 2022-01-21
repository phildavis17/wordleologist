import pytest

from wordleologist import ColorRange, ColorBox

def test_cr_extant():
    cr = ColorRange()
    assert cr is not None

@pytest.fixture
def basic_color_range() -> "ColorRange":
    return ColorRange(min_color=(0, 255, 128), max_color=(255, 0, 128))

def test_color_range_position(basic_color_range: "ColorRange"):
    assert basic_color_range.color_from_position(0.0) == (0, 255, 128)
    assert basic_color_range.color_from_position(1.0) == (255, 0, 128)
    assert basic_color_range.color_from_position(0.5) == (127, 127, 128)

def test_color_range_number(basic_color_range: "ColorRange"):
    assert basic_color_range.color_from_number(0) == (0, 255, 128)
    assert basic_color_range.color_from_number(100) == (255, 0, 128)
    assert basic_color_range.color_from_number(50) == (127, 127, 128)

def test_cb_extant():
    cb = ColorBox()
    assert cb is not None

@pytest.fixture
def basic_color_box() -> "ColorBox":
    return ColorBox()

def test_color_box_position(basic_color_box: "ColorBox"):
    assert basic_color_box.color_from_positions(0.0, 0.0) == (0, 0, 0)
    assert basic_color_box.color_from_positions(0.0, 0.5) == (127, 127, 0)
    assert basic_color_box.color_from_positions(0.0, 1.0) == (255, 255, 0)
    assert basic_color_box.color_from_positions(0.5, 0.0) == (127, 127, 127)
    assert basic_color_box.color_from_positions(1.0, 0.0) == (255, 255, 255)
    assert basic_color_box.color_from_positions(0.5, 0.5) == (127, 127, 127)
    assert basic_color_box.color_from_positions(1.0, 1.0) == (0, 0, 255)
