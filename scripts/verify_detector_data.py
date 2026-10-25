import os
import sys
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.inference.detector import Detector
from src.inference.types import Detection


def main():
    detector = Detector("models/yolov8n.pt", confidence=0.4)

    # Берём одно тестовое изображение (или кадр с веб-камеры)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Камера недоступна")
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("Не удалось получить кадр")

    detections = detector.predict(frame)

    print(f"Тип результата: {type(detections)}")
    print(f"Количество детекций: {len(detections)}")

    for i, det in enumerate(detections):
        # Явная проверка, что это наш dataclass, а не «сырые» данные Ultralytics
        assert isinstance(det, Detection), "Это не Detection!"
        print(
            f"  [{i}] class_id={det.class_id}, class_name={det.class_name!r}, "
            f"confidence={det.confidence:.3f}, "
            f"bbox=({det.x1},{det.y1},{det.x2},{det.y2}), "
            f"center={det.center}, bottom_center={det.bottom_center}"
        )

    print("\n✅ Проверка пройдена: детектор возвращает список Detection")


if __name__ == "__main__":
    main()