#!/usr/bin/python3

import quick2wire.i2c as twi
import sys, math, os, time 
from ctypes import *

ADDR = 0x48

CONV_REG = 0x00
CONF_REG = 0x01
CONF_OS = 0x8000
CONF_PGA = [0x200, 0x400, 0x800]
CONF_MUX = [0x1000, 0x2000, 0x4000]

MASK_PGA = 0x0E

V6144 = 0 ; V4096 = 1 ; V2048 = 2 ; V1024 = 3
P0N1 = 0 ; P0N3 = 1 ; P1N3 = 2 ; P2N3 = 3 ; P0G0 = 4 ; P1G0 = 5 ; P2G0 = 6 ; P3G0 = 7

with twi.I2CMaster() as bus :
	
	def readCONF() :
		bus.transaction(twi.writing_bytes(ADDR, CONF_REG))
		readreg = bus.transaction(twi.reading(ADDR, 2))
		return readreg


	def writeCONF(writebyte, set) :
		
		tmpreg = readCONF()
		tmpregh = tmpreg[0][0]
		tmpregl = tmpreg[0][1]
		
		tmpregw = tmpregh << 8
		tmpregw = tmpregw | tmpregl

		if (set == 1) :
			tmpregw = tmpregw |  writebyte
		
		elif (set == 0) :
			tmpregw = tmpregw  & (~writebyte)
		
		
		tmpregh = (tmpregw >> 8)
		tmpregl = (tmpregw & 0xFF)

		bus.transaction(twi.writing_bytes(ADDR, CONF_REG, tmpregh, tmpregl))
		
		tmpreg = readCONF()
		
		return ((tmpreg[0][0] << 8) + tmpreg[0][1]) & writebyte
	
	def readCONV() :
		writeCONF(CONF_OS, 1)
		
		bus.transaction(twi.writing_bytes(ADDR, CONV_REG))
		readresult = bus.transaction(twi.reading(ADDR, 2))
		return readresult


	def readVolt() :
		
		refbits = readCONF()
		tmprefbits = (refbits[0][0] & MASK_PGA) >> 1

		if(tmprefbits == 0) :
			uref = 6.144
		elif(tmprefbits == 1) :
			uref = 4.096
		elif(tmprefbits == 2) :
			uref = 2.048
		elif(tmprefbits == 3) :
			uref = 1.024
		 

		readAD = readCONV()
		ureadAD = (readAD[0][0] << 8) + (readAD[0][1] & 0xFF)
		
		if(ureadAD & 0x8000) :
			sreadAD =  (65535 - ureadAD) *  -1
		else :
			sreadAD = ureadAD

		return (sreadAD / 32767) * uref


	def setREF(uref) :
		if(uref == V6144) :
			writeCONF(CONF_PGA[0], 0)
			writeCONF(CONF_PGA[1], 0)
			writeCONF(CONF_PGA[2], 0)
		elif(uref == V4096) :
			writeCONF(CONF_PGA[0], 1)
			writeCONF(CONF_PGA[1], 0)
			writeCONF(CONF_PGA[2], 0)
		elif(uref == V2048) :
			writeCONF(CONF_PGA[0], 0)
			writeCONF(CONF_PGA[1], 1)
			writeCONF(CONF_PGA[2], 0)
		elif(uref == V1024) :
			writeCONF(CONF_PGA[0], 1)
			writeCONF(CONF_PGA[1], 1)
			writeCONF(CONF_PGA[2], 0)
			
	def setINP(inpmode) :
		if(inpmode == P0N1) :
			writeCONF(CONF_MUX[0], 0)
			writeCONF(CONF_MUX[1], 0)
			writeCONF(CONF_MUX[2], 0)
		elif(inpmode == P0N3) :
			writeCONF(CONF_MUX[0], 1)
			writeCONF(CONF_MUX[1], 0)
			writeCONF(CONF_MUX[2], 0)
		elif(inpmode == P1N3) :
			writeCONF(CONF_MUX[0], 0)
			writeCONF(CONF_MUX[1], 1)
			writeCONF(CONF_MUX[2], 0)
		elif(inpmode == P2N3) :
			writeCONF(CONF_MUX[0], 1)
			writeCONF(CONF_MUX[1], 1)
			writeCONF(CONF_MUX[2], 0)
		elif(inpmode == P0G0) :
			writeCONF(CONF_MUX[0], 0)
			writeCONF(CONF_MUX[1], 0)
			writeCONF(CONF_MUX[2], 1)
		elif(inpmode == P1G0) :
			writeCONF(CONF_MUX[0], 1)
			writeCONF(CONF_MUX[1], 0)
			writeCONF(CONF_MUX[2], 1)
		elif(inpmode == P2G0) :
			writeCONF(CONF_MUX[0], 0)
			writeCONF(CONF_MUX[1], 1)
			writeCONF(CONF_MUX[2], 1)
		elif(inpmode == P2G0) :
			writeCONF(CONF_MUX[0], 1)
			writeCONF(CONF_MUX[1], 1)
			writeCONF(CONF_MUX[2], 1)
	setREF(V6144)	
	setINP(P0N1)	
	

	while True :	
		print(readVolt())   
		time.sleep(1)	
 