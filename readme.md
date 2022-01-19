# Wordleologist


## Entering Information

### Green or Yellow Letters
Green or Yellow letters are tied to a specific location in the target word. In order to tell Wordleologist which letters you know are yellow or green, enter the command followed by a 5 character sequence containing letters at their correct positions separated by a space filling character. "-" is used as a space filling character in these examples, but any non-letter character will be treated the same way. The sequence you enter must be exactly 5 characters long.

```
 > green -a---
```
This will eliminate all words that do not have 'a' as their second letter.

```
 > yellow --r--
```
This will eliminate all words that do not contain the letter 'r' as well as words that have 'r' as their third letter. 

### Gray Letters
Since gray letters are (usually) not tied to a specific position in the word, you can enter as many of these as you want at once, and there's no need for space filling characters.

```
 > gray acbdefgh
```

## Testing Guesses
Wordleologist allows you to test out the expected strength of a guess.
```
 > test above
```
Wordleologist will then print out the guess, coloring each letter according its frequency in the pool of remaining possible words. If a letter does not occur often in possible words, it will be more gray. If it occurs in many possible words, but not at that position, it will be more yellow. If it occurs often at that position, it will be more green. 

## Getting Suggested Guesses
Entering `clues` will produce a list of three suggested high-value guesses. These guesses come in three flavors.

### More Information
This guess is generated by considering the pool of remaining possible words, and finding a word that has as many letters in comming with as many remaining words as possible. The hope here is to maximize information gain.

### More Green Letters
This guess also looks at the poole of remaining possible words, but then finds a word that has the best odds of producing as many green letters as possible.

### Balanced
This guess is generated by taking into account both potential green letters and total information gain.

## Showing the Word List
Entering `words` will print a sorted list of possible words given the current information. Just as a heads up, Wordleologist uses the full list of valid 5 letter scrabble words, which appears to include much more obscure words than those that show up in Wordle, so a lot of these words might be weird. 

## Activating Hardmode
Entering `hardmode` will toggle hardmode on or off. If hardmode is on, all guesses must be possible solutions to the puzzle. **Note:** Resetting sets hardmode to off.

## Resetting
If you'd like to start over, enter `reset`. This returns Wordleologist to its initial state.
