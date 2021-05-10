
<p>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python version" height="17"></a>
	<a href="https://github.com/2kofawsome/pi74HC595/blob/master/LICENSE"><img src="https://img.shields.io/github/license/2kofawsome/pi74HC595" alt="License" height="18"></a>
</p>

# full-stack-chessboard

## Description

A chessboard with built in piece detection and Stockfish engine. 
From turning the pieces on a lathe, to soldering the components, to coding the Raspberry Pi. 
This is true full stack development.

<br>

## This Project Includes: 

> A Wood Working component with turning the pieces and building the board

> An Electrical Engineering component of wiring and soldering it together

> A Software component with coding the logic of the board on a Raspberry Pi Zero

While I had more experience in some (Software) than others (Wood Working), 
each took a tremendous amount of time to accomplish the parts necessary for this project.

Now that's full stack

<br>

### Circuitry

First created and tested on breadboards, final soldering was done in this layout (created using KiCAD):
![BW Schematics](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/1-1.jpg)  | ![Colour Schematics](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/1-2.jpg) 
With the boards (pre-soldering):
![MCP23017s](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/2-1.jpg)  | ![Pi Extender](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/2-2.jpg)  | ![LEDbar - Front](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/2-3.jpg)  |![LEDbar - Back](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/2-4.jpg)  
In the general layout (pre-soldering, pre-wires):
![Pieces and Layout](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/3-1.jpg)  | ![Layout](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/3-2.jpg) 
And the layout of the reed switches was (pre-soldering):
![Lid w/o Top](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/4-1.jpg)  | ![Lid w/ Top](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/4-2.jpg) 

<br>

### Piece and Board creation

Thank you to Paul (Grandpa) for buiding the board for me:
![Board - Back](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/5-1.jpg)  | ![Board - Shelf](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/5-2.jpg) 
And for building the pieces with me (first time on a lathe!):
![Board - Overhead](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/6-1.jpg)  | ![Board - Front](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/6-2.jpg) 
Pieces contain magnets for reed switches (top) and RFID chips for scanning (bottom):
![Piece - Front](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/7-1.jpg)  | ![Piece Magnet RFID](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/7-2.jpg)  | ![Piece - Bottom](https://raw.githubusercontent.com/2kofawsome/full-stack-chessboard/master/READMEimages/7-3.jpg) 


<br>

### Python Modules

Take a look at the code for full details, but here is a brief overview of the modules I used/created for the project.

``` Python
import string, time, os, datetime, sys, re
import RPi.GPIO as GPIO
```

I contributed to make this work in my project: [Github](https://github.com/zhelyabuzhsky/stockfish)
``` Python
from stockfish import Stockfish
```

I built this to run the 74HC595 [Github](https://github.com/2kofawsome/pi74HC595) [PyPI](https://pypi.org/project/pi74HC595/)
``` Python
import pi74HC595
```

Editied from: [Github](https://github.com/the-raspberry-pi-guy/lcd) to run the LCD1602 display
With accompanying [Video](https://www.youtube.com/watch?v=3XLjVChVgec)
``` Python
import lcddriver
```

Used to run the MFRC522 RFID reader: [Github](https://github.com/pimylifeup/MFRC522-python)
``` Python
from mfrc522 import SimpleMFRC522
```

Used to run the MCP23017s: [Github](https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx)
``` Python
import board, busio
from adafruit_mcp230xx.mcp23017 import MCP23017
```

<br>

## Engine

The engine ended up being a fair bit of effort to get working since the Python module 
[Stockfish](https://github.com/zhelyabuzhsky/stockfish) needed some changes to make it work how I wanted.

And the engine itself here: <a href="https://stockfishchess.org/download/"> Stockfish Download </a>
 
```
Compiled by running "sudo make -j4 profile-build ARCH=armv7 LDFLAGS="-latomic -lpthread -lgcov" on the source code
```
</details>

<br>


### Components

- [Mastercraft 25W Soldering Iron](https://www.canadiantire.ca/en/pdp/mastercraft-25w-soldering-iron-0586305p.html)
- [Raspberry Pi Zero W](https://www.canakit.com/raspberry-pi-zero-wireless.html)
	- 16 GB MicroSD Card
	- 2.5A Power Supply
- [2x20-pin Male Header](https://www.amazon.ca/gp/product/B0756KM7CY/)
- [Freenove RFID Starter Kit](https://www.amazon.ca/gp/product/B06VTH7L28/)
	- 74HC595
	- LED Bar
	- LCD1602 Display
	- RC522 RFID module
	- 1N4001 Diode
	- 28 Male-to-Female Wires
- 32 x [20mm 13.56MHZ RFID Tags](https://www.aliexpress.com/item/32898752493.html)
- 3 x [Switches](https://www.aliexpress.com/item/32990004998.html)
- 2 x [Buttons](https://www.aliexpress.com/item/2024643496.html)
- 4 x [MCP23017](https://www.aliexpress.com/item/32909314135.html)
- 32 x Neodymium Magnets
- Various PCB Prototype Boards
- 10 x 220 ohms Resistors
- 4 x 1K ohms Resistors
- 68 x 10K ohms Resistors
- [22 Gauge Multicolour Wires](https://www.amazon.ca/gp/product/B0791BNDY2/)
- 64 x Reed Switches

<br>

## Credits

- [Sam Gunter](https://github.com/2kofawsome)

## License
MIT License. Please see [License File](LICENSE) for more information.
