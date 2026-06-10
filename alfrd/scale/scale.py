#!/usr/bin/python3
import statistics
from .hx711 import HX711


class Scale:
    def __init__(self, source=None, samples=20, spikes=4):
        self.source = source or HX711()
        self.samples = samples
        self.spikes = spikes
        self.history = []

    def _read(self):
        self.history.append(self.source.getWeight())
        self.history = self.history[-self.samples:]

    def getMeasure(self):
        """Continuous measurement — keeps history for spike filtering."""
        self._read()
        avg = statistics.mean(self.history)
        deltas = sorted(abs(v - avg) for v in self.history)
        max_delta = deltas[-self.spikes] if len(deltas) >= self.spikes else deltas[-1]
        valid = [v for v in self.history if abs(v - avg) <= max_delta]
        return statistics.mean(valid)

    def getWeight(self, samples=None):
        """One-shot measurement — clears history before sampling."""
        self.history = []
        for _ in range(samples or self.samples):
            self._read()
        return self.getMeasure()

    def tare(self, times=25):
        self.source.tare(times)

    def setOffset(self, offset):
        self.source.setOffset(offset)

    def setReferenceUnit(self, reference_unit):
        self.source.setReferenceUnit(reference_unit)

    def powerDown(self):
        self.source.powerDown()

    def powerUp(self):
        self.source.powerUp()

    def reset(self):
        self.source.reset()
