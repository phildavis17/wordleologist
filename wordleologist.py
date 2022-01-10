import argparse
import enum
import os
import random
import string
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

import rich

SCRABBLE_WORDS_PATH = Path(__file__).parent / "data" / "Collins Scrabble Words (2019).txt"

with open(SCRABBLE_WORDS_PATH) as scrabble_words:
    SCRABBLE_WORDS = {word.strip() for word in scrabble_words.readlines()}


class ColorRange:
    """Maps a range of colors to a color gradient."""

    def __init__(self, min: int = 0, max: int = 100, min_color: Tuple[int, int, int] = None, max_color: Tuple[int, int, int] = None) -> None:
        self.min: int = min
        self.max: int = max
        self.min_color: tuple = min_color
        self.max_color: tuple = max_color
        if self.min_color is None:
            self.min_color = (0, 0, 0)
        if self.max_color is None:
            self.max_color = (255, 255, 255)
    
    def color_from_number(self, n: int) -> Tuple[int, int, int]:
        """Returns an interpolated rgb tuple based on a number within the established range."""
        if not self.min <= n <= self.max:
            raise ValueError(f"{n} exceeds range bounds ({self.min}, {self.max})")
        pos = (n - self.min) / (self.max - self.min)
        return self.color_from_position(pos)
        
    def color_from_position(self, pos: float) -> Tuple[int, int, int]:
        """Returns an interpolated rgb tuple based on a decimal number between 0 and 1."""
        if not 0.0 <= pos <= 1.0:
            raise ValueError(f"pos must be between 0 and 1, not {pos}")
        return tuple([int(min_val + (max_val - min_val) * pos) for min_val, max_val in zip(self.min_color, self.max_color)])
    
    @staticmethod
    def rich_format_rgb(rgb: tuple) -> str:
        """Returns a string that describes the supplied rgb tuple in a way rich can understand."""
        r, g, b = rgb
        return f"rgb({r},{g},{b})"
    
    def demo(self, count: int = 10) -> None:
        """Prints a """
        start = self.min
        stop = self.max
        print(repr(self))
        for n in range(count):
            pos = n / (count - 1)
            num = int(start + (stop - start) * (n / (count - 1)))
            rich.print(f"{'{:.2f}'.format(pos)} [{self.rich_format_rgb(self.color_from_number(num))}]████ Demo ████[/] {num}")

    def __repr__(self) -> str:
        return f"ColorRange({self.min}, {self.max})"


class ColorBox:
    def __init__(
        self, 
        x_bounds: Tuple[int, int] = (0, 100),
        y_bounds: Tuple[int, int] = (0, 100), 
        upper_colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = None,
        lower_colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = None,
        ) -> None:
        self.x_min, self.x_max = x_bounds
        self.y_min, self.y_max = y_bounds
        if upper_colors is None:
            upper_colors = ((255, 255, 0), (0, 0, 255))
        if lower_colors is None:
            lower_colors = ((0, 0, 0), (255, 255, 255))
        upper_start, upper_stop = upper_colors
        lower_start, lower_stop = lower_colors
        self.upper_range = ColorRange(self.x_min, self.x_max, upper_start, upper_stop)
        self.lower_range = ColorRange(self.x_min, self.x_max, lower_start, lower_stop)
    
    def color_from_numbers(self, x: int, y: int) -> Tuple[int, int, int]:
        upper = self.upper_range.color_from_number(x)
        lower = self.lower_range.color_from_number(x)
        vertical = ColorRange(self.y_min, self.y_max, lower, upper)
        return vertical.color_from_number(y)

    def color_from_positions(self, x: float, y: float) -> Tuple[int, int, int]:
        upper = self.upper_range.color_from_position(x)
        lower = self.lower_range.color_from_position(x)
        vertical = ColorRange(self.y_min, self.y_max, lower, upper)
        return vertical.color_from_position(y)

    @staticmethod
    def rich_format_rgb(rgb: Tuple[int, int, int]):
        """Returns a string that describes the supplied rgb tuple in a way rich can understand."""
        r, g, b = rgb
        return f"rgb({r},{g},{b})"

    def demo(self, count: int = 10) -> None:
        for y in range(count):
            y_pos = y / (count - 1)
            row = []
            for x in range(count):
                x_pos = x / (count - 1)
                row.extend([f"[{self.rich_format_rgb(self.color_from_positions(x_pos, y_pos))}]", "█", "[/]"])
            rich.print("".join(row))

                
    def __repr__(self) -> str:
        pass


