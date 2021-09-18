#!/usr/bin/python3

import smbus
import time

ADDR1 = 0x6E
UREF_BI_10V = 10.24; UREF_BI_2V = 2.048; UREF_10V = 10.24
MODE_CONT_CONV = 0x01; MODE_ONE_SHOT_CONV = 0x00
INPUT_1P_1M = 0x00; INPUT_2P_2M = 0x01; INPUT_3P_3M = 0x02; INPUT4P_4M = 0x03
SAMP_240 = 0x00; SAMP_60 = 0x01; SAMP_15 = 0x02; SAMP_375 = 0x03
GAIN_1 = 0x00; GAIN_2 = 0x01; GAIN_4 = 0x02; GAIN_8 = 0x03
ONE_SHOT = 0x07


aval = 0

i2c = smbus.SMBus(1)

i2c.write_byte(ADDR1, 0x00)

def read_adc(mode, sample, uref, gain, input) :
	
	write_byte = gain | (sample << 2) | (mode << 4) | (input << 5)

	if (mode == MODE_ONE_SHOT_CONV) :
		write_byte |= (1 << ONE_SHOT)
	elif (mode == MODE_CONT_CONV) :
		write_byte |= (0 << ONE_SHOT)

	a = i2c.read_i2c_block_data(ADDR1, write_byte)
	print(a[2])

	if(sample == SAMP_240) :
		aval = (a[0] << 8) | a[1]
		sign = 0x800
		signed = aval & (sign - 1)
	elif(sample == SAMP_60) :
		aval = (a[0] << 8) | a[1]
		sign = 0x2000
		signed = aval & (sign - 1)
	elif(sample == SAMP_15) :
		aval = (a[0] << 8) | a[1]
		sign = 0x8000
		signed = aval & (sign - 1) 
	elif (sample == SAMP_375) :
		aval = (a[0] << 16) | (a[1] << 8) | a[2]
		sign = 0x20000
		signed = aval & (sign - 1)

	if (uref == UREF_BI_10V) or (uref == UREF_BI_2V) : 
		if (aval & sign) :
			signed = ((sign - 1) - signed + 1) * -1 
	
	return (signed / (sign - 1)) * uref * (2 ** gain)



while True :
	print(read_adc(MODE_ONE_SHOT_CONV, SAMP_240, UREF_BI_10V, GAIN_1, INPUT_2P_2M))
	time.sleep(1)
