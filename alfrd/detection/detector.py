import os
import sys
import numpy as np
from PIL import Image
import tensorflow as tf
import config

# TF object-detection research utilities live outside this package
sys.path.append(config.TF_RESEARCH_PATH)
from utils import label_map_util  # noqa: E402


class Detector:
    """Loads a frozen TensorFlow graph once and exposes a detect() method."""

    def __init__(self, model_name=None, num_classes=None, threshold=None):
        model_name = model_name or config.MODEL_NAME
        num_classes = num_classes or config.NUM_CLASSES
        self.threshold = threshold if threshold is not None else config.DETECTION_THRESHOLD

        root = os.path.dirname(os.path.abspath(config.__file__))
        path_to_ckpt = os.path.join(root, model_name, "frozen_inference_graph.pb")
        path_to_labels = os.path.join(root, "data", "mscoco_label_map.pbtxt")

        label_map = label_map_util.load_labelmap(path_to_labels)
        categories = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=num_classes, use_display_name=True
        )
        self.category_index = label_map_util.create_category_index(categories)

        graph = tf.Graph()
        with graph.as_default():
            graph_def = tf.GraphDef()
            with tf.gfile.GFile(path_to_ckpt, "rb") as fid:
                graph_def.ParseFromString(fid.read())
                tf.import_graph_def(graph_def, name="")
            self._sess = tf.Session(graph=graph)

        self._image_tensor = graph.get_tensor_by_name("image_tensor:0")
        self._boxes = graph.get_tensor_by_name("detection_boxes:0")
        self._scores = graph.get_tensor_by_name("detection_scores:0")
        self._classes = graph.get_tensor_by_name("detection_classes:0")
        self._num = graph.get_tensor_by_name("num_detections:0")

    def detect(self, image_path):
        """Return a list of object name strings detected above the confidence threshold."""
        image = Image.open(image_path)
        image_np = np.array(image.getdata()).reshape(
            (image.size[1], image.size[0], 3)
        ).astype(np.uint8)
        image_expanded = np.expand_dims(image_np, axis=0)

        (boxes, scores, classes, num) = self._sess.run(
            [self._boxes, self._scores, self._classes, self._num],
            feed_dict={self._image_tensor: image_expanded},
        )

        return [
            self.category_index[classes[0][i]]["name"]
            for i, score in enumerate(scores[0])
            if score > self.threshold
        ]
