import sys
import time
import threading

import numpy as np
import RPi.GPIO as GPIO

import config
from alfrd.scale.hx711 import HX711
from alfrd.camera.camera import take_a_photo
from alfrd.detection.detector import Detector
from alfrd.led.led import init_strip, colorWipe, showalllight, dim, Color
import alfrd.db.mongodb as db


def _sum_of_squares(data):
    c = np.mean(data)
    return sum((x - c) ** 2 for x in data)


def _led_startup(strip):
    colorWipe(strip, Color(255, 255, 255), wait_ms=100)
    colorWipe(strip, Color(0, 0, 0), wait_ms=1)


def _led_processing(strip, stop_event):
    while not stop_event.is_set():
        dim(strip, wait_ms=3)


def _detect_and_upload(weight, detector):
    take_a_photo()
    objs = detector.detect(config.PHOTO_PATH)
    db.populate_3_tables(weight, objs)
    return objs


def run():
    strip = init_strip()

    startup = threading.Thread(target=_led_startup, args=(strip,))
    startup.start()

    hx = HX711(dout=config.SCALE_DOUT_PIN, pd_sck=config.SCALE_SCK_PIN)
    hx.setReferenceUnit(config.SCALE_REFERENCE_UNIT)
    hx.reset()
    hx.tare()

    detector = Detector()

    weight_window = [0.0] * config.WEIGHT_WINDOW_SIZE
    baseline = float(np.mean(weight_window))

    startup.join()
    showalllight(strip, Color(5, 250, 5), wait_ms=2)
    time.sleep(2)
    colorWipe(strip, Color(0, 0, 0), wait_ms=2)
    print("Ready")

    while True:
        try:
            val = hx.getWeight()
            weight_window = weight_window[1:] + [val]
            current = float(np.mean(weight_window))

            if abs(_sum_of_squares(weight_window)) < 1:
                threshold = abs(config.WEIGHT_CHANGE_THRESHOLD_G + baseline * config.WEIGHT_CHANGE_TOLERANCE_PCT)
                if abs(current - baseline) > threshold:
                    print(f"Weight change detected: {current:.1f}g (was {baseline:.1f}g)")
                    baseline = current

                    stop_event = threading.Event()
                    processing = threading.Thread(target=_led_processing, args=(strip, stop_event))
                    processing.start()

                    objs = _detect_and_upload(current, detector)
                    print(f"Detected: {objs}")

                    stop_event.set()
                    processing.join()
                    showalllight(strip, Color(20, 20, 200), wait_ms=2)
                    time.sleep(2)
                    colorWipe(strip, Color(0, 0, 0), wait_ms=2)
            else:
                print("Measuring...")

        except (KeyboardInterrupt, SystemExit):
            colorWipe(strip, Color(0, 0, 0), wait_ms=10)
            GPIO.cleanup()
            print("Stopped.")
            sys.exit()


if __name__ == "__main__":
    run()
