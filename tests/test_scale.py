from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_hx():
    return MagicMock()


def test_spike_filter_excludes_outliers(mock_hx):
    with patch.dict("sys.modules", {"RPi": MagicMock(), "RPi.GPIO": MagicMock()}):
        from alfrd.scale.scale import Scale

        readings = [100.0] * 18 + [500.0, 100.0]
        mock_hx.getWeight.side_effect = readings
        scale = Scale(source=mock_hx, samples=20, spikes=2)
        result = scale.getWeight()
        assert abs(result - 100.0) < 1.0


def test_getweight_clears_history(mock_hx):
    with patch.dict("sys.modules", {"RPi": MagicMock(), "RPi.GPIO": MagicMock()}):
        from alfrd.scale.scale import Scale

        mock_hx.getWeight.return_value = 50.0
        scale = Scale(source=mock_hx, samples=5)
        scale.history = [999.0] * 10
        scale.getWeight()
        assert len(scale.history) <= 5


def test_sum_of_squares_zero_for_constant():
    import numpy as np
    with patch.dict("sys.modules", {
        "RPi": MagicMock(), "RPi.GPIO": MagicMock(),
        "alfrd.detection.detector": MagicMock(),
        "alfrd.led.led": MagicMock(),
        "alfrd.db.mongodb": MagicMock(),
        "alfrd.camera.camera": MagicMock(),
        "config": MagicMock(
            SCALE_DOUT_PIN=5, SCALE_SCK_PIN=6, SCALE_REFERENCE_UNIT=-441,
            WEIGHT_WINDOW_SIZE=10, WEIGHT_CHANGE_THRESHOLD_G=2,
            WEIGHT_CHANGE_TOLERANCE_PCT=0.05, PHOTO_PATH="/tmp/pic.jpg",
        ),
    }):
        from alfrd.main import _sum_of_squares
        assert _sum_of_squares([5.0] * 10) == pytest.approx(0.0)
