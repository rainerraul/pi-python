#! /usr/bin/python3

import quick2wire.i2c as twi
import os, math, time

slave = 0x60
interval = 1

#i2c command table
PARTID = 0x00;         UCOEF = [0x13, 0x14, 0x15, 0x16]
REVID  = 0x01;         PARAW = 0x17
SEQID  = 0x02;         COMM  = 0x18
INTCFG = 0x03;         RESP  = 0x20
IRQEN  = 0x04;         IRSTA = 0x21
HWKEY  = 0x07;         VIDAT = [0x22, 0x23]  
MRATE  = [0x08, 0x09]; IRDAT = [0x24, 0x25]
PARAR  = 0x2e;         UVDAT = [0x2c, 0x2d]
CHSTAT = 0x30;         INKEY = [0x3b, 0x3c, 0x3d, 0x3e]

#ram command table
SLADDR = 0x00; IRMISC = 0x1f
CHLIST  = 0x01
ALSENC  = 0x06
IRADMUX = 0x0e
AUXMUX  = 0x0f
VISADCO = 0x10
VISGAIN = 0x11
VISMISC = 0x12
IRADCO  = 0x1d
IRGAIN  = 0x1e

#command register extensions  
QUERY = 0x80; NOP = 0x00; I2CADDR = 0x02; ALSFORCE = 0x06; ALSAUTO = 0x0e 
PSET  = 0xa0; RST = 0x01; GETCAL  = 0x12; ALSPAUSE = 0x0a

#read ram_parameter
RD_SLADDR = (QUERY | SLADDR); RD_VISGAIN = QUERY | VISGAIN
RD_CHLIST  = QUERY | CHLIST;  RD_VISMISC = QUERY | VISMISC
RD_ALSENC  = QUERY | ALSENC;  RD_IRADCO  = QUERY | IRADCO
RD_IRADMUX = QUERY | IRADMUX; RD_IRGAIN  = QUERY | IRGAIN
RD_AUXMUX  = QUERY | AUXMUX;  RD_IRMISC  = QUERY | IRMISC
RD_VISADCO = QUERY | VISADCO

#write ram_parameter
WR_SLADDR = PSET | SLADDR; WR_VISGAIN = PSET | VISGAIN
WR_CHLIST  = PSET | CHLIST;  WR_VISMISC = PSET | VISMISC
WR_ALSENC  = PSET | ALSENC;  WR_IRADCO  = PSET | IRADCO
WR_IRADMUX = PSET | IRADMUX; WR_IRGAIN  = PSET | IRGAIN
WR_AUXMUX  = PSET | AUXMUX;  WR_IRMISC  = PSET | IRMISC
WR_VISADCO = PSET | VISADCO


#some constants
VIS = 0; IR = 1; UV = 2
UCOVAL = [0x7b, 0x6b, 0x01, 0x00]

with twi.I2CMaster(1) as twibus :
#i2c routines
	def i2c_read(reg) :
		readvalue = twibus.transaction(twi.writing_bytes(slave, reg), twi.reading(slave, 1))
		return readvalue[0][0]
	

	def i2c_write(reg, value) :
		twibus.transaction(twi.writing_bytes(slave, reg, value))

	
	def i2c_read_more(reg, length) :
		readvalue = twibus.transaction(twi.writing_bytes(slave, reg), twi.reading(slave, length))
		return readvalue
#ram routines
	def ram_command_write(wr_ram_register, ram_value) :
		state = True
	
		while (state == True) :
			i2c_write(COMM, NOP)
			
			if(ram_value >= 0) :
				i2c_write(PARAW, ram_value)
		
			if(i2c_read(RESP) == 0x00) :	
				i2c_write(COMM, wr_ram_register)
				rsp = i2c_read(RESP)
	
				if(rsp != 0x00) :
					state = False
		return rsp	

	def ram_command_read(rd_ram_register) :
		state = True
		ram_value = 0
		
		while (state == True) :
			i2c_write(COMM, NOP)
	
			if(i2c_read(RESP) == 0x00) :	
				i2c_write(COMM, rd_ram_register)
				rsp = i2c_read(RESP)
		
				if(rsp != 0x00) :
					state = False
	
		if((rd_ram_register & QUERY) == QUERY) :	
			ram_value = i2c_read(PARAR)
			return ram_value
		
		return rsp

