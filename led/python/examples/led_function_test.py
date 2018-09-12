import sys
sys.path.append('/home/pi/Alfrd/led/python/examples')
from led_function import *

colorWipe(strip, Color(255,255,255), wait_ms=100)
colorWipe(strip, Color(0,0,0), wait_ms=1)
showalllight(strip, Color(20,20,200), wait_ms=200, iterations=1)
colorWipe(strip, Color(0,0,0), wait_ms=1)
dim(strip,wait_ms=3)
colorWipe(strip, Color(0,0,0), wait_ms=1)
