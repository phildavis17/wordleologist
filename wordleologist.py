import string
from collections import Counter
from pathlib import Path
from typing import Iterable, Optional
from rich.console import Console
from rich.theme import Theme

SCRABBLE_WORDS_PATH = Path(__file__).parent / "data" / "Collins Scrabble Words (2019).txt"

with open(SCRABBLE_WORDS_PATH) as scrabble_words:
    five_letter_words = {word.strip() for word in scrabble_words.readlines() if len(word.strip()) == 5}


class Wordle:
    def __init__(self, target_word: Optional[str] = None) -> None:
        self.target_word = target_word
        self.possible_letters = {x: set(string.ascii_uppercase) for x in range(5)}
        self.included: set = set()
        self.excluded: set = set()

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
        remaining_words = Wordle._filter_by_inlcuded(self.included, five_letter_words)
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

    def evaluate_guesses_by_frequency(self):
        """Returns a list of possible words sorted by their frequency scores."""
        return list(reversed(sorted([(self._get_frequency_score(word), word) for word in self.possible_words])))
    
    def find_best_sieve(self):
        """Returns the word with the highest frequency score, whether or not it could be the target word."""
        freq = self.frequencies
        best_sieve = (0, "")
        for word in five_letter_words:
            best_sieve = max(best_sieve, (self._get_frequency_score(word, freq=freq), word))
        return best_sieve
    
    def find_best_guess(self):
        freq = self.frequencies
        best_guess = (0, "")
        for word in self.possible_words:
            best_guess = max(best_guess, (self._get_frequency_score(word, freq), word))
        return best_guess
            

    def _get_frequency_score(self, word: str, freq: Optional[Counter] = None) -> int:
        """
        Returns the sum of frequency scores by character in a supplied word, excluding characters that must be included in the target word.
        A heuristic for the amount of information gained by guessing that word.
        """
        if freq is None:
            freq = self.frequencies
        return sum([freq[c] for c in set(word) if c not in self.included])


def test():
    w = Wordle()
    w.assign_at_index(1, "A")
    #w.assign_at_index(2, "N")
    w.exclude("SOREYI")
    w.include("ALNB")
    w.exclude_at_index(0, "LN")
    #w.exclude_at_index(1, "")
    w.exclude_at_index(2, "AB")
    w.exclude_at_index(3, "L")
    w.exclude_at_index(4, "NA")
    #print(w.included)
    print(w.possible_words)
    #print(w.frequencies)
    #for t in w.evaluate_guesses_by_frequency():
    #    print(t)
    print(w.find_best_guess())

if __name__ == "__main__":
    test()