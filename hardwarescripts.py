import time
import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)
reader = SimpleMFRC522()

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

class MFRC522():
    def test(self):
        reader = SimpleMFRC522()
        try:
            id, text = reader.read()
            print("RFID:", id, text)
        finally:
            gpio.cleanup()

    if __name__ == '__main__':
        test()
