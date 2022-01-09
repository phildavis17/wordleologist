import os
import string
import random
import rich
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional, Tuple
#from rich.console import Console
#from rich.theme import Theme

SCRABBLE_WORDS_PATH = Path(__file__).parent / "data" / "Collins Scrabble Words (2019).txt"

with open(SCRABBLE_WORDS_PATH) as scrabble_words:
    SCRABBLE_WORDS = {word.strip() for word in scrabble_words.readlines()}


class ColorRange:
    """A one dimensional """
    def __init__(self, min: int = 0, max: int = 100, min_color: Tuple[int] = None, max_color: Tuple[int] = None) -> None:
        self.min: int = min
        self.max: int = max
        self.min_color: tuple = min_color
        self.max_color: tuple = max_color
        if self.min_color is None:
            self.min_color = (0, 0, 0)
        if self.max_color is None:
            self.max_color = (255, 255, 255)
    
    def color_from_number(self, n: int) -> tuple:
        if not self.min <= n <= self.max:
            raise ValueError(f"{n} exceeds range bounds ({self.min}, {self.max})")
        span = self.max - self.min
        pos = n / span
        return self.color_at_position(pos)
        
    def color_at_position(self, pos: float) -> tuple:
        return tuple([int((min_val + max_val) * pos) for min_val, max_val in zip(self.min_color, self.max_color)])
    
    @staticmethod
    def rich_format_rgb(rgb: tuple) -> str:
        r, g, b = rgb
        return f"rgb({r},{g},{b})"

    def __repr__(self) -> str:
        return f"ColorRange({self.min}, {self.max})"

class ColorBox:
    def __init__(self) -> None:
        self



class OutputColor(Enum):
    """
    This Enum describes the colors used in the OutputStyle Enum.
    These are stored apart from the style as a whole to allow for simpler numerical operations on color.
    """
    GREEN = (0, 208, 0)
    YELLOW = (208, 208, 0)
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

class Wordle:
    FIVE_LETTER_WORDS = {word for word in SCRABBLE_WORDS if len(word) == 5}
    STANDARD_MESSAGES = {
        "turn": "\nPlease enter your guess: ",
        "bad turn": "\nPlease enter a valid 5 letter word:",
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
    def new_random_wordle(cls) -> "Wordle":
        """Creates a new Wordle object with a randomly selected target word."""
        return Wordle(random.choice(tuple(cls.FIVE_LETTER_WORDS)))
    
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
        print(message)
        guess = input()
        return guess

    def play(self) -> None:
        print("Welcome to wordle!\n")
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

    def _evaluate_alphabet_character(self, char: str) -> str:
        pass

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
        
    
# PLAY LOOP
# - Request Turn
# - Validate Turn
# - evaluate turn
# - Update internal state
# - print response
# - Repeat as needed


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
        remaining_words = Wordle._filter_by_inlcuded(self.included, self.FIVE_LETTER_WORDS)
        for index, letters in self.possible_letters.items():
            remaining_words = Wordle._filter_by_letter(index, letters, remaining_words)
        return remaining_words

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
        return sum([freq[c] for c in set(word) if c not in self.included])


def test():
    #w = Wordle.new_random_wordle()
    #w.rich_print_guess_response("SOARE")
    #w = Wordle.new_random_wordle()
    #w.exclude("ABCD")
    #w.rich_print_alphabet()
    #w.play()
    #w.assign_at_index(0, "A")
    #w.assign_at_index(1, "L")
    #w.assign_at_index(2, "N")
    #w.assign_at_index(3, "I")
    #w.assign_at_index(4, "Y")
    #w.exclude("AROEINTY")
    #w.include("LS")
    #w.exclude_at_index(0, "L")
    #w.exclude_at_index(1, "")
    #w.exclude_at_index(2, "")
    #w.exclude_at_index(3, "S")
    #w.exclude_at_index(4, "")
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
    #    print(w.possible_words)
    #print(w.find_best_guess())

    cr = ColorRange(min = 0, max = 10, min_color=(255,0,0), max_color=(0,255,0))
    
    for n in range(11):
        rich.print(f"[{cr.rich_format_rgb(cr.color_from_number(n))}] TESTING [/]")
def run_as_cli():
    pass

if __name__ == "__main__":
    test()