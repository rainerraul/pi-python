#! /usr/bin/python3


import quick2wire.i2c as ibus
import os, time, math, string


HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[10m'
UNDERLINE = '\033[4m'


device = 0x40
polynom = 0x131
rd = 0; wr = 1
io = [0x00, 0x00]
hygro0 = 0; hygro1 = 1; temp0 = 2; temp1 = 3; temp2 = 4
toggle_heater = 0x00
heat_on = 1; heat_off = 0
heater_current = [3, 9, 15, 21, 27, 33, 39, 45, 51, 57, 63, 69, 75, 81, 86, 94] 
res0 = 0; res1= 1; res2 = 2; res3 = 3

with ibus.I2CMaster() as bussystem :

	def si7020_read1(register, length) :
		readdata = bussystem.transaction(ibus.writing_bytes(device, register), ibus.reading(device, length))
		return readdata		
	
	def si7020_read_after_Clockstretch(register, length) :
		bussystem.transaction(ibus.writing_bytes(device, register))
		time.sleep(0.025)
		readdata = bussystem.transaction(ibus.reading(device, length))
		return readdata

	def si7020_read2(reg1, reg2, length) :
		readdata = bussystem.transaction(ibus.writing_bytes(device, reg1, reg2), ibus.reading(device, length))
		return readdata

	def si7020_write(register, value) :
			bussystem.transaction(ibus.writing_bytes(device, register, value))
			
	def si7020_regcompare_write2(io_register, bitset, operation) :
		
		tmp_readdata = si7020_read1(io_register[0], 1)
		tmp = tmp_readdata[0][0]

		if(operation == "xor") :
			tmp ^= bitset
		elif(operation == "normal") :
			tmp = bitset
		elif(operation == "set") :
			tmp |= bitset
		elif(operation == "unset") :
			tmp &= ~(bitset)

		bussystem.transaction(ibus.writing_bytes(device, io_register[1], tmp))
		readdata = si7020_read1(io_register[0], 1)		
		return readdata[0][0]

	def si7020_crc8(chkdata, chksum) :
		for i in range(8) :
			if((chksum & 0x80) != (chkdata & 0x80))  :
				chksum = (chksum  << 1) ^ polynom

			else :	
				chksum <<= 1

			chkdata <<= 1
		return chksum & 0xff


	def si7020_read_Id() :
		id = [0x00, 0x00]
		ok = 0x00	

		readit = si7020_read2(0xfa, 0x0f, 8)
		ok = si7020_crc8(readit[0][0], ok)		
		ok = si7020_crc8(readit[0][2], ok)
		ok = si7020_crc8(readit[0][4], ok)
		ok = si7020_crc8(readit[0][6], ok)

		if(ok != readit[0][7]) :
			return False	

		for n in range(0, 8) :
			id[0] |= readit[0][n] << (n * 8)
		
		ok = 0x00
		readit = si7020_read2(0xfc, 0xc9, 8)
		ok = si7020_crc8(readit[0][0], ok)		
		ok = si7020_crc8(readit[0][1], ok)		
		ok = si7020_crc8(readit[0][3], ok)
		ok = si7020_crc8(readit[0][4], ok)
		
		if(ok != readit[0][5]) :
			return False
		
		for n in range(0, 6) :
			id[1] |= readit[0][n] << (n * 8)
		return id


	def si7020_read_Firmware_version() :
		firm = si7020_read2(0x84, 0xb8, 1)
	
		if(firm[0][0] == 255) :
			return 0x01
		else :
			return 0x02


	def si7020_read_Sensor(mode) :
		length = 3
		sensvalue = 0

		if(mode == 0) : 
			cmdRead = 0xe5
		elif(mode == 1) :
			cmdRead = 0xf5
		elif(mode == 2) :
			cmdRead = 0xe3
		elif(mode == 3) :
			cmdRead = 0xf3
		elif(mode == 4) :
			cmdRead = 0xe0
			length = 2
		else :
			return -1

		rawData = si7020_read_after_Clockstretch(cmdRead, length)

		if(mode != 4) :

			ok = 0x00
			ok = si7020_crc8(rawData[0][0], ok)
			ok = si7020_crc8(rawData[0][1], ok)

			if(rawData[0][2] != ok) :
				return -1

		rawval = (rawData[0][0] << 8) or rawData[0][1]

		if((mode == 0) or (mode == 1)) :
			sensvalue = ((125 * rawval) / 65536) - 6 
		
		elif((mode == 2) or (mode == 3) or (mode == 4)) :
			sensvalue = ((175.72 * rawval) / 65536) - 47.85

		return sensvalue


	def si7020_toggle_heater() :
		io[rd] = 0xe7; io[wr] = 0xe6; control = 0x00
		toggle_heater = 0x04

		control = si7020_regcompare_write2(io, toggle_heater, "xor") 	

		if((control & toggle_heater) == toggle_heater) :
			return 1
		elif((control & toggle_heater) == 0x00) :
			return 0

	def si7020_set_heater_level(currlevel) :
		io[rd] = 0x11; io[wr] = 0x51
		control = si7020_regcompare_write2(io, currlevel, "normal")
		if((control & currlevel) == currlevel) :
			return heater_current[currlevel] 

		return -1

	def si7020_set_precision(mode) :
		io[rd] = 0xe7; io[wr] = 0xe6
		
		if(mode == res0) :
			control = si7020_regcompare_write2(io, 0x80, "unset")
			control = si7020_regcompare_write2(io, 0x01, "unset")

			if((control & 0x80) != 0x00) :
				return -1
			elif((control & 0x01) != 0x00) :
				return -1

		elif(mode == res1) :
			control = si7020_regcompare_write2(io, 0x80, "unset")
			control = si7020_regcompare_write2(io, 0x01, "set")

			if((control & 0x80) != 0x00) :
				return -1
			elif((control & 0x01) == 0x00) :
				return -1

		elif(mode == res2) :
			control = si7020_regcompare_write2(io, 0x80, "set")
			control = si7020_regcompare_write2(io, 0x01, "unset")

			if((control & 0x80) == 0x00) :
				return -1
			elif((control & 0x01) != 0x00) :
				return -1
		elif(mode == res3) :
			control = si7020_regcompare_write2(io, 0x80, "set")
			control = si7020_regcompare_write2(io, 0x01, "set")

			if((control & 0x80) == 0x00) :
				return -1
			elif((control & 0x01) == 0x00) :
				return -1

		return 1

#	print(si7020_set_precision(3))
#	print(si7020_toggle_heater())

	while True :
		print("----------------------------------------------------" + FAIL)
		time.sleep(0.2)

		print("Temperature(Hold Master mode): %8.2f" % si7020_read_Sensor(temp0) + OKGREEN)
		time.sleep(0.2)
		
		print("Temperature(No Hold Master mode): %8.2f" % si7020_read_Sensor(temp1) + OKBLUE)
		time.sleep(0.2)
		
		print("Humidity(Hold Master mode): %8.2f" % si7020_read_Sensor(hygro0) + HEADER)
		time.sleep(0.2)
		
		print("Humidity(No Hold Master mode): %8.2f" % si7020_read_Sensor(hygro1) + WARNING)
		time.sleep(0.2)
		
		print(ENDC + "----------------------------------------------------" + ENDC)

		time.sleep(1)
