#!/usr/bin/python3

import os
import quick2wire.i2c as i2c
import time

ADDR = 0x44

with i2c.I2CMaster() as bus :
	
	def readSensor() :

		bus.transaction(i2c.writing_bytes(ADDR, 0x22, 0x20))
		time.sleep(0.05)
		readout = bus.transaction(i2c.writing_bytes(ADDR, 0xE0, 0x00), i2c.reading(ADDR, 6))
		time.sleep(1.0)

		return readout


#	while True :
	timestamp = time.asctime(time.localtime(time.time()))
	
	readit = readSensor()
    		
	rawtemp = (readit[0][0] << 8) | readit[0][1]
	temp = -45.0 + 175.0 * (rawtemp / 65535)
		
	rawhum = (readit[0][3] << 8) | readit[0][4]
	hum = 100 * (rawhum / 65535);
		
	filehandle = open("/var/www/wetter/sht31.dat", "a")
	filehandle.write("time+%s+temp+%3.1f+humidity+%5i\r\n" %(timestamp, temp, hum))
	filehandle.close()
	time.sleep(1)

