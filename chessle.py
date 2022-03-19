import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from wordle import Wordle, color_guess, entropy_guesses

class Chessle(Wordle):
    def __init__(self, opening, n_rows=6, n_moves=10):
        self.opening = opening
        self.n_rows = n_rows
        self.n_moves = n_moves
        self.guesses = [] # Formatted as ["move1","move2",...,"move10"]
        self.colors = []  # Formatted as ["?","?",...,"?"] where ? = G (green), Y (yellow), N (not in word)
        self.curr_row = 0
        self.win_state = False
        self.blocks = {"G":"🟩", "Y":"🟨", "N":"⬛"}

    def __repr__(self):
        s = "-------\n"
        s += "Guesses:\n"
        s += "-------\n"
        for guess in self.guesses:
            s += ' '.join(guess)
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
        if len(guess) == self.n_moves and self.curr_row < self.n_rows:
            self.curr_row += 1
            self.guesses.append([guess[_] for _ in range(len(guess))])
            self.colors.append(color_guess(guess, self.opening))
            if guess == self.opening:
                self.win_state = True

class ChessGuesser:
    def __init__(self, openings, frequencies, n_guesses=6):
        self.allowed_openings = openings
        self.frequencies = frequencies
        self.n_guesses = n_guesses
        self.guesses = []
        self.colors = []
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

    def prune_moves(self, guesses, colors, mode="chessle"):
        # Returns all the allowed openings for which the guesses give a specific set of colors
        new_allowed_openings = []
        for candidate in self.allowed_openings:
            if all(color_guess(guesses[_], candidate,mode) == colors[_] for _ in range(len(guesses))):
                new_allowed_openings.append(candidate)
        return new_allowed_openings

    def guess(self):
        self.allowed_openings = self.prune_moves(self.guesses, self.colors)
        total = sum(self.frequencies[w] for w in self.allowed_openings)
        probabilities = [self.frequencies[w]/total for w in self.allowed_openings]
        if len(self.allowed_openings) > 0:
            self.guesses.append(np.random.choice(self.allowed_openings, p=probabilities))
            print(f"Based on the current information, the guess is \n{self.guesses[-1]}")
            return self.guesses[-1]

    def play(self):
        turn = 0
        while turn < self.n_guesses:
            if turn > 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(self.__repr__())
            self.guess()
            color = input("Enter the result:")
            self.colors.append(color)
            
            turn += 1
            # End the game if the guess was correct
            if color == "GGGGGGGGGG":
                os.system('cls' if os.name == 'nt' else 'clear')
                print(self.__repr__())
                print("You won!")
                break
        # If you didn't guess after the allowed number of guesses, you lose
        if self.colors[-1]!="GGGGGGGGGG":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self.__repr__())
            print("You lose!")


def openings_by_entropy(allowed_openings, frequencies):
    '''
    Returns a dataframe consisting of the set of allowed openings ordered by their entropy value.
    '''
    total = sum(frequencies[w] for w in allowed_openings)
    probabilities = [frequencies[w]/total for w in allowed_openings]
    entropy = entropy_guesses(allowed_openings, frequencies, "chessle")
    df = pd.DataFrame(columns=["opening", "entropy"])
    df["opening"] = allowed_openings
    df["entropy"] = [entropy[w] for w in allowed_openings]
    df = df.sort_values(by="entropy", ascending=False)
    return df


# Highest entropy guess
# e4 e5 Nf3 Nc6 Bc4 Be7 Nc3 Nf6 d4 d6

