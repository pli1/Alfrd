import RPi.GPIO as GPIO
import time
import sys
import thread
import numpy as np
sys.path.append('/home/pi/Alfrd/scale')
from hx711 import HX711
sys.path.append('/home/pi/Alfrd/camera')
import camera
sys.path.append('/home/pi/Alfrd/yolo')
import darknet_v2
sys.path.append('/home/pi/Alfrd/mongodb')
import mongodb_connection as db
sys.path.append('/home/pi/Alfrd/led/python/examples')
from led_function import *

def cleanAndExit():
    print ("Cleaning...")
    GPIO.cleanup()
    print ("Bye!")
    sys.exit()

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = np.mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

print "initiating"
def led_initiating():
    colorWipe(strip, Color(255,255,255), wait_ms=10)
    colorWipe(strip, Color(0,0,0), wait_ms=1)
    
thread.start_new_thread(led_initiating,())

print "."
hx = HX711(5, 6)
print "."

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("LSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
#hx.set_reference_unit(92)
hx.set_reference_unit(-441)

hx.reset()
print "."
hx.tare()

weight_list=[0,0,0]
initial_weight=np.mean(weight_list)
print "Ready"


while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment the three lines to see what it prints.
        #np_arr8_string = hx.get_np_arr8_string()
        #binary_string = hx.get_binary_string()
        #print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        #kl-this is the original
        #this works....
        
        val = hx.get_weight(5)
        #print weight_list
        weight_list=weight_list[1:]
        weight_list.append(val)
        #print weight_list
        #print np.mean(weight_list)
        if abs(_ss(weight_list))<1:
            #Stable weight captured
            if abs(np.mean(weight_list)-initial_weight)<=1+initial_weight*0.05:
                #weight doesn't change
                continue
            else:
                print "new weight detected"
                dim(strip,wait_ms=3)
                print weight_list
                print np.mean(weight_list)
                initial_weight=np.mean(weight_list)
                #dim(strip,wait_ms=5)
                #camera.take_a_photo()
                #dim(strip,wait_ms=5)
                #darknet_v2.performDetect()
                showalllight(strip, Color(20,20,200), wait_ms=2, iterations=1)
                time.sleep(2)
                colorWipe(strip, Color(0,0,0), wait_ms=2)
                
        else:
            def fun1():
                print "measuring"
            def fun2():
                dim(strip,wait_ms=3)
            thread.start_new_thread(fun1,())
            thread.start_new_thread(fun2,())

        hx.reset()
        time.sleep(0.001)
        
    except (KeyboardInterrupt, SystemExit):
        colorWipe(strip, Color(0,0,0), wait_ms=10)
        cleanAndExit()