class OutputColor(Enum):
    """
    This Enum describes the colors used in the OutputStyle Enum.
    These are stored apart from the style as a whole to allow for simpler numerical operations on color.
    """
    GREEN = (0, 192, 50)
    YELLOW = (228, 208, 0)
    GRAY = (98, 98, 98)
    WHITE = (208, 208, 208)


class OutputStyle(Enum):
    """
    This Enum contains the rich style descriptions used for evlauating guesses.
    It uses the numerical values from the OutputColor Enum.
    """
    GREEN = f"bold rgb({','.join([str(n) for n in OutputColor.GREEN.value])})"
    YELLOW = f"bold rgb({','.join([str(n) for n in OutputColor.YELLOW.value])})"
    GRAY = f"bold rgb({','.join([str(n) for n in OutputColor.GRAY.value])})"
    WHITE = f"bold rgb({','.join([str(n) for n in OutputColor.WHITE.value])})"

class BadWordException(Exception):
    pass

class WordleTrainer:
    FIVE_LETTER_WORDS = {word for word in SCRABBLE_WORDS if len(word) == 5}
    STANDARD_MESSAGES = {
        "turn": "\nPlease enter your guess: ",
        "bad turn": "\nPlease enter a valid 5 letter word: ",
        "win": "\nCongratulations!",
        "lose": "\nBetter luck next time!",
    }

    def __init__(self, target_word: Optional[str] = None) -> None:
        self.target_word = target_word
        self.possible_letters = {x: set(string.ascii_uppercase) for x in range(5)}
        self.known_alphabet = {c: OutputStyle.WHITE.value for c in string.ascii_uppercase}
        self.included: set = set()
        self.excluded: set = set()
        self.guessed_words: list = []

    @classmethod
    def new_random_wordle(cls) -> "WordleTrainer":
        """Creates a new Wordle object with a randomly selected target word."""
        return WordleTrainer(random.choice(tuple(cls.FIVE_LETTER_WORDS)))
    
    def _build_guess_evaluation(self, guess: str) -> tuple:
        """Creates a tuple of rich styles to match the evaluation of each character in the supplied guess."""
        return tuple([self._evaluate_guess_char(i, c) for i, c in enumerate(guess)])
    
    def _build_rich_response_string(self, guess: str) -> str:
        """Creates a string with rich style markup tags for the supplied guess. """
        response: list = []
        for style, char in zip(self._build_guess_evaluation(guess), guess):
            response = response + [f"[{style}]{char}[/]"]
        return "".join(response)
    
    def rich_print_guess_response(self, guess: str) -> None:
        """Uses rich to print a stylized guess string."""
        rich.print(self._build_rich_response_string(guess))

    def _validate_guess(self, guess: str) -> bool:
        """Returns True if a supplied guess is valid."""
        if len(guess) != 5:
            return False
        if self.target_word is None:
            raise RuntimeError(f"Target word not set")
        if guess.upper() not in self.FIVE_LETTER_WORDS:
            return False
        return True
    
    def _evaluate_guess_char(self, index: int, guess_char: str) -> str:
        """
        Returns a rich markup style to match the evaluation of a supplied character,
        and updates the known alphabet accordingly.
        """
        if self.target_word[index] == guess_char:
            self.known_alphabet[guess_char] = OutputStyle.GREEN.value
            return OutputStyle.GREEN.value
        elif guess_char in self.target_word:
            if not self.known_alphabet[guess_char] == OutputStyle.GREEN.value:
                self.known_alphabet[guess_char] = OutputStyle.YELLOW.value
            return OutputStyle.YELLOW.value
        else:
            self.known_alphabet[guess_char] = OutputStyle.GRAY.value
            return OutputStyle.GRAY.value

    def _get_valid_turn(self) -> str:
        """Prompts the user for turns until they provide a valid one."""
        guess = self._request_turn()
        while not self._validate_guess(guess):
            guess = self._request_turn(self.STANDARD_MESSAGES["bad turn"])
        return guess.upper()

    @classmethod
    def _request_turn(cls, message: Optional[str] = None) -> str:
        """Prompts the user for a guess."""
        if message is None:
            message = cls.STANDARD_MESSAGES["turn"]
        print(message, end="")
        guess = input()
        return guess

    def play(self) -> None:
        print("Welcome to wordleologist!\n")
        while self.target_word not in self.guessed_words and len(self.guessed_words) < 6:
            self.guessed_words.append(self._get_valid_turn())
            self.clear_console()
            for word in self.guessed_words:
                self.rich_print_guess_response(word)
            self.rich_print_alphabet()
        if self.target_word in self.guessed_words:
            print("Congratulations!")
        else:
            rich.print(f"\nWe were looking for [{OutputStyle.GREEN.value}]{self.target_word}[/]")
            print("Better luck next time!")

    def _build_alphabet_string(self) -> str:
        styled_alpha = ["\n"]
        for char, style in self.known_alphabet.items():
            styled_alpha.extend([f"[{style}]", char, "[/] "])
        return "".join(styled_alpha)

    def rich_print_alphabet(self) -> None:
        rich.print(self._build_alphabet_string())
    
    @staticmethod
    def clear_console():
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')

    def conclude(self) -> None:
        pass

    @property
    def frequencies(self) -> Counter:
        """The character frequency counts for characters in remaining possible words."""
        freq: Counter = Counter()
        for word in self.possible_words:
            freq.update(set(word))
        return freq
    
    @property
    def possible_words(self) -> set:
        """The set of words that can possibly be the target word, based on current information."""
        remaining_words = WordleTrainer._filter_by_inlcuded(self.included, self.FIVE_LETTER_WORDS)
        for index, letters in self.possible_letters.items():
            remaining_words = WordleTrainer._filter_by_letter(index, letters, remaining_words)
        return remaining_words
    
    @property
    def index_frequencies(self) -> dict:
        return {i: Counter(chars) for i, chars in enumerate(zip(*self.possible_words))}

    @staticmethod
    def _filter_by_inlcuded(included: set, words: set) -> set:
        """Returns the supplied set of words stripped of all words that do not contain letters that must appear in the target word."""
        bad_words = set()
        for char in included:
            for word in words:
                if char not in word:
                    bad_words.add(word)
            words = words.difference(bad_words)
            bad_words = set()
        return words

    @staticmethod
    def _filter_by_letter(index: int, possible: set, words: set) -> set:
        """Returns the supplied set of words stripped of all words that contain errant letters at any index."""
        bad_words = set()
        for word in words:
            if word[index] not in possible:
                bad_words.add(word)
        return words.difference(bad_words)

    def exclude(self, bad_chars: str) -> None:
        """Removes the supplied characters from all sets of possible characters."""
        for index in self.possible_letters:
            self.exclude_at_index(index, bad_chars)
    
    def exclude_at_index(self, index: int, bad_chars: str) -> None:
        """Removes the supplied characters from the set of possible characters at the supplied index,."""
        self.possible_letters[index] = self.possible_letters[index].difference(set(bad_chars))

    def include(self, good_chars: str):
        """Adds supplied characters to the set of letters that must appear in the target word."""
        self.included.update(set(good_chars))

    def assign_at_index(self, index: int, char: str):
        """
        Reduces the set of possible letters at the supplied index to a single supplied letter.
        Do this with green letters.
        """
        if len(char) != 1:
            raise ValueError(f"Tried to assign a string with improper number of characters: {char}")
        self.possible_letters[index] = set(char)
        self.included.add(char)

    def _build_prediction_str(self, guess: str) -> str:
        cb = ColorBox(upper_colors=(OutputColor.YELLOW.value, OutputColor.GREEN.value), lower_colors=(OutputColor.GRAY.value,OutputColor.GRAY.value))
        num_words = len(self.possible_words)
        total_freq = self.frequencies
        index_freq = self.index_frequencies
        prediction = []
        for i, c in enumerate(guess):
            presence_freq = total_freq[c] / num_words
            if total_freq[c] == 0:
                idx_freq = 0.0
            else:
                idx_freq = index_freq[i][c] / total_freq[c]
            prediction.extend([f"[{cb.rich_format_rgb(cb.color_from_positions(idx_freq, presence_freq))}]", c, "[/]"])
        return "".join(prediction)
        
    def rich_print_prediction_str(self, guess: str) -> None:
        rich.print(self._build_prediction_str(guess))
        
    def find_best_guess(self, hardmode: bool = False):
        """Returns the word with the highest frequency score that could also be the target word."""
        freq = self.frequencies
        best_score = 0
        best_guesses = []
        if hardmode:
            word_set = self.possible_words
        else:
            word_set = self.FIVE_LETTER_WORDS
        for word in word_set:
            score = self._get_frequency_score(word, freq)
            if score == best_score:
                best_guesses.append(word)
            elif score > best_score:
                best_score = score
                best_guesses = [word]
        return random.choice(best_guesses)
            
    def _get_frequency_score(self, word: str, freq: Optional[Counter] = None) -> int:
        """
        Returns the sum of frequency scores by character in a supplied word, excluding characters that must be included in the target word.
        A heuristic for the amount of information gained by guessing that word.
        """
        if freq is None:
            freq = self.frequencies
        return sum([freq[c] for c in set(word) if c not in self.included and c not in self.excluded])

    def find_best_guess_by_frequency(self, hardmode: bool = False) -> str:
        pass

    def _get_index_frequency_score(self, word: str, freq: Optional[dict] = None) -> int:
        if freq is None:
            freq = self.index_frequencies
        return sum([freq[i][c] for i, c in enumerate(word)])
        


