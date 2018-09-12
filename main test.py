#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main test.py
#  
#  Copyright 2018  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


def main(args):
	sys.path.append('led/python/examples')
	from led_function import *
	sys.path.append('scale')
	from hx711 import HX711
	colorWipe(strip, Color(255,255,255), wait_ms=100)
	colorWipe(strip, Color(0,0,0), wait_ms=1)
	showalllight(strip, Color(20,20,200), wait_ms=200, iterations=1)
	colorWipe(strip, Color(0,0,0), wait_ms=1)
	dim(strip,wait_ms=3)
	colorWipe(strip, Color(0,0,0), wait_ms=1)
	print ("imported")

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
