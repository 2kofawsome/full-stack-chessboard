from stockfish import Stockfish
import string, time, os, datetime
import RPi.GPIO as GPIO
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
                if fen == "":
                    fen += "1"
                elif fen[-1].isnumeric():
                    fen = fen[:-1] + str(int(fen[-1]) + 1)
                else:
                    fen += "1"
            else:
                fen += m
        fen += r"/"
    fen = fen[:-1]

    return fen


def ischeck():
    """
    Returns True if player with current move is in check

    args: None
    returns: True or False
    """
    fen = stockfish.get_fen_position()
    fen = fen.split(" ")

    if fen[1] == "w":
        pieces = ["K", "n", "p", "r", "b", "q"]
    else:
        pieces = ["k", "N", "P", "R", "B", "Q"]

    grid = togrid(fen[0])

    for rank in range(8):
        for file in range(8):
            if grid[rank][file] == pieces[0]:
                break
        else:
            continue
        break

    # knight
    knights = [
        [rank + 2, file + 1],
        [rank + 2, file - 1],
        [rank - 2, file + 1],
        [rank - 2, file - 1],
        [rank + 1, file + 2],
        [rank + 1, file - 2],
        [rank - 1, file + 2],
        [rank - 1, file - 2],
    ]
    for n in knights:
        if (
            not (n[0] < 0 or n[0] > 7 or n[1] < 0 or n[1] > 7)
            and grid[n[0]][n[1]] == pieces[1]
        ):
            return True

    # pawns
    if pieces[0] == "K":
        pawns = [[rank + 1, file + 1], [rank + 1, file - 1]]
    else:
        pawns = [[rank - 1, file + 1], [rank - 1, file - 1]]
    for n in pawns:
        if (
            not (n[0] < 0 or n[0] > 7 or n[1] < 0 or n[1] > 7)
            and grid[n[0]][n[1]] == pieces[2]
        ):
            return True

    # rook + queen
    for n in range(rank + 1, 8):
        if grid[n][file] == "":
            continue
        else:
            if grid[n][file] == pieces[3] or grid[n][file] == pieces[5]:
                return True
            break
    for n in range(file + 1, 8):
        if grid[rank][n] == "":
            continue
        else:
            if grid[rank][n] == pieces[3] or grid[rank][n] == pieces[5]:
                return True
            break
    for n in range(1, rank + 1):
        if grid[rank - n][file] == "":
            continue
        else:
            if grid[rank - n][file] == pieces[3] or grid[rank - n][file] == pieces[5]:
                return True
            break
    for n in range(1, file + 1):
        if grid[rank][file - n] == "":
            continue
        else:
            if grid[rank][file - n] == pieces[3] or grid[rank][file - n] == pieces[5]:
                return True
            break

    # bishop + queen
    n = [rank + 1, file + 1]
    while not (n[0] < 0 or n[0] > 7 or n[1] < 0 or n[1] > 7):
        if grid[n[0]][n[1]] == "":
            n = [n[0] + 1, n[1] + 1]
            continue
        else:
            if grid[n[0]][n[1]] == pieces[4] or grid[n[0]][n[1]] == pieces[5]:
                return True
            break
    n = [rank + 1, file - 1]
    while not (n[0] < 0 or n[0] > 7 or n[1] < 0 or n[1] > 7):
        if grid[n[0]][n[1]] == "":
            n = [n[0] + 1, n[1] - 1]
            continue
        else:
            if grid[n[0]][n[1]] == pieces[4] or grid[n[0]][n[1]] == pieces[5]:
                return True
            break
    n = [rank - 1, file + 1]
    while not (n[0] < 0 or n[0] > 7 or n[1] < 0 or n[1] > 7):
        if grid[n[0]][n[1]] == "":
            n = [n[0] - 1, n[1] + 1]
            continue
        else:
            if grid[n[0]][n[1]] == pieces[4] or grid[n[0]][n[1]] == pieces[5]:
                return True
            break
    n = [rank - 1, file - 1]
    while not (n[0] < 0 or n[0] > 7 or n[1] < 0 or n[1] > 7):
        if grid[n[0]][n[1]] == "":
            n = [n[0] - 1, n[1] - 1]
            continue
        else:
            if grid[n[0]][n[1]] == pieces[4] or grid[n[0]][n[1]] == pieces[5]:
                return True
            break

    # if nothing found
    return False