def test():
    w = WordleTrainer.new_random_wordle()
    #for k, v in w.index_frequencies.items():
    #    print(v)
    w.rich_print_prediction_str("CORES")
    #w.rich_print_guess_response("SOARE")
    #w.play()
    #w.assign_at_index(0, "G")
    #w.assign_at_index(1, "O")
    #w.assign_at_index(2, "N")
    #w.assign_at_index(3, "I")
    #w.assign_at_index(4, "E")
    #w.exclude("AS")
    #w.include("RO")
    #w.exclude_at_index(0, "")
    #w.exclude_at_index(1, "R")
    #w.exclude_at_index(2, "O")
    #w.exclude_at_index(3, "")
    #w.exclude_at_index(4, "")
    #w.rich_print_prediction_str("GOURD")
    #print(w.possible_words)
    #print(w.included)
    #print(w.possible_words)
    #print(w.frequencies)
    #for t in w.evaluate_guesses_by_frequency():
    #    print(t)
    #if len(w.possible_words) > 100:
    #    print(w.find_best_sieve())
    #elif len(w.possible_words) >10:
    #    print(w.find_best_guess())
    #else:
    #print(w.possible_words)
    #print(w.find_best_guess())

    #cr = ColorRange(min = 7, max = 23, min_color=OutputColor.YELLOW.value, max_color=OutputColor.GREEN.value)
    #cr.demo()

    #cb = ColorBox(upper_colors=(OutputColor.YELLOW.value, OutputColor.GREEN.value), lower_colors=(OutputColor.GRAY.value, OutputColor.GRAY.value))
    #cb.demo(8)


def run_as_cli():
    pass

if __name__ == "__main__":
    test()