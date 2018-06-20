from picamera import PiCamera
from time import sleep

def take_a_photo():
    camera = PiCamera()
    camera.start_preview()
    camera.capture('/home/pi/Alfrd/picture.jpg')
    camera.stop_preview()
    camera.close()
