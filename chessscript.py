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

    ### At this point it is alegraic notation

    example = ["e2", "e4"]

    # algebraic to FIDE
    # update saved PGN

    fen = updatefen(example)
    stockfish.set_fen_position(fen)

    # check best move and send to hardware (skip if players turn)
    # check evaluation and send to hardware


def getboard(): # will be determined with hardware
    return [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]]

def updatefen(algebraic):
    fen = stockfish.get_fen_position()
    fen = fen.split(" ")

    grid = togrid(fen[0])
    last = grid[-int(algebraic[0][1])][alphabet.index(algebraic[0][0])]
    next = grid[-int(algebraic[1][1])][alphabet.index(algebraic[1][0])]


    if last == "P" or last == "p" or next != " ": #5 half moves since last capture or pawn movement
        fen[4] = "0"
    else:
        fen[4] = str(int(fen[4]) + 1)

    # 4 en passent
    if (last == "P" or last == "p") and abs(int(algebraic[0][1])-int(algebraic[1][1])) == 2:
        fen[3] = algebraic[0][0] + str(int((int(algebraic[0][1])+int(algebraic[1][1]))/2))
    else:
        fen[3] = "-"

    fen[0] = "" #1 moves
    grid[-int(algebraic[1][1])][alphabet.index(algebraic[1][0])] = last
    grid[-int(algebraic[0][1])][alphabet.index(algebraic[0][0])] = " "
    for n in grid:
        for m in n:
            if m == " ":
                if fen[0][-1].isnumeric():
                    fen[0] = fen[0][:-1] + str(int(fen[0][-1]) + 1)
                else:
                    fen[0] += "1"
            else:
                fen[0] += m
        fen[0] += r"/"
    fen[0] = fen[0][:-1]

    if fen[1] == "w": #2 black or white
        fen[1] = "b"
    else:
        fen[1] = "w"

    if fen[1] == "w": #6 incremented after blacks move, b was already changed to w above
        fen[5] = str(int(fen[5]) + 1)

    fen[2] = "KQkq" #3 castling "KQkq"

    fen = " ".join(fen)
    return fen


def tofen(fen):
    grid = togrid(fen)
    fen = ""

    for n in grid:
        for m in n:
            if m == " ":
                if fen[-1].isnumeric():
                    fen = fen[:-1] + str(int(fen[-1]) + 1)
                else:
                    fen += "1"
            else:
                fen += m
        fen += r"/"
    fen = fen[:-1]

    return fen

def togrid(fen): #FEN without information at the end, eg "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    grid = [[]]
    i = 0
    n = 0
    for m in fen:
        if m == r"/":
            n += 1
            grid.append([])
        elif m.isnumeric():
            for m in range(int(m)):
                grid[n].append(" ")
        else:
            grid[n].append(m)
        i += 1
    return grid

alphabet = list(string.ascii_lowercase)
LEDbar = hardwarescripts.the74HC595()

stockfish = Stockfish("/home/pi/full-stack-chessboard/stockfish", depth=8)
stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

example = ["e2", "e4"]
print(updatefen(example))
stockfish.set_fen_position(updatefen(example))
example = ["d7", "d5"]
print(updatefen(example))

LEDbar.setvalue([1, 1, 1, 1, 0, 0, 1, 0, 1, 1])
time.sleep(1)
LEDbar.clear()
#updateboard()

RFID = SimpleMFRC522()
print(RFID.read())



while True:
    print("now")
    print(RFID.read_no_block())
    time.sleep(10)
