import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.environ["MONGODB_URI"]

# HX711 GPIO pins (BCM numbering)
SCALE_DOUT_PIN = 5
SCALE_SCK_PIN = 6
# Calibration constant — recalculate if sensor is replaced:
# tare with no weight, then weigh a known mass and divide raw delta by grams
SCALE_REFERENCE_UNIT = -441

# Detection trigger thresholds
WEIGHT_WINDOW_SIZE = 10        # rolling sample window
WEIGHT_CHANGE_THRESHOLD_G = 2  # minimum change in grams to trigger detection
WEIGHT_CHANGE_TOLERANCE_PCT = 0.05  # additional 5% of baseline tolerance

# Camera
PHOTO_PATH = "/home/pi/Alfrd/picture.jpg"

# TensorFlow — path to the TF research/object_detection directory
TF_RESEARCH_PATH = "/home/pi/Alfrd/models/research/object_detection"
MODEL_NAME = "ssdlite_mobilenet_v2_coco_2018_05_09"
NUM_CLASSES = 90
DETECTION_THRESHOLD = 0.5

# LED strip (WS2812 / NeoPixel)
LED_COUNT = 19
LED_PIN = 18         # GPIO 18 (PWM)
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0
