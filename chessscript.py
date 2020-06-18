from stockfish import Stockfish
import string, time, os, datetime
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

    # figure out what board/move makes sense from hardware

    ### At this point it is alegraic notation
    example = ["e2", "e4"]


    if not stockfish.is_move_correct("".join(example)): #special for castling, just king movement
        # do somethign if move not valid
        pass


    fen = updatefen(example)
    stockfish.set_fen_position(fen)

    # algebraic to FIDE
    # update saved PGN

    # check best move (skip if players turn)
    # send to hardware

    # check evaluation
    LEDbar.setvalue([1, 1, 1, 1, 0, 0, 1, 0, 1, 1])
    time.sleep(1)
    LEDbar.clear()


def getboard(): # will be determined with hardware
    return [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]]

def updatepgn(algebraic):
    global PGN
    fen = stockfish.get_fen_position()
    fen = fen.split(" ")

    move = ""
    if fen[1] == "w":
        move = move + fen[5] + ". "

    if algebraic[0] == "O-O-O" or algebraic[0] == "O-O":
        move = move + algebraic[0]

    else:
        grid = togrid(fen[0])
        last = grid[-int(algebraic[0][1])][alphabet.index(algebraic[0][0])]
        next = grid[-int(algebraic[1][1])][alphabet.index(algebraic[1][0])]

        if last != "p" and last != "P":
            move = move + last.upper()

        possibilities = []
        for n in range(8):
            for m in range(8):
                if grid[n][m] == last:
                    possibilities.append(alphabet[m]+str(8-n))
        possibilities.remove(algebraic[0])
        conflicting = []
        for n in possibilities:
            if stockfish.is_move_correct(n+algebraic[1]):
                conflicting.append(n) #a1
        add = "  "
        for n in conflicting:
            if algebraic[0][0] != n[0] and (add[1] == " " or add[1] == n[1]): #letter
                add = algebraic[0][0] + add[1]
            elif algebraic[0][1] != n[1] and (add[0] == " " or add[0] == n[0]): #number
                add = add[0] + algebraic[0][1]
        add = add.replace(" ", "")
        move = move + add


        if next != "":
            move = move + "x"

        move = move + algebraic[1]

    move = move + " "

    PGN["moves"] = PGN["moves"] + move

    saved = open(("../PGNs/" + PGN["Date"] + "/game" + str(round) + ".txt"), "w")
    saved.write(PGN["moves"])
    saved.close()
    return PGN


