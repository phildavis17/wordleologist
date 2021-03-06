# Wordleologist

Wordleologist is an interactive command line tool designed as a companion to [Wordle](https://www.powerlanguage.co.uk/wordle/). It can offer gentle hints, or, if you prefer, blunt ones.

![A recorded demo of Wordleologist in use](https://github.com/phildavis17/wordleologist/blob/main/documentation/Demo.gif)

Running Wordleologist will start an interactive session.

![The Wordleologist Greeting](https://github.com/phildavis17/wordleologist/blob/main/documentation/images/Greeting.jpg)

From here, you can enter the information you've learned, and ask for help in a few ways.

## Entering Information
Let Wordleologist know how your game is going by telling it about the green, yellow, and gray letters you've seen. If the information you enter reduces the number of words that could be possible solutions to the puzzle, it will let you know how many possible words remain.

### Green or Yellow Letters
Green or Yellow letters are tied to a specific location in the target word. In order to tell Wordleologist which letters you know are yellow or green, enter the command followed by a 5 character sequence containing letters at their correct positions separated by a space filling character. "-" is used as a space filling character in these examples, but any non-letter character will be treated the same way. The sequence you enter must be exactly 5 characters long.

```
 > green -r---
```
This will eliminate all words that do not have 'r' as their second letter.

```
 > yellow a----
```
This will eliminate all words that do not contain the letter 'a' as well as words that have 'a' as their first letter. 

### Gray Letters
Since gray letters are (usually) not tied to a specific position in the word, you can enter as many of these as you want at once, in any order, and there's no need for space filling characters.

```
 > gray ose
```
This will eliminate all words that contain 'o', 's', or 'e'.

## Testing Guesses
Wordleologist allows you to test out the expected strength of a guess. By testing a number of guesses, Wordleologist can help guide you towards more useful guesses.

![An example of guess testing](https://github.com/phildavis17/wordleologist/blob/main/documentation/images/Test.jpg)

Wordleologist will then print out the guess, coloring each letter according its frequency in the pool of remaining possible words. If a letter does not occur often in possible words, it will be more gray. If it occurs in many possible words, but not at that position, it will be more yellow. If it occurs often at that position, it will be more green.

In the above example, the 'R' and 'A' are very common in these positions in the remaining possilbe words, while the other letters are less common.

## Getting Suggested Guesses
Entering `clues` will produce a list of three suggested high-value guesses, each printed with colors to show the expected outcome of each letter. These guesses come in three flavors:

**More Information** - This guess is generated by considering the pool of remaining possible words, and finding a word that has as many letters in comming with as many remaining words as possible. The hope here is to maximize information gain.

**More Green Letters** - This guess also looks at the poole of remaining possible words, but then finds a word that has the best odds of producing as many green letters as possible.

**Balanced** - This guess is generated by taking into account both potential green letters and total information gain.

If Wordleologist finds more than one word with the same expected value, it will pick one at random. You can ask for clues multiple times to see if there are alternate options.

![An example of suggested clues](https://github.com/phildavis17/wordleologist/blob/main/documentation/images/Clues.jpg)

In the above example, each of the letters in 'CLINT' is a fairly dim color, though some are showing signs of life. While these letters are not particularly likely to occur in the target word, Wordleologist has found that getting information about these letters will help include or exclude the most words from the remaining pool.

'TRANT' has a 'T' at the beginning and end, suggesting that many of the remaining words have a 'T' in one or both of those positions. This gives you a better chance of getting a green letter, but if they both end up being gray, you'll have missed out on gaining more information by including a different letter.

'TRAIN' has the same high-likelihood 'R' and 'A' from 'TRANT', but it also reintroduces the 'I' from 'CLINT', which is expected to yeild a lot of information about remaining words.

## Showing the Word List
Entering `words` will print a sorted list of possible words given the current information. Just as a heads up, Wordleologist uses the full list of valid 5 letter scrabble words, which appears to include much more obscure words than those that show up in Wordle, so a lot of these words might be weird. 

![An example word list](https://github.com/phildavis17/wordleologist/blob/main/documentation/images/Words.jpg)

A lot of these are uncommon, but one of them must be the target word.

## Activating Hardmode
Entering `hardmode` will toggle hardmode on or off. If hardmode is on, all guesses will be possible solutions to the puzzle. **Note:** Resetting sets hardmode to off.

## Resetting
If you'd like to start over, enter `reset`. This returns Wordleologist to its initial state.

## Exiting
When you're done, enter `exit`.

## A Note on the Word List
Wordleologist bases its estimates on the full list of accepted 5 letter Scrabble words, which includes a lot of uncommon words. While I have yet to encounter a Scrabble word that Wordle rejects as a guess, Wordle seems to be pulling its target words from a much smaller list of more common words. Comparing against the Wordle list would be more accurate, but I have not yet found a canonical list of Wordle words. Rather than making assumptions, I've stuck to the Scrabble list. It still works pretty well.