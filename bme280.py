import smbus
import os
import time
import math

twowire = smbus.SMBus(4)

cal0 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
cal1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
dig_T = [0,0,0,0,0,0,0,0,0]
dig_P = [0,0,0,0,0,0,0,0,0,0]
dig_H = [0,0,0,0,0,0,0,0,0]

raw_data = [0,0,0,0,0,0,0,0]
raw_values = [0,0,0]

TEMP = 1 ; ALTI = 0 ; HUMI = 2
T1 = 0 ; T2 = 1 ; T3 = 2
P1 = 0; P2 = 1; P3 = 2; P4 = 3; P5 = 4
P6 = 5; P7 = 6; P8 = 7; P9 = 8

ADDR = 0x76
CALB0 = 0x88
CALB1 = 0xE1
MEASURE = 0xF7
CONTROL = 0xF4
CONTROL1 = 0xF2

CONTROL_BYTE = 0x27 #oversampling x 1 forced mode temp and pressure
CONTROL_BYTE1 = 0x01 #oversampling x 1 humidity 

def usign_convert_word(unsigned) :
	signed = unsigned
	if(unsigned & 0x8000) :
		signed = ((0xFFFF - unsigned + 1) * -1)
	return signed

def usign_convert_qword(unsigned) :
	signed = unsigned
	if(unsigned & 0x8000000000000000) :
		signed = ((0xFFFFFFFFFFFFFFFF - unsigned + 1) * -1)
	return signed

def usign_convert_dword(unsigned) :
	signed = unsigned
	if(unsigned & 0x80000000) :
		signed = ((0xFFFFFFFF - unsigned + 1) * -1)
	return signed


def read_cal0() :
	cal0 = twowire.read_i2c_block_data(ADDR, CALB0)
	return cal0


def read_cal1() :
	cal1 = twowire.read_i2c_block_data(ADDR, CALB1)
	return cal1


def calibrationT() :
	param = read_cal0()
	for i in range(0, 3) :
		dig_T[i] = param[0 + (i * 2)] | (param[1 + (i * 2)] << 8)
	return dig_T

def calibrationP() :
	param = read_cal0()
	for i in range(3, 12) :
		dig_P[i - 3] = param[0 + (i * 2)] | (param[1 + (i * 2)] << 8)
	return dig_P


def calibrationH() :
	param0 = read_cal0()
	param1 = read_cal1()

	dig_H[0] = param0[25]
	dig_H[1] = param1[0] | (param1[1] << 8)
	dig_H[2] = param1[2]
	dig_H[3] = ((param1[4] & 0x0F) | (param1[3] << 4)) & 0xFFF

	param1[4] = (param1[4] >> 4) & 0x0F

	dig_H[4] = (param1[4] | (param1[5] << 4)) & 0xFFF
	dig_H[5] = param1[6]

	return dig_H


def get_raw_values() :
	twowire.write_byte_data(ADDR, CONTROL, CONTROL_BYTE)
	twowire.write_byte_data(ADDR, CONTROL1, CONTROL_BYTE1)

	raw_data = twowire.read_i2c_block_data(ADDR, MEASURE)

	raw_values[ALTI] = ((raw_data[2] >> 4) & 0x0F) | (raw_data[1] << 4) | (raw_data[0] << 12)
	raw_values[TEMP] = ((raw_data[5] >> 4) & 0x0F) | (raw_data[4] << 4) | (raw_data[3] << 12)
	raw_values[HUMI] = raw_data[7] | (raw_data[6] << 8)

	return raw_values

def calc_temp(raw_temp) :

	dig = calibrationT()
	raw_temp = usign_convert_dword(raw_temp)
	dig[T2] = usign_convert_word(dig[T2])
	dig[T3] = usign_convert_word(dig[T3])

	var1 = ((((raw_temp >> 3) - (dig[T1] << 1))) * (dig[T2])) >> 11
	var2 = (((((raw_temp >> 4) - (dig[T1])) * ((raw_temp >> 4) - (dig[T1]))) >> 12) * (dig[T3])) >> 14
	t_fine = var1 + var2
	T = (t_fine * 5 + 128) >> 8
	return [T / 100.0, t_fine]

def calc_airp(raw_temp, raw_press) :
	dig = calibrationP()
	t_fine = calc_temp(raw_temp)

	t_fine[1] = usign_convert_qword(t_fine[1])
	raw_press = usign_convert_dword(raw_press)

	for i in range(1, 8) :
		dig[i] = usign_convert_qword(dig[i])

	var1 = t_fine[1] - 128000
	var2 = var1 * var1 * dig[P6]
	var2 = var2 + ((var1 * dig[P5]) << 17)
	var2 = var2 + ((dig[P4]) << 35)
	var1 = (( var1 * var1 * dig[P3]) >> 8) + ((var1 * dig[P2]) << 12)
	var1 = ((((dig[P1]) << 47) + var1)) * (dig[P1]) >> 33

	if var1 == 0 :
		return 0

	P = 1048576 - raw_press

while True :
	test = get_raw_values()
	test[TEMP] = calc_temp(test[TEMP])[0]
	print(test[TEMP])
	time.sleep(1)