def updatefen(algebraic):
    fen = stockfish.get_fen_position()
    fen = fen.split(" ")

    grid = togrid(fen[0])

    if algebraic[0] == "O-O-O" or algebraic[0] == "O-O":
        fen[3] = "-"

        fen[4] = str(int(fen[4]) + 1)

        if fen[1] == "b":
            fen[2] = fen[2].replace("q", "")
            fen[2] = fen[2].replace("k", "")
        elif fen[1] == "w":
            fen[2] = fen[2].replace("Q", "")
            fen[2] = fen[2].replace("K", "")
        if fen[2] == "":
            fen[2] = "-"

        if fen[1] == "b":
            if algebraic[0] == "O-O-O":
                grid[0][0] = ""
                grid[0][2] = "k"
                grid[0][3] = "r"
                grid[0][4] = ""
            if algebraic[0] == "O-O":
                grid[0][4] = ""
                grid[0][5] = "r"
                grid[0][6] = "k"
                grid[0][7] = ""
        if fen[1] == "w":
            if algebraic[0] == "O-O-O":
                grid[7][0] = ""
                grid[7][2] = "K"
                grid[7][3] = "R"
                grid[7][4] = ""
            if algebraic[0] == "O-O":
                grid[7][4] = ""
                grid[7][5] = "R"
                grid[7][6] = "K"
                grid[7][7] = ""

        fen[0] = "" #1 moves
        for n in grid:
            for m in n:
                if m == "":
                    if fen[0][-1].isnumeric():
                        fen[0] = fen[0][:-1] + str(int(fen[0][-1]) + 1)
                    else:
                        fen[0] += "1"
                else:
                    fen[0] += m
            fen[0] += r"/"
        fen[0] = fen[0][:-1]

    else:
        last = grid[-int(algebraic[0][1])][alphabet.index(algebraic[0][0])]
        next = grid[-int(algebraic[1][1])][alphabet.index(algebraic[1][0])]


        if last == "P" or last == "p" or next != "": #5 half moves since last capture or pawn movement
            fen[4] = "0"
        else:
            fen[4] = str(int(fen[4]) + 1)

        # 4 en passent
        if (last == "P" or last == "p") and abs(int(algebraic[0][1])-int(algebraic[1][1])) == 2:
            fen[3] = algebraic[0][0] + str(int((int(algebraic[0][1])+int(algebraic[1][1]))/2))
        else:
            fen[3] = "-"

        if last == "k": # 3 castling "KQkq"
            fen[2] = fen[2].replace("k", "")
            fen[2] = fen[2].replace("q", "")
        elif last == "K":
            fen[2] = fen[2].replace("K", "")
            fen[2] = fen[2].replace("Q", "")
        elif last == "r":
            if algebraic[0][0] == "a":
                fen[2] = fen[2].replace("q", "")
            elif algebraic[0][0] == "h":
                fen[2] = fen[2].replace("k", "")
        elif last == "R":
            if algebraic[0][0] == "a":
                fen[2] = fen[2].replace("Q", "")
            elif algebraic[0][0] == "h":
                fen[2] = fen[2].replace("K", "")
        if fen[2] == "":
            fen[2] = "-"

        fen[0] = "" #1 moves
        grid[-int(algebraic[1][1])][alphabet.index(algebraic[1][0])] = last
        grid[-int(algebraic[0][1])][alphabet.index(algebraic[0][0])] = ""
        for n in grid:
            for m in n:
                if m == "":
                    if fen[0][-1].isnumeric():
                        fen[0] = fen[0][:-1] + str(int(fen[0][-1]) + 1)
                    else:
                        fen[0] += "1"
                else:
                    fen[0] += m
            fen[0] += r"/"
        fen[0] = fen[0][:-1]

    if fen[1] == "b": #6 incremented after blacks move
        fen[5] = str(int(fen[5]) + 1)

    if fen[1] == "w": #2 black or white
        fen[1] = "b"
    else:
        fen[1] = "w"

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
                grid[n].append("")
        else:
            grid[n].append(m)
        i += 1
    return grid


def main():
    # Tracks 2 buttons
    button1 = False
    if button1 == True:
        print(RFID.read_no_block())
    # Tracks 3 switches
    # Tracks board/reed switch movements



    stockfish.set_fen_position("r3k2r/pppppppp/8/8/7b/8/PPPPPPPP/R3K2R w KQkq - 0 1")

    example = ["O-O-O"]
    print(updatefen(example))
    print(updatepgn(example))

    input()



alphabet = list(string.ascii_lowercase)
LEDbar = hardwarescripts.the74HC595()
RFID = SimpleMFRC522()
stockfish = Stockfish("/home/pi/full-stack-chessboard/stockfish", depth=8)

PGN = {"Event":"Unknown", "Site":"Unknown", "Date":"", "Round":"",
       "White":"", "Black":"", "Result":"", "moves":""}
date =  datetime.datetime.now()
PGN["Date"] = date.strftime("%Y.%m.%d")

if "PGNs" not in os.listdir(".."):
    os.makedirs("../PGNs")
if PGN["Date"] not in os.listdir("../PGNs"):
    os.makedirs("../PGNs/" + PGN["Date"])
round = 1
for n in os.listdir("../PGNs/" + PGN["Date"]):
    round += 1
saved = open(("../PGNs/" + PGN["Date"] + "/game" + str(round) + ".txt"), "w")
saved.write("")
saved.close()

PGN["Round"] = str(round)
PGN["White"] = "Unknown" #AI or player
PGN["Black"] = "Unknown" #AI or player
PGN["Result"] = "*"

stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

while True:
    main()

