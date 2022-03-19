import chess
import chess.pgn
import chess.svg
import io
import os
import time
import pandas as pd
from tqdm import tqdm

def get_five_moves(game):
    board = game.board()
    opening = []
    for i,move in enumerate(game.mainline_moves()):
        opening.append(board.san(move))
        board.push(move)
        if i>8:
            break
    return " ".join(opening)

five_moves = []
filename = "lichess_db_standard_rated_2014-07.pgn"
with open(filename) as f:
    frequency = {}
    opening_name = {}
    while True:
        game = chess.pgn.read_game(f)
        if game is None:
            break # end of file
        opening = get_five_moves(game)
        if len(opening.split(" "))==10:
            if opening in frequency:
                frequency[opening] += 1
            else:
                frequency[opening] = 1
            if "Opening" in game.headers:
                opening_name[opening] = game.headers["Opening"]
            else:
                opening_name[opening] = "Unknown"
            #print(opening_name[opening])

df = pd.DataFrame(columns=["opening", "frequency", "name"])
df["opening"] = frequency.keys()
df["frequency"] = [frequency[w] for w in frequency]
df["name"] = [opening_name[w] for w in frequency]
#df["moves"] = df["opening"].apply(lambda x : len(x.split(" ")) if type(x)==str else 0)
#df = df[df["moves"]==10]
df = df.sort_values(by="frequency", ascending=False)
df.to_csv("opening_frequency_new.csv", index=False)

#print(get_five_moves(game))
#for move in game.mainline_moves():
#    print(board.sen(move))

