import logging
import os
from ultralytics import YOLO

from .types import Detection

logger = logging.getLogger(__name__)
os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"


class Detector:
    """
    Обёртка над YOLOv8. Возвращает список Detection, а не «сырые» данные Ultralytics.
    Интерфейс: __init__(model_path, confidence), predict(frame) -> list[Detection].
    """

    def __init__(self, model_path: str, confidence: float = 0.5):
        if not model_path:
            raise ValueError("model_path не может быть пустым")
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            raise RuntimeError(f"Не удалось загрузить модель {model_path}: {e}") from e
        self.confidence = confidence
        self.model_path = model_path
        logger.info("Detector loaded: %s, conf=%.2f", model_path, confidence)

    def predict(self, frame) -> list[Detection]:
        try:
            result = self.model.predict(
                frame,
                conf=self.confidence,
                verbose=False,
            )[0]
        except Exception as e:
            logger.error("Inference failed: %s", e)
            raise RuntimeError(f"Ошибка инференса: {e}") from e

        names = result.names
        detections: list[Detection] = []
        for box in result.boxes:
            cls_id = int(box.cls.item())
            conf = float(box.conf.item())
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detections.append(
                Detection(
                    class_id=cls_id,
                    class_name=str(names[cls_id]),
                    confidence=conf,
                    x1=x1, y1=y1, x2=x2, y2=y2,
                )
            )
        return detections

    def set_confidence(self, confidence: float) -> None:
        self.confidence = float(confidence)
        logger.info("Confidence threshold changed to %.2f", self.confidence)