import numpy as np
import pandas as pd
from tqdm import tqdm
from wordle import Wordle, WordGuesser, words_by_entropy
from chessle import ChessGuesser, openings_by_entropy

def load_wordle_data():
    # Load the wordlist from Wordle (allowed guesses taken out of the source code of the official game):
    with open("./wordle_data/wordlist.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        wordlist = line.replace(" ","").replace("'","").split(',')
    
    # Load table of frequency of 5 letter words (constructed from Google n-gram dataset)
    frequencies_df = pd.read_csv("./wordle_data/five_letter_frequencies.csv")
    frequencies = pd.Series(frequencies_df["count"].values, index=frequencies_df["word"]).to_dict()

    return wordlist, frequencies

def play_wordle(word, wordlist):
    print(f"The hidden word is {word}")
    wordle = Wordle(word)
    player = WordGuesser(wordle, wordlist, frequencies)
    player.play()

def load_chessle_data():
    # Load the opening corpus for Chessle (data taken from Lichess July 2014):
    openings = pd.read_csv("./chessle_data/opening_frequency.csv")
    frequencies = pd.Series(openings["frequency"].values, index=openings["opening"]).to_dict()
    return openings["opening"].values, frequencies


if __name__ == "__main__":
    # Load Wordle data
    #wordlist, frequencies = load_wordle_data()

    # Calculates the entropy of each word for the whole wordlist
    #print(words_by_entropy(wordlist, frequencies))

    # Play Wordle with a hidden random word    
    #word = np.random.choice(wordlist)
    #play_wordle(word, wordlist)
    
    # Load Chessle data
    allowed_openings, frequencies = load_chessle_data()

    # Calculate the entropy of each opening for the top 10000 most frequent openings
    print(openings_by_entropy(allowed_openings= allowed_openings[:10000], frequencies=frequencies))
    
    # Play Chessle (https://jackli.gg/chessle/) manually, input the result you get from the game for the guess
    guesser = ChessGuesser(allowed_openings, frequencies)
    guesser.play()