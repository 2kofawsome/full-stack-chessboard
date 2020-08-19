
<p>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python version" height="17"></a>
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Codestyle Black" height="17">
    </a>
</p>

# full-stack-chessboard

### Next Tasks:

- Pre-RFID ask for "w" or "b" turn

<hr>

- Wait for more packages to arrive in the mail!

- Choose side you play as

- Detect Piece movements

- RFID error testing

- Pieces to middle to resign/draw

<br>

## Description

If you do not turn the chess pieces on the lathe and solder the reed switches yourself, 
how can you ever claim full stack for just setting up frontend and backend.

<br>

## This Project Includes: 

> A Wood Working component with turning the pieces and building the board

> An Electrical Engineering component of wiring and soldering it together

> A Software component with coding the logic of the board on a Raspberry Pi Zero

While I had more experience in some (Software) than others (Wood Working), 
each took a tremendous amount of time to accomplish the parts necessary for this project.

Now that's full stack

<br>

### Components

- [Mastercraft 25W Soldering Iron](https://www.canadiantire.ca/en/pdp/mastercraft-25w-soldering-iron-0586305p.html)
- [Raspberry Pi Zero W](https://www.canakit.com/raspberry-pi-zero-wireless.html)
	- 16 GB MicroSD Card
	- 2.5A Power Supply
- [2x20-pin Male Header](https://www.amazon.ca/gp/product/B0756KM7CY/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1)
- [Freenove RFID Starter Kit](https://www.amazon.ca/gp/product/B06VTH7L28/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1)
	- 74HC595
	- LED Bar
	- LCD1602 Display
	- RC522 RFID module
	- 1N4001 Diode
	
- 34 x [20mm 13.56MHZ RFID Tags](https://www.aliexpress.com/item/32898752493.html)
- 3 x [Switches](https://www.aliexpress.com/item/32990004998.html)
- 2 x [Buttons](https://www.aliexpress.com/item/2024643496.html)
- 4 x [MCP23017](https://www.aliexpress.com/item/32909314135.html)
- 34 x Neodymium Magnets
- Various PCB Prototype Board
- 10 x ___ ohms Resistors
- 64 x 1K ohms Resistors
- Soldering Wires (Red, Black, White)
- 64 x Reed Switches


<br>

### Circuitry

First created and tested on breadboards, final soldering was done in this layout:

Include layout here

<br>

### Piece and Board creation

Creating pieces and board explanation will go here

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

<details>
 <summary><a href="https://stockfishchess.org/download/"> Stockfish Download </a></summary>
 
```

Compiled by running "sudo make -j4 profile-build ARCH=armv7 LDFLAGS="-latomic -lpthread -lgcov" on the source code
```
</details>

<br>

### Credits

- [Sam Gunter](https://github.com/2kofawsome)