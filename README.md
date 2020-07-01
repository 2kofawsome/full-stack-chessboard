
<p>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python version" height="17"></a>
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Codestyle Black" height="17">
    </a>
</p>

# full-stack-chessboard

### Next Tasks:

- LED changes direction depending on who starts

- Draw on repetition/50 move?

<hr>

- Wait for more packages to arrive in the mail!

- Choose side you play as
 
- Reed Switch layout

- RFID stuff

- Pieces to middle to resign/draw

- Turn on on startup

- Turn off on power down

<br>

### Glitch Log

- updatepgn was not running every move? (No errors?)

- A move did not register properly?

``` Python

Traceback (most recent call last):
  File "chessscript.py", line 987, in <module>
    startup()
  File "chessscript.py", line 968, in startup
    newgame()
  File "chessscript.py", line 924, in newgame
    main()
  File "chessscript.py", line 706, in main
    last = grid[int(move[0][1]) - 1][alphabet.index(move[0][0])]
ValueError: invalid literal for int() with base 10: 'a')```

-

## Description

A true full stack developer not only runs the database and the website, but builds every part of their project. 

If you do not turn the chess pieces on the lathe and solder the reed switches yourself, how can you ever claim full stack for just running the Raspberry Pi.

<br>

## This Project Includes: 

> An Electrical Engineering component of wiring it all up

> A Wood Working component with turning the pieces and building the board

> A Software component with coding the brains on a Raspberry Pi Zero

> A back end component with the database of past games and running the website server on another Raspberry Pi (3B+)

> Front end componenet of building the website visuals

Now that's full stack

<br>

### Components

- [Raspberry Pi Zero W](https://www.canakit.com/raspberry-pi-zero-wireless.html)
	- 16 GB MicroSD Card
	- 2.5A Power Supply
- [2x20-pin Male Header](https://www.amazon.ca/gp/product/B0756KM7CY/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1)
- [Freenove RFID Starter Kit](https://www.amazon.ca/gp/product/B06VTH7L28/ref=ppx_yo_dt_b_asin_title_o04_s00?ie=UTF8&psc=1)
	- 74HC595
	- LED Bar
	- LCD1602 Display
	- RC522 RFID module
- [Mastercraft 25W Soldering Iron](https://www.canadiantire.ca/en/pdp/mastercraft-25w-soldering-iron-0586305p.html)
- [PCB Prototype Board](https://www.aliexpress.com/item/32588853051.html)
- [Resisitors](https://www.aliexpress.com/item/32785425406.html)
- [13.56MHZ RFID Tags](https://www.aliexpress.com/item/32898752493.html)
- [Soldering Cable](https://www.aliexpress.com/item/32822880152.html)
- [Switches](https://www.aliexpress.com/item/32990004998.html)
- [Buttons](https://www.aliexpress.com/item/2024643496.html)
- [MCP23017](https://www.aliexpress.com/item/32909314135.html)
- [TCA9548A](https://www.aliexpress.com/item/32648420655.html)
- Neodymium Magnets
- [Reed Switches](https://www.aliexpress.com/item/32801522211.html)


<br>

### Circuitry

Will go here

<br>

### Piece and Board creation

Will go here

<br>

### Software

``` Python
import string, time, os, datetime, sys
import RPi.GPIO as GPIO
```

Contributed: [Github](https://github.com/zhelyabuzhsky/stockfish)
``` Python
from stockfish import Stockfish
```

I built this
``` Python
import driver74HC595
```

Editied from: [Github](https://github.com/the-raspberry-pi-guy/lcd)
With accompanying [Video](https://www.youtube.com/watch?v=3XLjVChVgec)
``` Python
import lcddriver
```

Thank you to: [Github](https://github.com/pimylifeup/MFRC522-python)
``` Python
from mfrc522 import SimpleMFRC522
```

<br>

## Engine

<details>
 <summary><a href="https://stockfishchess.org/download/"> Stockfish Download </a></summary>
 
```
Compiled by running "sudo make -j4 profile-build ARCH=armv7 LDFLAGS="-latomic -lpthread -lgcov" on the source code
```
</details>

<br>

### Credits

- [Sam Gunter](https://github.com/2kofawsome)