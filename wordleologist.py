# Wordleologist, Wordle hints as gentle as you want them.
# Philip Davis
# 2022

import os
import random
import string
import sys
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

import rich

from wordleologist_help import WORDLEOLOGIST_HELP

SCRABBLE_WORDS_PATH = (
    Path(__file__).parent / "data" / "Collins Scrabble Words (2019).txt"
)

with open(SCRABBLE_WORDS_PATH) as scrabble_words:
    SCRABBLE_WORDS = {word.strip() for word in scrabble_words.readlines()}


class ColorRange:
    """Maps a range of colors to a color gradient. Intended to work with rich."""

    def __init__(
        self,
        min: int = 0,
        max: int = 100,
        min_color: Tuple[int, int, int] = None,
        max_color: Tuple[int, int, int] = None,
    ) -> None:
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
        return tuple(
            [
                int(min_val + (max_val - min_val) * pos)
                for min_val, max_val in zip(self.min_color, self.max_color)
            ]
        )

    @staticmethod
    def rich_format_rgb(rgb: tuple) -> str:
        """Returns a string that describes the supplied rgb tuple in a way rich can understand."""
        r, g, b = rgb
        return f"rgb({r},{g},{b})"

    def demo(self, count: int = 10) -> None:
        """Prints a grid of characters demonstrating the current state of the ColorRange object."""
        start = self.min
        stop = self.max
        print(repr(self))
        for n in range(count):
            pos = n / (count - 1)
            num = int(start + (stop - start) * (n / (count - 1)))
            rich.print(
                f"{'{:.2f}'.format(pos)} [{self.rich_format_rgb(self.color_from_number(num))}]???????????? Demo ????????????[/] {num}"
            )

    def __repr__(self) -> str:
        return f"ColorRange({self.min}, {self.max})"


class ColorBox:
    """
    A 2 dimensional color gradient controlled by the color at each of the 4 corners.
    Relies on ColorRange class, and is also intended to work with rich.
    """

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
        """Returns a color tuple (r, g, b) by interpolating the supplied x and y numbers within the assigned ranges."""
        upper = self.upper_range.color_from_number(x)
        lower = self.lower_range.color_from_number(x)
        vertical = ColorRange(self.y_min, self.y_max, lower, upper)
        return vertical.color_from_number(y)

    def color_from_positions(self, x: float, y: float) -> Tuple[int, int, int]:
        """Returns a color tuple (r, g, b) by interpolating the supplied position floats."""
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
        """Prints a bunch of characters demonstrating the state of the ColorBox."""
        for y in range(count):
            y_pos = y / (count - 1)
            row = []
            for x in range(count):
                x_pos = x / (count - 1)
                row.extend(
                    [
                        f"[{self.rich_format_rgb(self.color_from_positions(x_pos, y_pos))}]",
                        "???",
                        "[/]",
                    ]
                )
            rich.print("".join(row))

    def __repr__(self) -> str:
        # Not sure how to represent these in text form.
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


