#!/usr/bin/python

import smbus
import os
import time
import math

twowire = smbus.SMBus(1)

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
H1 = 0; H2 = 1; H3 = 2; H4 = 3; H5 = 4; H6 = 5

ADDR = 0x76 #I2C Address BME280
CALB0 = 0x88 #start address calibration data0 T1-T3 P1-P9 H1
CALB1 = 0xE1 #start address calibration data1 H2-H6
MEASURE = 0xF7 #start address ad-conversion
CONTROL = 0xF4 #config adc temperature and airpressure
CONTROL1 = 0xF2 #config adc humidity
CONTROL2 = 0xF5 #config iir filter to discriminate noise

CONTROL_BYTE = 0x27 #oversampling x 1 forced mode temp and pressure
CONTROL_BYTE1 = 0x01 #oversampling x 1 humidity
CONTROL_BYTE2 = 0x04 #iir filter koefficient 2


def usign_convert_byte(unsigned) :
	signed = unsigned
	if(unsigned & 0x80) :
		signed = ((0xFF - unsigned + 1) * -1)
	return signed

def usign_convert_word(unsigned) :
	signed = unsigned
	if(unsigned & 0x8000) :
		signed = ((0xFFFF - unsigned + 1) * -1)
	return signed

def usign_convert_dword(unsigned) :
	signed = unsigned
	if(unsigned & 0x80000000) :
		signed = ((0xFFFFFFFF - unsigned + 1) * -1)
	return signed

#section read out eeprom calibration data0 and data1 

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

	dig_H[0] = twowire.read_byte_data(ADDR, 0xA1)
	dig_H[1] = param1[0] | (param1[1] << 8)
	dig_H[2] = param1[2]
	dig_H[3] = (param1[4] & 0x0F) | (param1[3] << 4)
	dig_H[4] = (param1[4] >> 4) | (param1[5] << 4)
	dig_H[5] = param1[6]

	return dig_H

#end section

def config_adc() :
	twowire.write_byte_data(ADDR, CONTROL, CONTROL_BYTE)
	twowire.write_byte_data(ADDR, CONTROL1, CONTROL_BYTE1)
	twowire.write_byte_data(ADDR, CONTROL2, CONTROL_BYTE2)

def get_raw_values() :

	raw_data = twowire.read_i2c_block_data(ADDR, MEASURE) #start ad-conversion

	raw_values[ALTI] = ((raw_data[2] >> 4) & 0x0F) | (raw_data[1] << 4) | (raw_data[0] << 12) #raw data airpressure 20bit
	raw_values[TEMP] = ((raw_data[5] >> 4) & 0x0F) | (raw_data[4] << 4) | (raw_data[3] << 12) #raw data temperature 20bit
	raw_values[HUMI] = raw_data[7] | (raw_data[6] << 8) #raw data humidity 16bit

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

def calc_airp(raw_temp, raw_press) : #see down below on function calc_hum()
	dig = calibrationP()
	t_fine = calc_temp(raw_temp)

	for i in range(1, 8) :
		dig[i] = usign_convert_word(dig[i])

	var1 = t_fine[1] - 128000
	var2 = var1 * var1 * dig[P6]
	var2 = var2 + ((var1 * dig[P5]) << 17)
	var2 = var2 + ((dig[P4]) << 35)
	var1 = (( var1 * var1 * dig[P3]) >> 8) + ((var1 * dig[P2]) << 12)
	var1 = (((1 << 47) + var1)) * (dig[P1]) >> 33

	if var1 == 0 :
		return 0

	P = 1048576 - raw_press
	P = (((P << 31) - var2) * 3125) / var1
	var1 = ((dig[9]) * (P >> 13) * (P >> 13)) >> 25
	var2 = ((dig[P8]) * P) >> 19
	P = ((P + var1 + var2) >> 8) + ((dig[P7]) << 4)
	return P / 25600

def calc_hum(raw_temp, raw_hum) : #compensation formulas to calibrate humidity sensor depending of temperature
	dig = calibrationH()
	t_fine = calc_temp(raw_temp)

	dig[H2] = usign_convert_word(dig[H2])
	dig[H4] = usign_convert_word(dig[H4])
	dig[H5] = usign_convert_word(dig[H5])
	dig[H6] = usign_convert_byte(dig[H6])

	vxl = t_fine[1] - 76800
	vxl = (((((raw_hum << 14) - ((dig[H4] << 20) - ((dig[H5]) * vxl)) + (16384)) >> 15) * (((((((vxl * dig[H6])) >> 10) *
	(((vxl * (dig[H3])) >> 11) + (32768))) >> 10) + (2097152)) * (dig[H2]) + 8192) >> 14))
	vxl = (vxl - (((((vxl >> 15) * (vxl >> 15)) >> 7) * (dig[H1])) >> 4))
	if vxl < 0 : vxl = 0
	if vxl > 419430400 : vxl = 419430400
	return (vxl >> 12) / 1000.0

def read_weather_data() :
	read_data = [0.00,0.00,0]

	raw_data = get_raw_values()
	read_data[TEMP] = calc_temp(raw_data[TEMP])[0]
	read_data[ALTI] = calc_airp(raw_data[TEMP], raw_data[ALTI])
	read_data[HUMI] = calc_hum(raw_data[TEMP], raw_data[HUMI])
	return read_data

file = "/var/www/html/wetter/bme280.dat"
  
timestamp = time.asctime(time.localtime(time.time()))
  
filehandle = open(file, "a")
  
config_adc() #first of all start this function for proper adc work
test = read_weather_data()

filehandle.write("time+%s+temp+%3.1f+pressure+%5i+humidity+%3i\r\n" %(timestamp, test[TEMP], test[ALTI], test[HUMI]))
filehandle.close()
#	print(str(test[TEMP]) + " " + str(test[ALTI]) + " " + str(test[HUMI]))
time.sleep(1)
