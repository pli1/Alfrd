from picamera import PiCamera
import config


def take_a_photo():
    camera = PiCamera()
    camera.capture(config.PHOTO_PATH)
    camera.close()
