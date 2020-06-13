from stockfish import Stockfish
import string, time
import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522
import hardwarescripts

def setdifficulty():
    pass
    # gives option for button to be clicked


def updateboard():
    grid = getboard()
    last = getfen()

    for n in range(len(grid)):
        for m in range(len(grid[n])):
            if grid[n][m] == 1 and last[n][m] == " " or \
                    grid[n][m] == 0 and last[n][m] != " ":
                print(str(8 - n) + alphabet[m])

    # check if board does not make sense
        # send to hardware
    # check if a valid move
        # send to hardware

    # update board (FEN in stockfish)
    # update saved FENs
    # update saved PGN

    # check best move and send to hardware (skip if players turn)
    # check evaluation and send to hardware


def getboard(): # will be determined with hardware
    return [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]]


def getfen():
    fen = stockfish.get_fen_position()
    grid = [[]]
    i = 0
    n = 0
    while True:
        if fen[i] == r"/":
            n += 1
            grid.append([])
        elif fen[i] == " ":
            break
        elif fen[i].isnumeric():
            for m in range(int(fen[i])):
                grid[n].append(" ")
        else:
            grid[n].append(fen[i])
        i += 1
    return grid

alphabet = list(string.ascii_lowercase)
LEDbar = hardwarescripts.LEDBar()

stockfish = Stockfish("/home/pi/full-stack-chessboard/stockfish", depth=8)
stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

LEDbar.setvalue([1, 1, 1, 1, 0, 0, 1, 0, 1, 1])
time.sleep(1)
LEDbar.clear()
updateboard()

test = hardwarescripts.MFRC522()
test.test()