class WordleTrainer:
    FIVE_LETTER_WORDS = {word for word in SCRABBLE_WORDS if len(word) == 5}
    STANDARD_MESSAGES = {
        "turn": "\nPlease enter your guess: ",
        "bad turn": "\nPlease enter a valid 5 letter word: ",
        "win": "\nCongratulations!",
        "lose": "\nBetter luck next time!",
    }
    
    def __init__(self, target_word: Optional[str] = None) -> None:
        # The actual setup stuff has been moved to self.reset to reduce code duplication.
        self.reset()

    def reset(self, target_word: Optional[str] = None) -> None:
        """
        Sets all the attributes of a Wordleologist object to their initial state.
        This method is called by __init__ to set up fresh objects.
        """
        self.target_word = target_word
        self.possible_letters = {x: set(string.ascii_uppercase) for x in range(5)}
        self.known_alphabet = {
            c: OutputStyle.WHITE.value for c in string.ascii_uppercase
        }
        self.included: set = set()
        self.excluded: set = set()
        self.guessed_words: list = []
        self.hardmode = False

    @classmethod
    def new_random_wordle(cls) -> "WordleTrainer":
        """Creates a new Wordle object with a randomly selected target word."""
        return WordleTrainer(random.choice(tuple(cls.FIVE_LETTER_WORDS)))

    def _build_guess_evaluation(self, guess: str) -> tuple:
        """Creates a tuple of rich styles to match the evaluation of each character in the supplied guess."""
        return tuple([self._evaluate_guess_char(i, c) for i, c in enumerate(guess)])

    def _build_rich_response_string(self, guess: str) -> str:
        """Creates a string with rich style markup tags for the supplied guess."""
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
        if not self.target_word:
            raise RuntimeError("You can't play if there's no target word!")
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
        """Enters the play game loop."""
        print("Welcome to wordleologist!\n")
        while (
            self.target_word not in self.guessed_words and len(self.guessed_words) < 6
        ):
            self.guessed_words.append(self._get_valid_turn())
            self.clear_console()
            for word in self.guessed_words:
                self.rich_print_guess_response(word)
            self.rich_print_alphabet()
        if self.target_word in self.guessed_words:
            print("Congratulations!")
        else:
            rich.print(
                f"\nWe were looking for [{OutputStyle.GREEN.value}]{self.target_word}[/]"
            )
            print("Better luck next time!")

    def _build_alphabet_string(self) -> str:
        """
        Returns a rich formatted string of the alphabet where the style of each letter reflects
        the best information available for that letter in the current game state.
        """
        styled_alpha = ["\n"]
        for char, style in self.known_alphabet.items():
            styled_alpha.extend([f"[{style}]", char, "[/] "])
        return "".join(styled_alpha)

    def rich_print_alphabet(self) -> None:
        rich.print(self._build_alphabet_string())

    @staticmethod
    def clear_console():
        """Clears the console. Design to handle both Windows and UNIX-like systems."""
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

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
        remaining_words = WordleTrainer._filter_by_inlcuded(
            self.included, self.FIVE_LETTER_WORDS
        )
        for index, letters in self.possible_letters.items():
            remaining_words = WordleTrainer._filter_by_letter(
                index, letters, remaining_words
            )
        if not remaining_words:
            raise ValueError("No words are possible. Something went wrong!")
        return remaining_words

    @property
    def index_frequencies(self) -> dict:
        """
        Returns a dictionary in the form {index: Counter} where the Counter contains counts of each letter that occurs at that index
        in the pool of remaining possible words.
        """
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
        if len(self.possible_letters[index]) > 1:
            self.possible_letters[index] = self.possible_letters[index].difference(
                set(bad_chars)
            )

    def include(self, good_chars: str):
        """Adds supplied characters to the set of letters that must appear in the target word."""
        self.included.update(set(good_chars))

    def assign_at_index(self, index: int, char: str):
        """
        Reduces the set of possible letters at the supplied index to a single supplied letter.
        Do this with green letters.
        """
        if len(char) != 1:
            raise ValueError(
                f"Tried to assign a string with improper number of characters: '{char}'"
            )
        self.possible_letters[index] = set(char)
        self.included.add(char)

    def _build_prediction_str(self, guess: str) -> str:
        """
        Uses a ColorBox to generate a color for each letter in the supplied guess by interpolating along two axes:
         - Index Frequency: The frequency with which this letter occurs at this index in remaining words vs at some other index (green vs yellow)
         - Presence Frequency: The frequency with which this letter occurs in remaining words vs does not occur (colorful vs gray)
        Returns a rich formatted string. 
        """
        cb = ColorBox(
            upper_colors=(OutputColor.YELLOW.value, OutputColor.GREEN.value),
            lower_colors=(OutputColor.GRAY.value, OutputColor.GRAY.value),
        )
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
            prediction.extend(
                [
                    f"[bold {cb.rich_format_rgb(cb.color_from_positions(idx_freq, presence_freq))}]",
                    c,
                    "[/]",
                ]
            )
        return "".join(prediction)

    def rich_print_prediction_str(self, guess: str) -> None:
        rich.print(self._build_prediction_str(guess))

    def find_best_guess_by_frequency(self):
        """Returns the word with the highest frequency score that could also be the target word."""
        freq = self.frequencies
        best_score = 0
        best_guesses = []
        if self.hardmode:
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
        return sum(
            [
                freq[c]
                for c in set(word)
                if c not in self.included and c not in self.excluded
            ]
        )

    def find_best_guess_by_index(self) -> str:
        """
        Returns a word that is expected to produce the most green letters.
        In the event of a tie, a word is chosen at random.
        """
        freq = self.index_frequencies
        best_score = 0
        best_guess = []
        if self.hardmode:
            words = self.possible_words
        else:
            words = self.FIVE_LETTER_WORDS
        for word in words:
            score = self._get_index_frequency_score(word, freq)
            if score > best_score:
                best_score = score
                best_guess = [word]
            elif score == best_score:
                best_guess.append(word)
        return random.choice(best_guess)

    def _get_index_frequency_score(self, word: str, freq: Optional[dict] = None) -> int:
        if freq is None:
            freq = self.index_frequencies
        return sum([freq[i][c] for i, c in enumerate(word)])

    def find_best_guess_combined(self) -> str:
        """
        Checks all available words for the frequency with which their letters are present in the remaining word pool,
        and also their likelihood to yeild green letters, returning a word with the maximum score.
        In the event of a tie, a word is chosen at random.
        """
        freq = self.frequencies
        i_freq = self.index_frequencies
        best_score = 0
        best_guess = []
        if self.hardmode:
            words = self.possible_words
        else:
            words = self.FIVE_LETTER_WORDS
        for word in words:
            score = self._get_frequency_score(
                word, freq
            ) + self._get_index_frequency_score(word, i_freq)
            if score > best_score:
                best_score = score
                best_guess = [word]
            elif score == best_score:
                best_guess.append(word)
        return random.choice(best_guess)

    def green(self, characters: str) -> None:
        """Handles green letters."""
        char_dict = self._process_char_assignment_str(characters)
        for i, c in char_dict.items():
            self.assign_at_index(i, c)

    def yellow(self, characters: str) -> None:
        """Handles yellow letters."""
        char_dict = self._process_char_assignment_str(characters)
        for i, c in char_dict.items():
            self.include(c)
            self.exclude_at_index(i, c)

    def gray(self, characters: str) -> None:
        """Handles gray letters."""
        self.exclude(characters.upper())
        pass

    def _process_char_assignment_str(self, input_str: str) -> dict:
        """
        Creates and returns a dictionary in the form {index: letter} for the letters in a supplied string.
        Ignores non-letter characters.
        """
        return {
            i: c.upper() for i, c in enumerate(input_str) if c in string.ascii_letters
        }

    def get_clues(self) -> None:
        """Prints the three different types of clue."""
        info = self.find_best_guess_by_frequency()
        green = self.find_best_guess_by_index()
        balance = self.find_best_guess_combined()
        print("More Information: ", end="")
        self.rich_print_prediction_str(info)
        print("More Green Letters: ", end="")
        self.rich_print_prediction_str(green)
        print("Balanced: ", end="")
        self.rich_print_prediction_str(balance)

    def get_words(self) -> None:
        """Returns a sorted list of words that are currently possible."""
        print(sorted(list(self.possible_words)))

    def test(self, guess: str) -> None:
        # How and where do I validate this?
        self.rich_print_prediction_str(guess)

    def help(self, cmd: str) -> None:
        """Prints help text for the supplied command."""
        print(WORDLEOLOGIST_HELP[cmd.lower()])

    def exit(self) -> None:
        """
        Exits the program. This is not currently used.
        Instead, the text 'exit' ends the while loop that drives the interface.
        """
        sys.exit()

    def toggle_hardmode(self) -> None:
        """Toggles hardmode on or off."""
        self.hardmode = not self.hardmode
        if self.hardmode:
            print("hardmode is on.")
        else:
            print("hardmode is off.")

    def _handle_command(self, cmd: tuple) -> None:
        """Calls the method associated with supplied input commands."""
        # Commands that do not require any additional information are in this dict.
        no_arg = {
            # "play": self.play, # Play is not implimented yet.
            "exit": self.exit,
            "clues": self.get_clues,
            "words": self.get_words,
            "reset": self.reset,
            "hardmode": self.toggle_hardmode,
        }
        # Commands that require additional information are in this dict.
        with_arg = {
            "help": self.help,
            "test": self.test,
            "green": self.green,
            "yellow": self.yellow,
            "gray": self.gray,
        }

        command, argument = cmd
        if command in no_arg:
            no_arg[command]()
        elif command in with_arg:
            with_arg[command](argument)
        else:
            raise RuntimeError(
                f"A strange command has made it past the gates: {command}??????"
            )

    @staticmethod
    def _tokenize_input(input_str: str) -> tuple:
        """Breaks an input string into two pieces, before and after the first space (' ') encountered."""
        parts = input_str.partition(" ")
        return (parts[0].lower(), parts[-1].upper())

    @staticmethod
    def _validate_index_token(tokens: tuple) -> bool:
        """
        Returns true if the token sent along with a command is a well formed token for an index sensitive command.
        Does nothing to validate the command itself, assuming that such a check happens before this is invoked.
        """
        _, token = tokens
        return len(token) == 5

    @staticmethod
    def _validate_any_token(tokens: tuple) -> bool:
        """
        Returns true if the token sent along with a command is a well formed token for a non-index-sensitive command.
        Does nothing to validate the command itself, assuming that such a check happens before this is invoked.
        """
        _, token = tokens
        return bool(token)

    @staticmethod
    def _validate_no_token(tokens: tuple) -> bool:
        # I don't think this actually needs to do anything?
        # Bad commands are caught before this is invoked, and if there's no token there's nothing else to validate.
        # I've left it in here, though, to keep the process symetrical for all command types.
        return True

    @classmethod
    def _validate_help(cls, tokens: tuple) -> bool:
        """Returns True if the supplied token is a key in the dict of help commands."""
        _, token = tokens
        return token.lower() in WORDLEOLOGIST_HELP

    @classmethod
    def _validate_command_input(cls, input_tuple: tuple) -> bool:
        """Dispatches input to the appropriate validator."""
        validators = {
            # "play": cls._validate_no_token, # play is not implimented yet.
            "help": cls._validate_help,
            "exit": cls._validate_no_token,
            "test": cls._validate_index_token,
            "green": cls._validate_index_token,
            "yellow": cls._validate_index_token,
            "gray": cls._validate_any_token,
            "clues": cls._validate_no_token,
            "words": cls._validate_no_token,
            "reset": cls._validate_no_token,
            "hardmode": cls._validate_no_token,
        }

        command, token = input_tuple
        if command not in validators:
            rich.print(f"[bold red]{command} is not a known command.[/]")
            return False
        elif not validators[command]((command, token)):
            rich.print("[bold red]Something was wasn't quite right with that input. Try again.[/]")
            return False
        return True

    @classmethod
    def _get_valid_command_input(cls) -> tuple:
        """Prompts the user for input until a valid command is entered."""
        valid = False
        while not valid:
            usr_input = cls._tokenize_input(input("\n > "))
            valid = cls._validate_command_input(usr_input)
        return usr_input

    def input_loop(self) -> None:
        rich.print(
            f"\n[{OutputStyle.GREEN.value}]Wordle[/][{OutputStyle.YELLOW.value}]ologist[/] at your service.\n"
        )
        print("Enter 'help' for instructions")
        print("Enter 'exit' to quit.")
        command, token = None, None
        word_cr = ColorRange(
            min_color=OutputColor.GREEN.value, max_color=(193, 193, 193)
        )
        while command != "exit":
            old_words = len(self.possible_words)
            command, token = self._get_valid_command_input()
            self._handle_command((command, token))
            new_words = len(self.possible_words)
            if new_words < old_words:
                rich.print(
                    f"\n[{word_cr.rich_format_rgb(word_cr.color_from_position(min(new_words/50, 1.0)))}]{new_words}[/] possible words remain.",
                    end="",
                )


def test():
    w = WordleTrainer.new_random_wordle()
    # print(w._validate_command_input("exit a--s-"))
    print(w._get_valid_command_input())


def run_text_interface():
    w = WordleTrainer()
    w.input_loop()


if __name__ == "__main__":
    run_text_interface()