#i2c command functions
	def get_part_id() :
		part = i2c_read(PARTID)
		return part
			
	
	def get_revision() :
		rev = i2c_read(REVID)
		return rev
		
	def get_sequenz() :
		seq = i2c_read(SEQID)
		return seq	
		
	def enable_int_output(state) :
		i2c_write(INTCFG, state)
		state = i2c_read(INTCFG)
		return state
		
	def enable_irq(state) :
		i2c_write(IRQEN, state)
		state = i2c_read(IRQEN)
		return state

	def set_int_out_pin(state) :
		i2c_write(INTCFG, state)
		state = i2c_read(INTCFG)
		return state
	
	def set_hardware_key() :
		i2c_write(HWKEY, 0x17)
		if(i2c_read(HWKEY) == 0x17) :
			return True
		return False

	def set_measure_rate(rate) :
		for i in range(2) :
			i2c_write(MRATE[i], (rate >> (8 * i)) & 0xff)
				
		rate = i2c_read_more(MRATE[0], 2)
		return (rate[0][1] << 8) | rate[0][0]

	def read_irq_state() :
		return i2c_read(IRSTA) & 0x21

	def read_sensor_data(senstype) :
		global multi
		global sensword

		multi = 1
		sensword = 0
		
		if(senstype == VIS) :
			comm = VIDAT
			#multi = 14.5 / 0.282
		elif(senstype == IR) :
			comm = IRDAT
			#multi = 14.5 * 0.41
		elif(senstype == UV) :
			comm = UVDAT

		
		sensdata = i2c_read_more(comm[0], 2)
		sensword = (sensdata[0][1] << 8) | sensdata[0][0]		

		if(senstype == UV) :
			sensword /= 100
		elif(senstype == IR) :
			if(sensword > 256) :
				sensword -= 256
				sensword *= 14.5
			else :
				sensword = 0

		elif(senstype == VIS) :
			if(sensword > 256) :
				sensword -= 256
				sensword *= 14.5
			else :
				sensword = 0

		return sensword		

	def chip_state() :
		state = i2c_read(CHSTAT) & 0x07
		return state

#ram command functions

	def reset_ir_adcmux() :
		state = ram_command_write(WR_IRADMUX, 0x00)
		state = ram_command_read(RD_IRADMUX)
		return state
	
	def set_aux_mux() :
		state = ram_command_write(WR_AUXMUX, 0x65)
		state = ram_command_read(RD_AUXMUX)
		return state

	def set_ir_range() :
		state = ram_command_write(WR_IRMISC, 0x20)
		state = ram_command_read(RD_IRMISC)
		return state

	def set_vis_range() :
		state = ram_command_write(WR_VISMISC, 0x20)
		state = ram_command_read(RD_VISMISC)
		return state

	def reset_ir_range() :
		state = ram_command_write(WR_IRMISC, 0x00)
		state = ram_command_read(RD_IRMISC)
		return state

	def reset_vis_range() :
		state = ram_command_write(WR_VISMISC, 0x00)
		state = ram_command_read(RD_VISMISC)
		return state

	def set_als_mode(mode) :
		state = ram_command_write(mode, -1)
		state = ram_command_read(mode)
		return mode

	def enable_als() :
		state = ram_command_write(WR_CHLIST, 0xf0)
		state = ram_command_read(RD_CHLIST)
		return state

	def visible_gain(v) :
		state = ram_command_write(WR_VISGAIN, v)
		state = ram_command_read(RD_VISGAIN)
		return state
		
	def irda_gain(v) :
		state = ram_command_write(WR_IRGAIN, v)
		state = ram_command_read(RD_IRGAIN)
		return state

	def ir_adc_counter(c) :
		state = ram_command_write(WR_IRADCO, c)
		state = ram_command_read(RD_IRADCO)	

	def vis_adc_counter(c) :
		state = ram_command_write(WR_VISADCO, c)
		state = ram_command_read(RD_VISADCO)	
	
	def init_sensor() :	

		for i in range(4) :	
			i2c_write(UCOEF[i], UCOVAL[i])


		set_hardware_key()
		set_measure_rate(0x080a)
	
		enable_als()
		visible_gain(0x00)
		irda_gain(0x00)
		vis_adc_counter(0x70)
		ir_adc_counter(0x70)
		set_als_mode(ALSAUTO)		
		reset_ir_adcmux()
		set_aux_mux()
		set_ir_range()
		set_vis_range()

#tool to store data in files per timestamp
	def write_data_to(file = "") :

		timestamp = time.asctime(time.localtime(time.time()))

		if(file != "") :
			filehandle = open(file, "a")
			lux = 0
			uvindex = 0

			uvindex = read_sensor_data(UV) / 1
	
			
			lux = (read_sensor_data(VIS) * 6.33) + (read_sensor_data(IR) * - 0.094)

			filehandle.write("time+%s+VIS+%6.1f+IR+%6.1f+UV+%3.1f+LUX+%6.1f\r\n" % (timestamp, 
                                                                      read_sensor_data(VIS),
			                                              read_sensor_data(IR),
                                                                      uvindex, 
								      lux))
			filehandle.close()

		else :
			print("Visual value: %6ilux Infrared value: %6ilux UV-Index: %3.1f" % 
                                                                      (read_sensor_data(VIS), 
                                                                       read_sensor_data(IR), 
                                                                       read_sensor_data(UV)))


	init_sensor()
	time.sleep(1)
	write_data_to("/var/www/wetter/si1132.dat")
