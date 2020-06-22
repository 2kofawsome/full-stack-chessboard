from stockfish import Stockfish
import string, time, os, datetime
import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522
import hardwarescripts

def togrid(
    fen,
):  # FEN without information at the end, eg "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    """
    Takes FEN (without extra information at end) and returns a grid

    args: fen[0]
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
    returns: grid[0]
        [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''], ['', '', '', '', 'P', '', '', ''], ['', '', '', '', '', '', '', ''], ['P', 'P', 'P', 'P', '', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
    """
    grid = []
    fen = fen.split("/")
    for n in range(len(fen)):
        grid.append([])
        for m in fen[n]:
            if m.isnumeric():
                for x in range(int(m)):
                    grid[n].append("")
            else:
                grid[n].append(m)
    grid = grid[::-1]

    return grid


def tofen(grid):
    """
    Takes grid and returns a FEN (without extra information at end)

    args: grid[0]
        [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''], ['', '', '', '', 'P', '', '', ''], ['', '', '', '', '', '', '', ''], ['P', 'P', 'P', 'P', '', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
    returns: fen[0]
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
    """
    fen = ""

    for n in reversed(grid):
        for m in n:
            if m == "":
                if fen[-1].isnumeric():
                    fen = fen[:-1] + str(int(fen[-1]) + 1)
                else:
                    fen += "1"
            else:
                fen += m
        fen += r"/"
    fen = fen[:-1]

    return fen


def updatepgn(algebraic):
    """
    Updates and saves PGN based on a valid move

    args: algebraic move
        ["e2", "e4"]
    returns: None
    """
    fen = stockfish.get_fen_position()
    fen = fen.split(" ")

    saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "a")

    move = ""
    if fen[1] == "w":
        saved.write(fen[5] + ". ")

    grid = togrid(fen[0])

    last = grid[int(algebraic[0][1]) - 1][alphabet.index(algebraic[0][0])]
    next = grid[int(algebraic[1][1]) - 1][alphabet.index(algebraic[1][0])]


    if last.upper() == "K" and algebraic[0][0] == "e" and algebraic[1][0] == "g": #castling
        saved.write("O-O")
    elif last.upper() == "K" and algebraic[0][0] == "e" and algebraic[1][0] == "c":
        saved.write("O-O-O")
    else:
        if last != "p" and last != "P":
            saved.write(last.upper())

            possibilities = []
            for n in range(8):
                for m in range(8):
                    if grid[n][m] == last:
                        possibilities.append(alphabet[m] + str(n + 1))
            possibilities.remove(algebraic[0])
            conflicting = []
            for n in possibilities:
                if stockfish.is_move_correct(n + algebraic[1]):
                    conflicting.append(n)
            add = "  "
            for n in conflicting:
                if algebraic[0][0] != n[0] and (add[1] == " " or add[1] == n[1]):  # letter
                    add = algebraic[0][0] + add[1]
                elif algebraic[0][1] != n[1] and (
                        add[0] == " " or add[0] == n[0]
                ):  # number
                    add = add[0] + algebraic[0][1]
            add = add.replace(" ", "")
            saved.write(add)

        if next != "":
            if last == "p" or last == "P":
                saved.write(algebraic[0][0])
            saved.write("x")

        saved.write(algebraic[1])

    saved.write(" ")
    saved.close()


def updatefen(algebraic):
    """
    Updates current fen position based on a valid move

    args: algebraic move
        ["e2", "e4"]
    returns: fen
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    """
    fen = stockfish.get_fen_position()
    fen = fen.split(" ")

    grid = togrid(fen[0])

    last = grid[int(algebraic[0][1]) - 1][alphabet.index(algebraic[0][0])]
    next = grid[int(algebraic[1][1]) - 1][alphabet.index(algebraic[1][0])]

    # 3 castling "KQkq"
    if last == "k":
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

    # 4 en passent
    if (last == "P" or last == "p") and abs(
        int(algebraic[0][1]) - int(algebraic[1][1])
    ) == 2:
        fen[3] = algebraic[0][0] + str(
            int((int(algebraic[0][1]) + int(algebraic[1][1])) / 2)
        )
    else:
        fen[3] = "-"

    # 5 half moves since last capture or pawn movement
    if last == "P" or last == "p" or next != "":
        fen[4] = "0"
    else:
        fen[4] = str(int(fen[4]) + 1)

    # 1 moves
    grid[int(algebraic[1][1]) - 1][alphabet.index(algebraic[1][0])] = last
    grid[int(algebraic[0][1]) - 1][alphabet.index(algebraic[0][0])] = ""
    if last == "K":
        if algebraic[0][0] == "e" and algebraic[1][0] == "g":
            grid[0][5] = "R"
        elif algebraic[0][0] == "e" and algebraic[1][0] == "c":
            grid[0][3] = "R"
    elif last == "k":
        if algebraic[0][0] == "e" and algebraic[1][0] == "g":
            grid[7][5] = "r"
        elif algebraic[0][0] == "e" and algebraic[1][0] == "c":
            grid[7][3] = "r"
    fen[0] = tofen(grid)

    # 6 incremented after blacks move
    if fen[1] == "b":
        fen[5] = str(int(fen[5]) + 1)

    # 2 black or white
    if fen[1] == "w":
        fen[1] = "b"
    else:
        fen[1] = "w"

    fen = " ".join(fen)
    return fen


def updateboard(algebraic):
    """
    Unknown

    args: algebraic move
        ["e2", "e4"]
    returns: None

    """

    fen = updatefen(algebraic)
    updatepgn(algebraic)
    stockfish.set_fen_position(fen)

    evaluation = stockfish.get_evaluation()
    if evaluation["type"] == "mate":
        if evaluation["value"] < 5:
            if fen[1] == "b":
                led = [0,0,0,0,0,0,0,0,0,1]
            else:
                led = [0,1,1,1,1,1,1,1,1,1]
        else:
            if fen[1] == "b":
                led = [0,0,0,0,0,0,0,0,1,1]
            else:
                led = [0,0,1,1,1,1,1,1,1,1]
    else:
        if evaluation["value"] >= 1000:
            led = [0,0,1,1,1,1,1,1,1,1]
        elif evaluation["value"] < 1000 and evaluation["value"] >= 500:
            led = [0,0,0,1,1,1,1,1,1,1]
        elif evaluation["value"] < 500 and evaluation["value"] >= 100:
            led = [0,0,0,0,1,1,1,1,1,1]
        elif evaluation["value"] < 100 and evaluation["value"] > -100:
            led = [0,0,0,0,0,1,1,1,1,1]
        elif evaluation["value"] <= -100 and evaluation["value"] > -500:
            led = [0,0,0,0,0,0,1,1,1,1]
        elif evaluation["value"] <= -500 and evaluation["value"] > -1000:
            led = [0,0,0,0,0,0,0,1,1,1]
        elif evaluation["value"] <= -1000:
            led = [0,0,0,0,0,0,0,0,1,1]

    LEDbar.setvalue(led)
    print(evaluation)

    # check best move (skip if players turn)

    # send to hardware
    # print(best)

def singleplayer():
    pass
    # make it single player
def multiplayer():
    pass
    # make it multi player
def boardoff():
    pass
    # shut down procedure + edit game to say terminated part way through

def main():  # this should loop
    """
    Unknown

    args:
    returns:

    """



    # Tracks board/reed switch movements

    # once player turn is determined


    # figure out what board/move makes sense from hardware

    example = ["e8", "f8"] # castling uses king movement only

    if stockfish.is_move_correct(
        "".join(example)
    ):
        updateboard(example)


def newgame():
    """
    Unknown

    args:
    returns:

    """

    # output "scan your king"
    # RFID.read()

    # set single or double

    # choose difficulty

    saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "w")
    saved.write('[Event "Unknown"]\n[Site "Unknown"]\n[Date "')
    saved.write(date)
    saved.write('"]\n[Round "')
    saved.write(str(round))
    saved.write('"]\n[White "')
    saved.write("Player")  # Determined by above
    saved.write('"]\n[Black "')
    saved.write("AI - Level __")  # Determined by above
    saved.write('"]\n[Result "*"]\n\n')
    saved.close()

    stockfish.set_fen_position(
        "r2qk2r/pppppbpp/8/3B4/3PP3/2P1QP2/PP4PP/4K2R b kq - 0 1"
    )

    main()


def startup():
    """
    Unknown

    args:
    returns:

    """

    # switch for LED is hardware only (no software)
    #gpio.add_event_detect(37, gpio.RISING, callback=singleplayer) # single/multi switch
    #gpio.add_event_detect(37, gpio.FALLING, callback=multiplayer)

    #gpio.add_event_detect(37, gpio.RISING) # Button 1
    #gpio.event_detected(37) # True or False
    #gpio.add_event_detect(37, gpio.RISING) # Button 2
    #if gpio.event_detected(37): # True or False
     #   print(RFID.read_no_block())

    #gpio.add_event_detect(37, gpio.RISING, callback=boardoff)

    newgame()


alphabet = list(string.ascii_lowercase)
LEDbar = hardwarescripts.the74HC595()
RFID = SimpleMFRC522()
stockfish = Stockfish("/home/pi/full-stack-chessboard/stockfish")

date = datetime.datetime.now().strftime("%Y.%m.%d")
if "PGNs" not in os.listdir(".."):
    os.makedirs("../PGNs")
if date not in os.listdir("../PGNs"):
    os.makedirs("../PGNs/" + date)
round = 1
for n in os.listdir("../PGNs/" + date):
    round += 1

startup()