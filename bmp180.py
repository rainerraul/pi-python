#!/usr/bin/python3

import quick2wire.i2c as twowire
import sys, math, os, time
from ctypes import *

    
deviceAddr = 0x77
adcword = 0
Cal = [0,0,0,0,0,0,0,0,0,0,0,0]
AC1 = [0xaa, 0xab]; AC2 = [0xac, 0xad]; AC3 = [0xae, 0xaf]; AC4 = [0xb0, 0xb1]; AC5 = [0xb2, 0xb3]; AC6 = [0xb4, 0xb5]
B1 = [0xb6, 0xb7]; B2 = [0xb8, 0xb9]; MB = [0xba, 0xbb]; MC = [0xbc, 0xbd]; MD = [0xbe, 0xbf]

nAC1 = [0, 0]; nAC2 = [0, 0]; nAC3 = [0, 0]; nAC4 = [0, 0]; nAC5 = [0, 0]; nAC6 = [0, 0]
nB1 = [0, 0]; nB2 = [0, 0]; nMB = [0, 0]; nMC = [0, 0]; nMD = [0, 0]


cmd_chipId = 0xD0; cmd_softrst = 0xE0; cmd_meas = 0xF4; cmd_adcx = 0xF8; cmd_adcl = 0xF7; cmd_adch = 0xF6

conversion_temp = 0x2e; conversion_4m5 = [0x2e, 0.0047]; conversion_7m5 = [0x74, 0.0075]; conversion_13m5 = [0xb4, 0.0135]
conversion_25m5 = [0xf4, 0.0255] 

reset = 0xb6

with twowire.I2CMaster() as bussystem :
	
	def bmp180_read(register) :
		readvalue = bussystem.transaction(twowire.writing_bytes(deviceAddr, register), twowire.reading(deviceAddr, 1))
		time.sleep(0.02)
		return readvalue[0][0]

	def bmp180_read_more(register, length) :
		readvalue = bussystem.transaction(twowire.writing_bytes(deviceAddr, register), twowire.reading(deviceAddr, length))
		return readvalue
	
	def bmp180_write(register, value) :
		tmpvalue = bmp180_read(register)
		bussystem.transaction(twowire.writing_bytes(deviceAddr, register, value))
		value = bmp180_read(register)
		
		if (value == tmpvalue) :
	 		return 0
		else :
			return 1
	
	def bmp180_writeParams_toFile() :
		bmp180_write(cmd_softrst, reset)
		time.sleep(0.047)
		
		for n in range(0, 2) :
			nAC1[n] = bmp180_read(AC1[n])
			nB1[n] = bmp180_read(B1[n])
			nAC2[n] = bmp180_read(AC2[n])
			nB2[n] = bmp180_read(B2[n])
			nAC3[n] = bmp180_read(AC3[n])
			nMB[n] = bmp180_read(MB[n])
			nAC4[n] = bmp180_read(AC4[n])
			nMC[n] = bmp180_read(MC[n])
			nAC5[n] = bmp180_read(AC5[n])
			nMD[n] = bmp180_read(MD[n])
			nAC6[n] = bmp180_read(AC6[n])
		
		Cal[0] = (nAC1[0] << 8) + nAC1[1]; Cal[6] = (nB1[0] << 8) + nB1[1] 
		Cal[1] = (nAC2[0] << 8) + nAC2[1]; Cal[7] = (nB2[0] << 8) + nB2[1]
		Cal[2] = (nAC3[0] << 8) + nAC3[1]; Cal[8] = (nMB[0] << 8) + nMB[1]
		Cal[3] = (nAC4[0] << 8) + nAC4[1]; Cal[9] = (nMC[0] << 8) + nMC[1]
		Cal[4] = (nAC5[0] << 8) + nAC5[1]; 
		Cal[5] = (nAC6[0] << 8) + nAC6[1]; Cal[10] = (nMD[0] << 8) + nMD[1]
		
		calfile = open("bmp180Cal.dat", "w")
		
		for i in range(0, 11) :
			if(((Cal[i] & 0x8000) == 0x8000)) :
				Cal[i] = 65535 - Cal[i]
				Cal[i] = Cal[i] * (- 1)

			calfile.write("%i" % Cal[i])
			calfile.write("\r\n")	
	
		calfile.close()


	def bmp180_readParams_fromFile() :
		
		s = 0
		calfile = open("bmp180Cal.dat", "r")
			
		for line in calfile.readlines() :
			Cal[s] = int(line)
			s += 1	
					
		calfile.close()
		return Cal


	def bmp180_readTemp() :

		bmp180_write(cmd_softrst, reset)
		time.sleep(0.047)

		bmp180_write(cmd_meas, conversion_temp) 
		time.sleep(0.0045)		
		adcword = bmp180_read(cmd_adch) << 8						
		adcword |= bmp180_read(cmd_adcl)
		caldata = bmp180_readParams_fromFile()

		X1 = (((adcword - caldata[5]) * caldata[4]) / (2 ** 15))
		X2 = ((caldata[9] * (2 ** 11)) / (X1 + caldata[10]))
		B5 = X1 + X2
		adctemp = (B5 + 8) / 16			
		temp = [int(adctemp) / 10, adcword]
		return temp

	def bmp180_readPressure(conversionTime)  :
		bmp180_write(cmd_softrst, reset)
		time.sleep(0.047)

		oss = (conversionTime[0] >> 6) & 0x03		
		bmp180_write(cmd_meas, conversionTime[0])
		time.sleep(conversionTime[1])
		adchbyte = bmp180_read(cmd_adch)			
		adclbyte = bmp180_read(cmd_adcl) 
		adcxbyte = bmp180_read(cmd_adcx)
		adcpressure = ((adchbyte << 16) + (adclbyte << 8) + adcxbyte) >> (8 - oss)
		
		
		temp = bmp180_readTemp()
		caldata = bmp180_readParams_fromFile()
		
		X1 = ((temp[1] - caldata[5]) * caldata[4]) >> 15
		X2 = (caldata[9] << 11) / (X1 + caldata[10])
		B5 = X1 + X2
		
		B6 = B5 - 4000
		X1 = ((int(caldata[7] * (B6 * B6)) >> 12)) >> 11
		X2 = int(caldata[1] * B6)  >> 11
		X3 = X1 + X2

		B3 = (((caldata[0] * 4 + X3) << oss) + 2) / 4
		X1 = int(caldata[2] * B6) >> 13
		X2 = ((caldata[6] * B6 * B6) / (2 ** 12)) / (2 ** 16)
		X3 = ((X1 + X2) + 2) / 4
		B4 = int(caldata[3] * (X3 + 32768)) >> 15
		B7 = (adcpressure - B3) * (50000 >> oss)

		if(B7 < 0x80000000) :
			p = (B7 * 2) / B4
		else :
			p = (B7 / B4) * 2
		
		X1 = int((p / (2 ** 8)) * (p / (2 ** 8)))
		X1 = int((X1 * 3038) / (2 ** 16))
		X2 = int((-7357 * p) / (2 ** 16))
		p = p + int((X1 + X2 + 3791) / (2 ** 4))
		return int(p)

	bmp180_writeParams_toFile()

	press = bmp180_readPressure(conversion_13m5)
	print(press)
	temp = bmp180_readTemp()
	print(temp[0])
