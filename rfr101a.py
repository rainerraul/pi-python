#!/usr/bin/python3


import serial
import time

serialRFID = serial.Serial("/dev/ttyAMA0", 9600)

while True:
	print (serialRFID.read(12)[1:11])

	serialRFID.flushInput()
	
	time.sleep(0.2)

