from stockfish import Stockfish
import string, time
import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522

class LEDBar():

    def __init__(self):
        LEDBar.data = 11 #DS
        LEDBar.parallel = 12 #ST_CP
        LEDBar.serial = 13 #SH_CP
        self.setupboard()
        self.clear()

    def setupboard(self):
        gpio.setup(LEDBar.data, gpio.OUT)
        gpio.output(LEDBar.data, gpio.LOW)
        gpio.setup(LEDBar.parallel, gpio.OUT)
        gpio.output(LEDBar.parallel, gpio.LOW)
        gpio.setup(LEDBar.serial, gpio.OUT)
        gpio.output(LEDBar.serial, gpio.LOW)

    def output(self): #ST_CP
        gpio.output(LEDBar.parallel, gpio.HIGH)
        gpio.output(LEDBar.parallel, gpio.LOW)

    def tick(self): #SH_CP
        gpio.output(LEDBar.serial, gpio.HIGH)
        gpio.output(LEDBar.serial, gpio.LOW)

    def clear(self): #SH_CP
        self.setvalue([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def setvalue(self, value):
        for n in value[1:-1]:
            if n == 0:
                gpio.output(LEDBar.data, gpio.LOW)
            else:
                gpio.output(LEDBar.data, gpio.HIGH)
            LEDBar.tick(self)
        self.output()
        if value[0] == 1: #Other pin
            pass
        else:
            pass
        if value[-1] == 1: #Other pin
            pass
        else:
            pass

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
gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
LEDbar = LEDBar()

stockfish = Stockfish("/home/pi/full-stack-chessboard/stockfish", depth=8)
stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

print([1, 1, 1, 1, 0, 0, 1, 0, 1, 1][1:-1])
LEDbar.setvalue([1, 1, 1, 1, 0, 0, 1, 0, 1, 1])
time.sleep(1)
LEDbar.clear()
updateboard()



reader = SimpleMFRC522()
while True:
    try:
        id,text = reader.read()
        print(id, text)
        time.sleep(1)
    finally:
        gpio.cleanup()