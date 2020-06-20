import time
import RPi.GPIO as gpio

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)


class the74HC595:
    def __init__(self):
        the74HC595.data = 11  # DS
        the74HC595.parallel = 13  # ST_CP
        the74HC595.serial = 15  # SH_CP
        the74HC595.first = 16 # 74HC595 is not long enough for all LED bars
        the74HC595.last = 18
        self._setupboard()
        self.clear()

    def _setupboard(self):
        gpio.setup(the74HC595.data, gpio.OUT)
        gpio.output(the74HC595.data, gpio.LOW)
        gpio.setup(the74HC595.parallel, gpio.OUT)
        gpio.output(the74HC595.parallel, gpio.LOW)
        gpio.setup(the74HC595.serial, gpio.OUT)
        gpio.output(the74HC595.serial, gpio.LOW)
        gpio.setup(the74HC595.first, gpio.OUT)
        gpio.output(the74HC595.first, gpio.LOW)
        gpio.setup(the74HC595.last, gpio.OUT)
        gpio.output(the74HC595.last, gpio.LOW)

    def _output(self):  # ST_CP
        gpio.output(the74HC595.parallel, gpio.HIGH)
        gpio.output(the74HC595.parallel, gpio.LOW)

    def _tick(self):  # SH_CP
        gpio.output(the74HC595.serial, gpio.HIGH)
        gpio.output(the74HC595.serial, gpio.LOW)

    def clear(self):  # SH_CP
        """
        Sets the 74HC595 back to all off
        Sets both specified GPIOs off

        Returns: None

        """
        self.setvalue([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def setvalue(self, value):
        """
        Sets the 74HC595 to values specified in the list, either 1 (on) or 0 (off)
        Sets 2 the two GPIOs before and after 74HC595 to on or off

        args: [0, 1, 0,...] (10 values)

        Returns: None

        """
        for n in value[1:-1]:
            if n == 0:
                gpio.output(the74HC595.data, gpio.LOW)
            else:
                gpio.output(the74HC595.data, gpio.HIGH)
            the74HC595._tick(self)
        self._output()
        if value[0] == 1:
            gpio.output(the74HC595.first, gpio.HIGH)
        else:
            gpio.output(the74HC595.first, gpio.LOW)
        if value[-1] == 1:
            gpio.output(the74HC595.last, gpio.HIGH)
        else:
            gpio.output(the74HC595.last, gpio.LOW)
