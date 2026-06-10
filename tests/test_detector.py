from unittest.mock import MagicMock, patch
import numpy as np
import pytest


def _make_mock_sess(class_scores, class_ids, category_index):
    sess = MagicMock()
    sess.run.return_value = (
        np.zeros((1, len(class_scores), 4)),
        np.array([class_scores]),
        np.array([class_ids]),
        np.array([len(class_scores)]),
    )
    return sess


def test_detect_filters_below_threshold():
    scores = [0.9, 0.3, 0.6]
    class_ids = [1.0, 2.0, 3.0]
    category_index = {1: {"name": "apple"}, 2: {"name": "banana"}, 3: {"name": "cup"}}

    mock_graph = MagicMock()
    mock_sess = _make_mock_sess(scores, class_ids, category_index)
    mock_graph.__enter__ = lambda s: s
    mock_graph.__exit__ = MagicMock(return_value=False)

    with patch("tensorflow.Graph", return_value=mock_graph), \
         patch("tensorflow.Session", return_value=mock_sess), \
         patch("tensorflow.GraphDef"), \
         patch("tensorflow.gfile.GFile"), \
         patch("tensorflow.import_graph_def"), \
         patch("sys.path"):
        from unittest.mock import MagicMock as MM
        import alfrd.detection.detector as det_module
        detector = MM()
        detector.threshold = 0.5
        detector.category_index = category_index
        detector._sess = mock_sess
        detector._image_tensor = "image_tensor:0"
        detector._boxes = mock_graph
        detector._scores = mock_graph
        detector._classes = mock_graph
        detector._num = mock_graph

        result = [
            category_index[int(class_ids[i])]["name"]
            for i, score in enumerate(scores)
            if score > detector.threshold
        ]
        assert result == ["apple", "cup"]
        assert "banana" not in result
