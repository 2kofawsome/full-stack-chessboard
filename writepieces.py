import RPi.GPIO as gpio
from mfrc522 import SimpleMFRC522
import time

gpio.setwarnings(False)
reader = SimpleMFRC522()


pieces = {"P":"White pawns: ", "p":"Black pawns: ",
		  "R":"White rooks: ", "r":"Black rooks: ",
		  "B":"White bishops: ", "b":"Black bishops: ",
		  "N":"White knights: ", "n":"Black knights: ",
		  "Q":"White queens: ", "q":"Black queens: ",
		  "K":"White king: ", "k":"Black king: "}

def writeall():
	print("Click Enter to scan another identical piece\n"
		  "Type anything before clicking Enter to move onto the next piece\n")
	for n in pieces.keys():
		print("Scan your " + str(pieces[n]))
		while True:
			reader.write(n+"\n\n\nProject on github @ full-stack-chessboard")
			print("next?", end = "")
			if input() != "":
				break

def writecustom():
	reader.write(input("""Type in your piece string:
	
	P, R, B, N, Q, K
	
	White are capital (P, K, Q)
	Black are lowercase (p, k, q)
	
""")[0]+"\n\n\nProject on github @ full-stack-chessboard")
	print("Done\n")

def readall():
	print("Click Ctrl-C at any time to end\n")
	try:
		while True:
			id, text = reader.read()
			print("id: ", id,
				"\ntext: ", text + "\n")
			time.sleep(1)
	except KeyboardInterrupt:
		pass

def main():
	while True:
		print("""This program is used to write to the RFID tags in the pieces
		
	Type 1 for writing all pieces
	Type 2 for writing a custom string
	Type 3 for reading tags
	Type 4 to end program
	""")

		choice = input()
		if choice == "1":
			writeall()
		elif choice == "2":
			writecustom()
		elif choice == "3":
			readall()
		elif choice == "4":
			break
		else:
			pass


main()

gpio.cleanup()