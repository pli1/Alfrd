from __future__ import print_function

import time
import sys
sys.path.append('scale')
from hx711 import HX711
sys.path.append('camera')
import camera
sys.path.append('led/python/examples')
from led_function import *

#sys.path.append('/home/pi/Alfrd/yolo')
#import darknet_v2
sys.path.append('mongodb')
import mongodb_connection as db
import RPi.GPIO as GPIO
import multiprocessing
import numpy as np

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = np.mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def led_initiating():
    colorWipe(strip, Color(255,255,255), wait_ms=100)
    colorWipe(strip, Color(0,0,0), wait_ms=1)

print ("initiating")
p = multiprocessing.Process(target = led_initiating)
p.start()

# choose pins on rpi (BCM5 and BCM6)
hx = HX711(dout=5, pd_sck=6)

# HOW TO CALCULATE THE REFFERENCE UNIT
#########################################
# To set the reference unit to 1.
# Call get_weight before and after putting 1000g weight on your sensor.
# Divide difference with grams (1000g) and use it as refference unit.

hx.setReferenceUnit(-441)

hx.reset()
hx.tare()

weight_list=[0,0,0,0,0,0,0,0,0,0]
initial_weight=np.mean(weight_list)
print ("Ready")
p.join()
showalllight(strip, Color(5,250,5), wait_ms=2, iterations=1)
time.sleep(2)
colorWipe(strip, Color(0,0,0), wait_ms=2)

def detect_obj():
    camera.take_a_photo()
    all_results=darknet_v2.performDetect()
    objs=all_results[1]
    return objs

def detect_n_upload(weight):
    objs=detect_obj()
    mgdb.populate_3_tables(weight,objs)
    return 0

def check_weight(weight_list,initial_weight):
	current_weight=(np.mean(weight_list))
	print ('current weight'+str(current_weight))
	print ('previous weight'+str(initial_weight))
	print ('weight changed from last detected weight'+str(abs(current_weight-initial_weight)))
	print (str(1+initial_weight*0.05))
	print (abs(current_weight-initial_weight)<=abs(2+initial_weight*0.05))

def fun2():
	while True:
		dim(strip,wait_ms=3)

while True:
    try:        
        val = hx.getWeight()
        #print weight_list
        weight_list=weight_list[1:]
        weight_list.append(val)
        #print weight_list
        #print np.mean(weight_list)
        current_weight=(np.mean(weight_list))        
        #check_weight()
        if abs(_ss(weight_list))<1:
            #Stable weight captured
            if abs(current_weight-initial_weight)<=abs(2+initial_weight*0.05):
                #weight doesn't change
                pass
            else:
                print ("new weight detected")
                initial_weight=np.mean(weight_list)
                p = multiprocessing.Process(target = fun2)
                #q = multiprocessing.Process(target = detect_n_upload,args=(np.mean(weight_list),))
                
                #q.start()
                p.start()

                
                #dim(strip,wait_ms=3)
                #print weight_list
                print (np.mean(weight_list))
                
                dim(strip,wait_ms=5)
                
                
                #q.join()
                p.terminate()
                showalllight(strip, Color(20,20,200), wait_ms=2, iterations=1)
                time.sleep(2)
                colorWipe(strip, Color(0,0,0), wait_ms=2)
                
        else:
            print ("measuring")
                
        
    except (KeyboardInterrupt, SystemExit):
        colorWipe(strip, Color(0,0,0), wait_ms=10)
        GPIO.cleanup()
        print ("Program Ended")
        sys.exit()
