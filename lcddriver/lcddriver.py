# Credit for this code goes to "natbett" of the Raspberry Pi Forum 18/02/13

# Editied by Sam Gunter for full-stack-chess program

from lcddriver import i2c_lib
from time import *
from multiprocessing import Process, Manager
import ctypes
import sys

# LCD Address
# Usually you will have to use one of the two provided values below.
# If you prefer, you can check your LCD address with the command: "sudo i2cdetect -y 1"
# This is a common LCD address.
ADDRESS = 0x27
# This is another common LCD address.
# ADDRESS = 0x3f

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit


class lcd:
    # initializes objects and lcd
    def __init__(self):
        self.lcd_device = i2c_lib.i2c_device(ADDRESS)

        self.manager = Manager()
        self.lines = self.manager.Namespace()
        self.lines.one = "Full-Stack-Chessboard"
        self.lines.two = "By Sam Gunter   "

        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)

        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(0.2)

        p1 = Process(target=self.loop)
        p1.start()

    # clocks EN to latch command
    def lcd_strobe(self, data):
        self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
        sleep(0.0005)
        self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
        sleep(0.0001)

    def lcd_write_four_bits(self, data):
        self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
        self.lcd_strobe(data)

    # write a command to lcd
    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

    # put string function
    def display_string(self, string, line):
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
        if line == 3:
            self.lcd_write(0x94)
        if line == 4:
            self.lcd_write(0xD4)

        for char in string:
            self.lcd_write(ord(char), Rs)

    # clear lcd and set to home
    def clear(self):
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)

    def loop(self):
        """
      Process that runs simultaneously to main program to keep the LCD monitor constantly updating

      args: None
      Returns: None

      """
        try:
            while True:

                line1 = self.lines.one
                line2 = self.lines.two

                while line1 == self.lines.one and line2 == self.lines.two:
                    self.display_string(line1, 1)
                    self.display_string(line2, 2)
                    if line1 == "Calculating.    ": #special case
                        sleep(0.2)
                        self.display_string("Calculating..", 1)
                        sleep(0.2)
                        self.display_string("Calculating...", 1)
                        sleep(0.2)

                    else:
                        for n in range(4):
                            sleep(0.25)
                            if line1 != self.lines.one or line2 != self.lines.two:
                                break
                        if line1 != self.lines.one or line2 != self.lines.two:
                            break

                        if len(line1) > len(line2):
                            for n in range(len(line1) - 16):
                                sleep(0.15)
                                self.display_string(line1[n + 1 :], 1)
                                if len(line1) - len(line2) < len(line1) - 16 - n:
                                    self.display_string(line2[n + 1 :], 2)
                        else:
                            for n in range(len(line2) - 16):
                                sleep(0.15)
                                if len(line2) - len(line1) < len(line2) - 16 - n:
                                    self.display_string(line1[n + 1 :], 1)
                                self.display_string(line2[n + 1 :], 2)

                        for n in range(4):
                            sleep(0.25)
                            if line1 != self.lines.one or line2 != self.lines.two:
                                break
                        else:
                            continue
                        break
        except KeyboardInterrupt:
            self.clear()

    def update(self, string, line):
        """
      Updates string for LCD display loop

      args: string, line (int)
      Returns: None

      """
        if len(string) < 16:
            string = string + " " * (16 - len(string))

        if line == 1:
            self.lines.one = string
        elif line == 2:
            self.lines.two = string
