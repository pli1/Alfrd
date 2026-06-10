#!/usr/bin/python3
import statistics
import time
import RPi.GPIO as GPIO


class HX711:
    def __init__(self, dout=5, pd_sck=6, gain=128, bitsToRead=24):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.REFERENCE_UNIT = 1
        self.GAIN = 0
        self.OFFSET = 1
        self.lastVal = 0
        self.bitsToRead = bitsToRead
        self.twosComplementThreshold = 1 << (bitsToRead - 1)
        self.twosComplementOffset = -(1 << bitsToRead)
        self.setGain(gain)
        self.read()

    def isReady(self):
        return GPIO.input(self.DOUT) == 0

    def setGain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        GPIO.output(self.PD_SCK, False)
        self.read()

    def waitForReady(self):
        while not self.isReady():
            pass

    def correctTwosComplement(self, unsignedValue):
        if unsignedValue >= self.twosComplementThreshold:
            return unsignedValue + self.twosComplementOffset
        return unsignedValue

    def read(self):
        self.waitForReady()
        unsignedValue = 0
        for i in range(self.bitsToRead):
            GPIO.output(self.PD_SCK, True)
            bitValue = GPIO.input(self.DOUT)
            GPIO.output(self.PD_SCK, False)
            unsignedValue = (unsignedValue << 1) | bitValue
        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)
        return self.correctTwosComplement(unsignedValue)

    def getValue(self):
        return self.read() - self.OFFSET

    def getWeight(self):
        return self.getValue() / self.REFERENCE_UNIT

    def tare(self, times=25):
        reference_unit = self.REFERENCE_UNIT
        self.setReferenceUnit(1)
        cut = times // 5
        values = sorted([self.read() for _ in range(times)])[cut:-cut]
        self.setOffset(statistics.mean(values))
        self.setReferenceUnit(reference_unit)

    def setOffset(self, offset):
        self.OFFSET = offset

    def setReferenceUnit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    def powerDown(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def powerUp(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)

    def reset(self):
        self.powerDown()
        self.powerUp()
