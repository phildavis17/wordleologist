# Wordleologist
# Philip Davis
# 2022

# I've broken this out into its own file in hopes of making the main file more readable. Did it work? Who can say.

_empty = """
To enter green letters
 > green ...

To enter yellow letters
 > yellow ...

To enter gray letters
 > gray ...

To test a guess
 > test ...

To get suggested guesses
 > clues

To see all possible words
 > words

To toggle hardmode
 > hardmode

To reset
 > reset

To quit
 > exit

For more information about one of these commands
 > help <command>
"""

_green = """
Green letters must be entered as part of a 5 character sequence. Use any non-letter character to fill empty spaces.

> green -r---
This will exclude all words that do not have 'r' as their second letter.
"""

_yellow = """
Yellow letters must be entered as part of a 5 character sequence. Use any non-letter character to fill empty spaces.

> yellow a----
This will exclude all words that do not contain the letter 'a', as well as those that have an 'a' as their first letter.
"""

_gray = """
Gray letters can be enterd in any order, as many as you like at a time.

> gray abc
This will exclude all words that contain 'a', 'b', or 'c'.
"""

_test = """
Wordleologist will print your guess, coloring each letter depending on its frequency in the remaining possible words.
More gray letters are less likely to be present.
More yellow letters are likely to be present, but not at that position.
More green letters are likely to be present at that position.
"""

_clues = """
Shows three suggested guesses. 
'More Information' - This guess aims to learn the most about the letters in the remaining possible words.
'More Green Letters' - This guess is intended to get as many green letters as possible.
'Balanced' - This guess takes into account both green letters and information gain.
"""

_words = """
Shows a list of all remaining possible words.
"""

_hardmode = """
Toggles hardmode on and off. While in hardmode, all suggested guesses will be possible solutions to the puzzle. By default, hardmode is off.
"""

_reset = """
Resets Wordleologist to its initial state.
"""

_exit = """
Exits Wordleologist.
"""

_help = """
Shows instructions about how to use Wordleologist.
For more information, check out the github repo at https://github.com/phildavis17/wordleologist
"""


WORDLEOLOGIST_HELP = {
    "": _empty,
    "green": _green,
    "yellow": _yellow,
    "gray": _gray,
    "test": _test,
    "clues": _clues,
    "words": _words,
    "hardmode": _hardmode,
    "reset": _reset,
    "exit": _exit,
    "help": _help,
}