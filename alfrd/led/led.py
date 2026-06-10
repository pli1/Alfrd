import time
from rpi_ws281x import Adafruit_NeoPixel, Color  # noqa: F401 — re-exported for callers
import config


def init_strip():
    strip = Adafruit_NeoPixel(
        config.LED_COUNT, config.LED_PIN, config.LED_FREQ_HZ,
        config.LED_DMA, config.LED_INVERT, config.LED_BRIGHTNESS, config.LED_CHANNEL,
    )
    strip.begin()
    return strip


def colorWipe(strip, color, wait_ms=200):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def showalllight(strip, color, wait_ms=20):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(wait_ms / 1000.0)


def dim(strip, wait_ms=20):
    """Breathing animation: ramp up then ramp down white light."""
    for j in range(5, 250):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(j, j, j))
        strip.show()
        time.sleep(wait_ms / 1000.0)
    for j in range(5, 250):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(255 - j, 255 - j, 255 - j))
        strip.show()
        time.sleep(wait_ms / 1000.0)
