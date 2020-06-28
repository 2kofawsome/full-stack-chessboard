import string, time, os, datetime, sys, re
import RPi.GPIO as GPIO
from stockfish import Stockfish
from mfrc522 import SimpleMFRC522
import driver74HC595
import lcddriver


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

    args: algebraic move, 3rd if pawn promotion
        ["e2", "e4"] or ["e2", "e4", "Q"]
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

        if len(algebraic) == 3:
            fide = fide + "=" + algebraic[2]

    return fide


def togrid(fen):
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

    args: grid
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


def updatefen(algebraic):
    """
    Updates current fen position based on a valid move

    args: algebraic move, 3rd if pawn promotion
        ["e2", "e4"] or ["e2", "e4", "Q"]
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
    if len(algebraic) == 2:
        grid[int(algebraic[1][1]) - 1][alphabet.index(algebraic[1][0])] = last
    else:  # len of 3 if pawn promotion
        grid[int(algebraic[1][1]) - 1][alphabet.index(algebraic[1][0])] = algebraic[2]
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

    args: algebraic move, 3rd if pawn promotion
        ["e2", "e4"] or ["e2", "e4", "Q"]
    returns: None or False if Checkmate
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
    Once move is determined, runs funcitons neccesary to update board position

    args: algebraic move, 3rd if pawn promotion
        ["e2", "e4"] or ["e2", "e4", "Q"]
    returns: None or False if Checkmate
    """
    global gamefens
    fen = updatepgn(algebraic)
    if fen == False:
        return False
    gamefens["1"].append(fen)

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
    except IndexError as E:
        print(E)
        led = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    LEDbar.setvalue(led)

    print(moves)
    print()

    if stockfish.get_best_move() == None:  # stalemate
        return True


