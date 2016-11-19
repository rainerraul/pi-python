#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as sqldb
import time


handle = sqldb.connect('localhost', 'root', 'rainermysql', 'test')
loggingFiler = open("/home/pi/python/loggLm75.log", 'rt')
loggerdata = loggingFiler.read()

parts = loggerdata.split(',', 3)

zeit = parts[0]
thos = float(parts[1])
thys = float(parts[2])
val = float(parts[3])


with handle:
	pointer = handle.cursor()
	insert = "INSERT INTO logtablelm75(datum,thyst,thos,temp)VALUES('%s',%.1f,%.1f,%.1f)" %(zeit,thos,thys,val)
	#print(insert)
	result = pointer.execute(insert)

if handle:
	handle.close()
	
loggingFiler.close()


