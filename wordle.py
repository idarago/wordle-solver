import numpy as np
import pandas as pd
from tqdm import tqdm

def color_guess(guess, word, mode="wordle"):
    '''
    Creates the color map for a guess of a hidden word.
    '''
    if mode=="chessle":
        guess = guess.strip().split(" ")
        word = word.strip().split(" ")
    # Create a frequency map of the characters in the selected word
    char_freq = {}
    n_letters = len(word)
    colors = ["?" for _ in range(n_letters)]
    for c in range(n_letters):
        # If there's a match we don't count it towards the frequency
        if guess[c] == word[c]:
            colors[c] = "G"
            if word[c] not in char_freq:
                char_freq[word[c]] = 0
        else:
            if word[c] not in char_freq:
                char_freq[word[c]] = 1
            else:
                char_freq[word[c]] += 1
    
    for c in range(n_letters):
        if guess[c] in word:
            if colors[c] != "G":
                # If it's in the word and not in the right place, color it yellow
                if char_freq[guess[c]]>0:
                    colors[c] = "Y"
                    char_freq[guess[c]] -= 1
                # If it has appeared enough times, then it's not in the word anymore
                else:
                    colors[c] = "N"
        else:
            colors[c] = "N"
    if mode=="chessle":
        return "".join(colors)
    else:
        return colors


def entropy_guesses(allowed_words, frequencies, mode="wordle"):
    '''
    Calculates the entropy of the distribution of colors obtained after guessing for a given hidden word. 
    '''
    total = sum(frequencies[w] for w in allowed_words)
    if total > 0.0:
        probabilities = {w : frequencies[w]/total for w in allowed_words}
    else:
        probabilities = {w : 0.0 for w in allowed_words}
    coloring_frequencies = {w : {} for w in allowed_words}
    entropy = {w : 0.0 for w in allowed_words}
    for w in tqdm(allowed_words):
        for x in allowed_words:
            coloring = "".join(color_guess(x,w,mode))
            if coloring in coloring_frequencies[w]:
                coloring_frequencies[w][coloring] += probabilities[x]
            else:
                coloring_frequencies[w][coloring] = probabilities[x]
        total = sum(coloring_frequencies[w][coloring] for coloring in coloring_frequencies[w])
        if total > 0.0:
            for coloring in coloring_frequencies[w]:
                if coloring_frequencies[w][coloring] > 0.0:
                    entropy[w] -= coloring_frequencies[w][coloring] * np.log(coloring_frequencies[w][coloring]/total) / total
    return entropy


def words_by_entropy(allowed_words, frequencies,mode="wordle"):
    '''
    Returns a dataframe consisting of the words in a set allowed_words ordered by their entropy value.
    '''
    total = sum(frequencies[w] for w in allowed_words)
    probabilities = [frequencies[w]/total for w in allowed_words]
    entropy = entropy_guesses(allowed_words, frequencies,mode)
    df = pd.DataFrame(columns=["word", "entropy"])
    df["word"] = allowed_words
    df["entropy"] = [entropy[w] for w in allowed_words]
    df = df.sort_values(by="entropy", ascending=False)
    return df

class Wordle:
    '''
    Implements the basic game structure of Wordle
    '''
    def __init__(self, word, n_rows = 6, n_letters = 5):
        self.word = word
        self.n_rows = n_rows
        self.n_letters = n_letters
        self.guesses = [] # Formatted as ["A","B","C","D","E"]
        self.colors = []  # Formatted as ["?","?","?","?","?"] where ? = G (green), Y (yellow), N (not in word)
        self.curr_row = 0
        self.win_state = False
        self.blocks = {"G":"🟩", "Y":"🟨", "N":"⬛"}

    def __repr__(self):
        s = "-------\n"
        s += "Guesses:\n"
        s += "-------\n"
        for guess in self.guesses:
            s += ''.join(guess)
            s += "\n"
        s += "-------\n"
        s += "Colors:\n"
        s += "-------\n"
        for color in self.colors:
            for block in color:
                s+=self.blocks[block]
            s+="\n"
    
        return s

    def guess_word(self, guess):
        if len(guess) == self.n_letters and self.curr_row < self.n_rows:
            self.curr_row += 1
            self.guesses.append([guess[_] for _ in range(len(guess))])
            self.colors.append(color_guess(guess, self.word))
            if guess == self.word:
                self.win_state = True

class WordGuesser:
    '''
    Solver for the Wordle game.
    '''
    def __init__(self, wordle, wordlist, frequencies):
        self.wordle = wordle
        self.allowed_words = wordlist
        self.frequencies = frequencies
    
    def play(self,verbose=True):
        for _ in range(self.wordle.n_rows):
            guess = self.guess()
            self.wordle.guess_word(guess)
            if guess == self.wordle.word:
                self.wordle.win_state = True
                if verbose:
                    print(self.wordle)
                    print("You guessed the correct word!")
                break
        if verbose and self.wordle.win_state == False:
            print(self.wordle)
            print("You lose!")

    def guess(self, val = 4):
        # Updates the list of allowed words
        self.allowed_words = self.prune_words(self.wordle.guesses, self.wordle.colors)
        if val == 2:
            return self.strategy_2()
        elif val == 3:
            return self.strategy_3()
        elif val == 4:
            return self.strategy_4()
        else:
            return self.strategy_1()
        

    def strategy_1(self):
        # Completely random choice for the word as long as it's allowed, weighted by the frequency of the words
        total = sum(self.frequencies[w] for w in self.allowed_words)
        probabilities = [self.frequencies[w]/total for w in self.allowed_words]
        return np.random.choice(self.allowed_words, p=probabilities)

    def strategy_2(self):
        # Returns the word that maximizes entropy for the current list of allowed words
        entropy = entropy_guesses(self.allowed_words, self.frequencies)
        max_val = list(entropy.values())
        max_key = list(entropy.keys())
        return max_key[max_val.index(max(max_val))]

    def strategy_3(self):
        # Choose the word that maximizes entropy for the first round: "tares", then chooses at random
        if self.wordle.curr_row==0:
            return "tares"
        else:
            return self.strategy_1()

    def strategy_4(self):
        # Same as strategy_2, but precomputes the first step
        if self.wordle.curr_row==0:
            return "tares"
        else:
            return self.strategy_2()


    def prune_words(self, guesses, colors, mode="wordle"):
        # Returns all the allowed words for which the guesses give a specific set of colors
        new_allowed_words = []
        for candidate in self.allowed_words:
            if all(color_guess(guesses[_], candidate,mode) == colors[_] for _ in range(len(guesses))):
                new_allowed_words.append(candidate)
        return new_allowed_words
