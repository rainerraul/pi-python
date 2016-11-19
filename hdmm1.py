#!/usr/bin/python3

import time
import quick2wire.i2c as i2c
import string
import math

Xval = 0.0
Yval = 0.0
X = 0.0
Y = 0.0
degree = 0.0

with i2c.I2CMaster() as bus:
	bus.transaction(i2c.writing_bytes(0x30, 0x00, 0x04)) #starte reset
	bus.transaction(i2c.writing_bytes(0x30, 0x00, 0x02)) #starte set
	bus.transaction(i2c.writing_bytes(0x30, 0x00, 0x01)) #starte auslesen	
	time.sleep(0.005)


	while True:
		bus.transaction(i2c.writing_bytes(0x30, 0x00, 0x01)) #starte zum Auslesen
		time.sleep(0.005)

		tmp = bus.transaction(i2c.writing_bytes(0x30, 0x00))	
		regvalue = bus.transaction(i2c.reading(0x30, 5)) #lese 5 bytes aus x und y-register
				
		Xval = ((regvalue[0][1]) << 8) + regvalue[0][2] #hi und low byte zusammenfuehren X-Wert
		Yval = ((regvalue[0][3]) << 8) + regvalue[0][4] #""         ""       ""         Y-Wert  
		X = Xval - 2048
		Y = Yval - 2048

		degree = math.atan2(Y, X) * 180 / math.pi   		
		if degree < 0: 
			degree += 360.0

		print ("-------------------")

		print("Kompass-Winkel: " + str(degree))

		time.sleep(1)	
