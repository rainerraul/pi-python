#!/usr/bin/python3

import quick2wire.i2c as twi
import time
import sys

real = 0
thyst = 1
tos = 2

temp = 0



with twi.I2CMaster() as connector:
	try:
		def readTemp( mode ):
		
			if (mode == 0): 
				m = 0x00
			if (mode == 1): 
				m = 0x02
			if (mode == 2):
				m = 0x03

			connector.transaction(twi.writing_bytes(0x4F, m))
			temp = connector.transaction(twi.reading(0x4F, 2))
			signFlag = (temp[0][0] & 0x80) / 0x80
	
			temperatur = ((temp[0][0] << 1)) + ((temp[0][1] & 0x80) >> 7)
	
			if (signFlag == 1):
				temperatur *= (-1)
		
			temperatur = temperatur / 2.0
			return temperatur

		def writeTemp( tempval, mode ):
			highbyte = 0
			lowbyte = 0
		
			if (mode == 1):
				m = 0x02
			if (mode == 2):
				m = 0x03

			tempval *= 2
			tempval = int(tempval)

			if ( tempval < 0 ):
				highbyte |= 0x80
			if ( tempval >= 0 ):
				highbyte &= 0x80
				
			highbyte |= ((tempval & 0xFE) >> 1)
			lowbyte |= (tempval & 0x01) << 7
 	
			connector.transaction(twi.writing_bytes(0x4F, m, highbyte, lowbyte)) 

		def configLM75 ( konfigbyte ):
			connector.transaction(twi.writing_bytes(0x4F, 0x01, konfigbyte))


		#configLM75(0x00)
		if (sys.argv[0] and sys.argv[1]):
			thystvalue = float(sys.argv[1])
			thosvalue = float(sys.argv[2])
			writeTemp(thystvalue, thyst)
			writeTemp(thosvalue, tos)
     		temp1 = readTemp(thyst);
		temp2 = readTemp(tos)
		temp3 = readTemp(real)
		print("thyst:" + str(temp1) + ":tos:" + str(temp2) + ":ist:" + str(temp3))
		

	except IndexError:
		temp1 = readTemp(thyst)
		temp2 = readTemp(tos)
		temp3 = readTemp(real)	
		print("thyst:" + str(temp1) + ":tos:" + str(temp2) + ":ist:" + str(temp3))
		print("Please put args in following order: lm75Konfig.py Thyst Thos");
		pass