def rebuildpgn(fen):
    """
    Rebuilds PGN based on FEN from rebuildfen

    args: fen
        "rn1qkbnr/pppbpp1p/6p1/3pP2Q/8/8/PPPP1PPP/RNB1KBNR w KQkq - 0 4"
    returns: None
    """
    global gamefens

    fen = fen.split(" ")

    branch, node = None, None
    for n in reversed(sorted(gamefens.keys())):
        for m in range(len(gamefens[n])):
            node = m # will always be either node or max length if no branch exists
            if gamefens[n][m][0] == fen[0]:
                branch = n
                break
        else:
            continue
        break

    data = open(
        ("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r"
    ).readlines()

    if branch == None:
        # What happens if have to create a FEN
        for n in range(len(data)): # What happens when previous FEN exists
            if data[n] == '[SetUp "1"]\n':
                lastfen = data[n+1] #save fen first
                del data[n]
                del data[n]

        # remove old {}
        old = data[-1]
        old = old.split("{")
        for n in range(len(old)):
            for m in range(len(n)):
                if m == "{":
                    old[n] = old[n][:m]
        old = "".join(old)

        data[-1] = "{" + lastfen[:-1] + " " + old + '}\n'

        data.append('[SetUp "1"]\n')
        data.append('[FEN "' + " ".join(fen) + '"]\n')

        if fen[1] == "b":
            data.append(str(node % 2 + 1) + "...")
        else:
            data.append("")

        # resets game fens
        gamefens = {}
        gamefen = []
        for n in node:
            gamefen.append("")
        gamefens["0"] = gamefen[:]

    else:
        # What happens if existed in a past state
        print(branch) #0 indexed (start position)
        print(node) #0 indexed



        if branch != 0: #if not in master branch
            # move to master branch, putting everything after that point in master branch to a {}
                # delete any {} existing inside new {} of old master
            # take everything after that point in side branch and keep in {}
            pass

        old = data[-1]
        olds = re.findall("\{[^{}]+\}", old)

        branches = []
        for n in gamefens.keys():
            branches.append(n)
        branches.sort()

        for n in range(len(branches)):
            if int(branches[n]) > branch:
                del gamefens[branches[n]]
                old.replace(olds[n], "")

        # add all moves afetr this node to {}


        data[-1] = old






    data = open(
        ("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r"
    ).readlines()
    saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "w")
    saved.writelines(data)
    saved.close()
    # Series of fens at the bottom of pgn that will be chacked to see if ever lined up
    # if so, comment out all moves after that point
    # if not, custom starting position and new moves from 1.
    # need way to go over even commented out code if further RFID adjustments
    # need way to comment out custom starting position if further RFID adjustments

    print(fen)

    pass


def rebuildfen(grid):
    """
    Rebuilds FEN based on grid from rebuildpieces

    args: grid
        [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''], ['', '', '', '', 'P', '', '', ''], ['', '', '', '', '', '', '', ''], ['P', 'P', 'P', 'P', '', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
    returns: fen
        "rn1qkbnr/pppbpp1p/6p1/3pP2Q/8/8/PPPP1PPP/RNB1KBNR w KQkq - 0 4"
    """
    # Series of fens at the bottom of pgn that will be chacked to see if ever lined up
    # if not, build fen with fingers crossed for en passent, kings, etc (ask user whos turn)

    print(grid)

    pass


def rebuildpieces(grid):
    """
    Edits pieces grid according to players RFID scans

    args: grid
        [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['', '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''], ['', '', '', '', 'P', '', '', ''], ['', '', '', '', '', '', '', ''], ['P', 'P', 'P', 'P', '', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]
    returns: None
    """
    time.sleep(0.5)
    # entirely user stuff
    # scan a piece or cancel
    # scan resultant pieces
    # loop both of above if required

    print(grid)

    pass


def enginemove(fen):
    """
    Sends move to display if it is engine's turn

    args: fen
        "rn1qkbnr/pppbpp1p/6p1/3pP2Q/8/8/PPPP1PPP/RNB1KBNR w KQkq - 0 4"
    returns: None
    """
    if "Engine" in white or "Engine" in black:
        LCD.update("Calculating.", 1)
        LCD.update("", 2)
        if player == "w" and "w" not in fen:  # check best move (skip if players turn)
            move = stockfish.get_best_move_time(33 * 1.5 ** (difficulty + 1))
            if len(move) == 5:
                move = [move[:2], move[2:4], move[4].lower()]
            else:
                move = [move[:2], move[2:4]]
            LCD.update(tofide(move) + " (" + move[0] + " -> " + move[1] + ")", 1)
            LCD.update("  Scan Pieces ->", 2)
        elif player == "b" and "w" in fen:
            move = stockfish.get_best_move_time(33 * 1.5 ** (difficulty + 1))
            if len(move) == 5:
                move = [move[:2], move[2:4], move[4].upper()]
            else:
                move = [move[:2], move[2:4]]
            LCD.update(tofide(move) + " (" + move[0] + " -> " + move[1] + ")", 1)
            LCD.update("  Scan Pieces ->", 2)


def main():  # this should loop
    """
    Listens for pieces movements, makes sure they are okay, then triggers update

    args: None
    returns: None

    """
    while True:
        fen = stockfish.get_fen_position()
        fen = fen.split(" ")
        enginemove(fen)
        if fen[1] == "w" and "Engine" not in white:
            LCD.update("White's move", 1)
        elif fen[1] == "b" and "Engine" not in black:
            LCD.update("Black's move", 1)
        LCD.update("  Scan Pieces ->", 2)
        grid = togrid(fen[0])

        changed = False
        GPIO.event_detected(31)  # clear detection
        GPIO.event_detected(33)
        while True:
            # Tracks board/reed switch movements
            # once player turn is determined
            # figure out what board/move makes sense from hardware
            if GPIO.event_detected(33):
                break
            elif GPIO.event_detected(31):
                changed = True
                rebuildpieces(grid)
                break
        if changed == True:
            continue

        print("give move in 'e2e4'")
        move = input()  # castling uses king movement only
        print()
        move = [move[:2], move[2:]]

        last = grid[int(move[0][1]) - 1][alphabet.index(move[0][0])]
        if (last == "P" and move[1][1] == "8") or (last == "p" and move[1][1] == "1"):
            LCD.update("Scan Promoted Piece", 1)
            LCD.update("", 2)
            while True:
                piece = RFID.read()[1][0]
                if not (
                    piece.upper() == "Q"
                    or piece.upper() == "R"
                    or piece.upper() == "B"
                    or piece.upper() == "N"
                ):
                    LCD.update("Must be a Queen, Knight, Rook, or Bishop", 2)
                elif piece.isupper() and last.islower():
                    LCD.update("Must be a Black", 2)
                elif piece.islower() and last.isupper():
                    LCD.update("Must be a White", 2)
                else:
                    break
            move.append(piece)

        if not stockfish.is_move_correct("".join(move)):
            LCD.update("Move Not Correct", 2)
            time.sleep(1)
            continue

        status = updateboard(move)
        if status != None:  # True is stalemate, False is checkmate
            break
    gameover(status)


def players(pin):
    """
    Cleans up hardware, edits game saves, turns off system safely

    args: None
    returns: None
    """
    global white, black
    try:
        data = open(
            ("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r"
        ).readlines()
    except FileNotFoundError:
        if GPIO.input(29) == 1:  # Single player
            if player == "w":
                white = "Player"
                black = "Engine"
            else:
                white = "Engine"
                black = "Player"
        else:  # multiplayer
            white = "Player"
            black = "Player"
        return

    # if data[-1] == '\n':
    #    os.remove("../PGNs/" + date + "/Game" + str(round) + ".txt")

    if GPIO.input(29) == 0:
        if player == "w" and "Engine" in data[5]:
            data[5] = '[Black "' + black + ' -> Player"]\n'
            black = "Player"
        elif player == "b" and "Engine" in data[4]:
            data[4] = '[White "' + white + ' -> Player"]\n'
            white = "Player"
    saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "w")
    saved.writelines(data)
    saved.close()

    # if move, show Engine or dont


def gameover(result):
    """
    Finishes Game after checkmate/stalemate/resign/draw

    args: result
        True or False
    returns: None
    """
    if result == True:
        LCD.update("Stalemate", 1)
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
            LCD.update("Checkmate for White", 1)
            saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "a")
            saved.write("1-0")
            saved.close()
            data = open(
                ("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r"
            ).readlines()
            data[6] = '[Result "1-0"]'
        else:
            LCD.update("Checkmate for Black", 1)
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

    GPIO.event_detected(31)  # clear detection
    LCD.update("     New Game ->", 2)
    while True:
        if GPIO.event_detected(31):
            break
        time.sleep(0.1)


def newgame():
    global round, difficulty, player, white, black, gamefens
    """
    Determines values required to start a new game

    args: None
    returns: None
    """
    while True:
        round = 1
        for n in os.listdir("../PGNs/" + date):
            round += 1

        # Makes sure pieces are set up properly

        # output "scan your king"
        # RFID.read()
        player = "w"  # for now

        # sets Engine/Player
        GPIO.event_detected(31)  # clear detection
        LCD.update("Toggle Engine Switch", 1)
        LCD.update("     Continue ->", 2)
        while True:
            time.sleep(0.1)
            if GPIO.event_detected(31):
                if GPIO.input(29) == 1:  # Single player
                    if player == "w":
                        white = "Player"
                        black = "Engine"
                    else:
                        white = "Engine"
                        black = "Player"
                else:  # multiplayer
                    white = "Player"
                    black = "Player"
                break

        # choose difficulty
        difficulty = 0
        if white == "Engine" or black == "Engine":
            time.sleep(0.2)
            GPIO.event_detected(31)  # clear detection
            GPIO.event_detected(33)
            LCD.update("Engine Level: " + str(difficulty + 1), 1)
            LCD.update("     Continue ->", 2)
            while white == "Engine" or black == "Engine":
                time.sleep(0.05)
                if GPIO.event_detected(33):
                    if difficulty != 9:
                        difficulty += 1
                    else:
                        difficulty = 0
                    LCD.update("Engine Level: " + str(difficulty + 1), 1)
                    time.sleep(0.1)
                    GPIO.event_detected(33)  # clear detection
                if GPIO.event_detected(31):
                    stockfish.set_skill_level(difficulty * 2)
                    if white == "Engine":
                        white = "Engine Level " + str(difficulty + 1)
                    else:
                        black = "Engine Level " + str(difficulty + 1)
                    break

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

        gamefens = {"0":[]}
        # stockfish.set_fen_position("k7/7P/1K6/8/8/8/8/8 w - - 0 1")

        LEDbar.setvalue([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

        main()


def boardoff():
    """
    Cleans up hardware, edits game saves, turns off system safely

    args: None
    returns: None
    """
    # LCD.clear() Runs in other process
    data = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "r").readlines()
    if data[6] == '[Result "*"]\n':
        data.insert(7, '[Termination "abandoned"]\n')
        saved = open(("../PGNs/" + date + "/Game" + str(round) + ".txt"), "w")
        saved.writelines(data)
        saved.close()
    if data[-1] == "\n":
        os.remove("../PGNs/" + date + "/Game" + str(round) + ".txt")

    LEDbar.clear()
    GPIO.cleanup()

    # will also shutdown raspberry pi


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
LCD = lcddriver.lcd()
LEDbar = driver74HC595.the74HC595()
RFID = SimpleMFRC522()
stockfish = Stockfish("/home/pi/full-stack-chessboard/stockfish", 1)

date = datetime.datetime.now().strftime("%Y.%m.%d")
if "PGNs" not in os.listdir(".."):
    os.makedirs("../PGNs")
if date not in os.listdir("../PGNs"):
    os.makedirs("../PGNs/" + date)

try:
    time.sleep(1)
    startup()
except KeyboardInterrupt:
    boardoff()