def tofide(algebraic):
    """
    Updates and saves PGN based on a valid move

    args: algebraic move
        ["e2", "e4"]
    returns: FIDE move
        "e4" or "Nxf3+" or "O-O-O"
    """
    fen = stockfish.get_fen_position()
    fen = fen.split(" ")

    fide = ""

    grid = togrid(fen[0])

    last = grid[int(algebraic[0][1]) - 1][alphabet.index(algebraic[0][0])]
    next = grid[int(algebraic[1][1]) - 1][alphabet.index(algebraic[1][0])]

    if (
        last.upper() == "K" and algebraic[0][0] == "e" and algebraic[1][0] == "g"
    ):  # castling
        fide = fide + "O-O"
    elif last.upper() == "K" and algebraic[0][0] == "e" and algebraic[1][0] == "c":
        fide = fide + "O-O-O"
    else:
        if last != "p" and last != "P":
            fide = fide + last.upper()

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
                if algebraic[0][0] != n[0] and (
                    add[1] == " " or add[1] == n[1]
                ):  # letter
                    add = algebraic[0][0] + add[1]
                elif algebraic[0][1] != n[1] and (
                    add[0] == " " or add[0] == n[0]
                ):  # number
                    add = add[0] + algebraic[0][1]
            add = add.replace(" ", "")
            fide = fide + add

        if next != "":
            if last == "p" or last == "P":
                fide = fide + algebraic[0][0]
            fide = fide + "x"

        fide = fide + algebraic[1]

    return fide


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

    ep = fen[3]
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
    elif last == "P" and algebraic[1] == ep:
        grid[int(algebraic[1][1]) - 2][alphabet.index(algebraic[1][0])] = ""
    elif last == "p" and algebraic[1] == ep:
        grid[int(algebraic[1][1])][alphabet.index(algebraic[1][0])] = ""

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

    saved.write(tofide(algebraic))

    fen = updatefen(algebraic)
    stockfish.set_fen_position(fen)

    if ischeck():
        if stockfish.get_best_move() == None:
            saved.write("#")
            saved.write(" ")
            saved.close()
            return False
        else:
            saved.write("+")
    saved.write(" ")
    saved.close()

    return fen


def updateboard(algebraic):
    """
    Unknown

    args: algebraic move
        ["e2", "e4"]
    returns: None

    """

    fen = updatepgn(algebraic)
    if fen == False:
        return False

    try:
        evaluation = stockfish.get_evaluation()
        if evaluation["type"] == "mate":
            if evaluation["value"] < 5:
                if fen[1] == "b":
                    led = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
                else:
                    led = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            else:
                if fen[1] == "b":
                    led = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
                else:
                    led = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
        else:
            if evaluation["value"] >= 1000:
                led = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
            elif evaluation["value"] < 1000 and evaluation["value"] >= 500:
                led = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
            elif evaluation["value"] < 500 and evaluation["value"] >= 100:
                led = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
            elif evaluation["value"] < 100 and evaluation["value"] > -100:
                led = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
            elif evaluation["value"] <= -100 and evaluation["value"] > -500:
                led = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
            elif evaluation["value"] <= -500 and evaluation["value"] > -1000:
                led = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
            elif evaluation["value"] <= -1000:
                led = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
    except IndexError:
        led = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    LEDbar.setvalue(led)

    if stockfish.get_best_move() == None:  # stalemate
        return True

    difficulty = 0

    if player == "w":  # check best move (skip if players turn)
        if GPIO.input(29) == 1 and "w" not in fen:
            move = stockfish.get_best_move_time(33 * 1.5 ** (difficulty + 1))
            move = [move[:2], move[2:]]
            print(tofide(move))
    else:
        if GPIO.input(29) == 1 and "w" in fen:
            move = stockfish.get_best_move_time(33 * 1.5 ** (difficulty + 1))
            move = [move[:2], move[2:]]
            print(tofide(move))

    print()
    # send to hardware


def players(pin):
    pass
    # edit file to say mixed


def boardoff():
    pass
    # shut down procedure + edit game to say terminated part way through


