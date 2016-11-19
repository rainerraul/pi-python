# pi-python
I had bought this Odroid-Weatherboard by a german distributor. The compact dimensions allows three sensors on one Board to attach all to a raspberry pi. The quick2wire-libraries i used, makes it possible to build code for weather-apps in python. During the python code works in the background, the pi can make collected weatherdata public over a web-server for an example. But first they have to be stored on local memory. For later outputting data and visualisation on a browser, i have to create some php-scripts.<br>
<b>(14 05 2015)</b><br>
The programming of these sensors on the weatherboard are complete. The next thing what i will do is to create a graphical interface for websites in php, a table output and some search routines.
to be continued...<br>
<b>(10 06 2015)</b><br>
Added a python-script called lcdprint. You can send a message to a twi-interfaced YuroBot display 4x20.
open a ssh-shell and type: <font color="red"><b><p style="font-color:red">lcdprint linenumber(0-3) "Hello Message".</p></b></font> Use this python-file to display data from
sensor devices, that are connected on the same i2c bus, where the LCD-Display is.<br>
<b>(19 11 2016)</b><br>
The sht31 humidity sensor from Sensirion runs without crc(byte3 and byte6 are the checksum bytes). Since i start datalogging the<br> sensor have not fail and works fine.<br>
LM75 is a sensor, that measure temperature and drive an open collector outlet. Also you can configurate a hysteresis value and a<br> maximum temperature value. The outlet is high, when current temperature is over its maximum and low, when the current<br> temperature is under the hysteresis value. It acts like a thermostate for heating.
