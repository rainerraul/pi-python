# pi-weather
I had bought this Odroid-Weatherboard by a german distributor. The compact dimensions allows three sensors on one Board to attach all to a raspberry pi. The quick2wire-libraries i used, makes it possible to build code for weather-apps in python. During the python code works in the background, the pi can make collected weatherdata public over a web-server for an example. But first they have to be stored on local memory. For later outputting data and visualisation on a browser, i have to create some php-scripts.<br>
(14 05 2015)<br>
The programming of these sensors on the weatherboard are complete. The next thing what i will do is to create a graphical interface for websites in php, a table output and some search routines.
to be continued...<br>
(10 06 2015)<br>
Added a python-script called lcdprint. You can send a message to a twi-interfaced YuroBot display 4x20.
open a ssh-shell and type: <font style="color:red">lcdprint linenumber(0-3) "Hello Message"</font>. Use this python-file to display data from
sensor devices, that are connected on the same i2c bus, where the LCD-Display is.