def gameover(result):
    """
    Finishes Game after checkmate/stalemate/resign/draw

    args: result
        True or False
    returns: None

    """

    if result == True:
        print("Stalemate")
        saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "a")
        saved.write("1/2-1/2")
        saved.close()
        data = open(
            ("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r"
        ).readlines()
        data[6] = '[Result "1/2-1/2"]'
    else:
        fen = stockfish.get_fen_position()
        fen = fen.split(" ")
        if fen[1] == "b":
            print("White won")
            saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "a")
            saved.write("1-0")
            saved.close()
            data = open(
                ("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r"
            ).readlines()
            data[6] = '[Result "1-0"]'
        else:
            print("Black won")
            saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "a")
            saved.write("0-1")
            saved.close()
            data = open(
                ("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r"
            ).readlines()
            data[6] = '[Result "0-1"]'

    saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "w")
    saved.writelines(data)
    saved.close()

    print("New game?")
    GPIO.event_detected(31)
    while True:
        if GPIO.event_detected(31):
            break
        time.sleep(0.1)


def main():  # this should loop
    """
    Unknown

    args:
    returns:

    """

    while True:

        # Tracks board/reed switch movements

        # once player turn is determined

        # figure out what board/move makes sense from hardware

        print("give move in 'e2e4'")
        move = input()  # castling uses king movement only
        move = [move[:2], move[2:]]

        if stockfish.is_move_correct("".join(move)):
            status = updateboard(move)
            if status != None:  # True is stalemate, False is checkmate
                break
    gameover(status)


def newgame():
    global round, difficulty, player
    """
    Determines values required to start the game

    args: None
    returns: None

    """
    while True:

        # output "scan your king"
        # RFID.read()
        player = "w"  # for now

        # set single or double
        print("Against Engine or Against Player")
        print(GPIO.input(29))
        while True:
            time.sleep(0.1)
            if GPIO.event_detected(31):
                if GPIO.input(29) == 1:  # Single player
                    if player == "w":
                        white = "Player"
                        black = "AI"
                    else:
                        white = "AI"
                        black = "Player"
                else:  # multiplayer
                    white = "Player"
                    black = "Player"
                break

        time.sleep(0.2)
        GPIO.event_detected(31)  # need better way to clear these
        GPIO.event_detected(33)

        # choose difficulty
        difficulty = 0
        if white == "AI" or black == "AI":
            print("Determine Engine level")
            print("Difficulty: " + str(difficulty + 1))
            while True:
                GPIO.event_detected(33)
                time.sleep(0.2)
                if GPIO.event_detected(33):
                    if difficulty != 9:
                        difficulty += 1
                    else:
                        difficulty = 0
                    print("Difficulty: " + str(difficulty + 1))
                if GPIO.event_detected(31):
                    if white == "AI":
                        white = "AI Level " + str(difficulty + 1)
                    else:
                        black = "AI Level " + str(difficulty + 1)
                    break

        round = 1
        for n in os.listdir("../PGNs/" + date):
            round += 1

        saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "w")
        saved.write('[Event "Unknown"]\n[Site "Unknown"]\n[Date "')
        saved.write(date)
        saved.write('"]\n[Round "')
        saved.write(str(round))
        saved.write('"]\n[White "')
        saved.write(white)  # Determined by above
        saved.write('"]\n[Black "')
        saved.write(black)  # Determined by above
        saved.write('"]\n[Result "*"]\n\n')
        saved.close()

        stockfish.set_fen_position(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )

        LEDbar.setvalue([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

        main()


def startup():
    """
    Required to set up the program on start

    args: None
    returns: None

    """

    # switch for LED is hardware only (no software)
    GPIO.setup(29, GPIO.IN)
    GPIO.add_event_detect(29, GPIO.BOTH, callback=players)  # single/multi switch
    GPIO.setup(31, GPIO.IN)
    GPIO.add_event_detect(31, GPIO.RISING)  # Button 1
    GPIO.setup(33, GPIO.IN)
    GPIO.add_event_detect(33, GPIO.RISING)  # Button 2
    # if GPIO.event_detected(33): # True or False
    #   print(RFID.read_no_block())
    # detect 5 and 6 not being connected due to switch

    newgame()


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
alphabet = list(string.ascii_lowercase)
LEDbar = hardwarescripts.the74HC595()
RFID = SimpleMFRC522()
stockfish = Stockfish("/home/pi/full-stack-chessboard/stockfish", 1)

date = datetime.datetime.now().strftime("%Y.%m.%d")
if "PGNs" not in os.listdir(".."):
    os.makedirs("../PGNs")
if date not in os.listdir("../PGNs"):
    os.makedirs("../PGNs/" + date)

startup()
