import os
os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"

import logging
from dataclasses import dataclass
from ultralytics import YOLO

logger = logging.getLogger(__name__)

@dataclass
class Track:
    """Объект с присвоенным Track ID."""
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def bottom_center(self) -> tuple[int, int]:
        return ((self.x1 + self.x2) // 2, self.y2)

class Tracker:
    """Обёртка над Ultralytics tracking (ByteTrack)."""
    def __init__(self, model_path: str, confidence: float = 0.5):
        self.model = YOLO(model_path)
        self.confidence = confidence
        logger.info("Tracker loaded: %s", model_path)

    def track(self, frame) -> list[Track]:
        # persist=True критически важен: он сохраняет состояние между кадрами
        results = self.model.track(frame, conf=self.confidence, tracker="bytetrack.yaml", persist=True, verbose=False)[0]
        
        tracks = []
        if results.boxes.id is None:
            return tracks  # В первых кадрах ID еще не присвоены
            
        ids = results.boxes.id.int().cpu().tolist()
        names = results.names
        
        for box, track_id in zip(results.boxes, ids):
            cls_id = int(box.cls.item())
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            tracks.append(Track(
                track_id=int(track_id),
                class_id=cls_id,
                class_name=str(names[cls_id]),
                confidence=float(box.conf.item()),
                x1=x1, y1=y1, x2=x2, y2=y2,
            ))
        return tracks