import os
import sys
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture.video_capture import VideoSource
from src.capture.fps_meter import FPSMeter
from src.inference.detector import Detector


CLASS_COLORS = {
    "person": (0, 200, 0),
    "car": (255, 100, 0),
    "truck": (0, 100, 255),
    "bus": (0, 200, 255),
    "motorcycle": (200, 0, 200),
    "bicycle": (150, 150, 0),
}
DEFAULT_COLOR = (255, 255, 255)


def draw_detection(frame, det):
    color = CLASS_COLORS.get(det.class_name, DEFAULT_COLOR)
    cv2.rectangle(frame, (det.x1, det.y1), (det.x2, det.y2), color, 2)
    label = f"{det.class_name} {det.confidence:.2f}"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (det.x1, det.y1 - th - 6), (det.x1 + tw, det.y1), color, -1)
    cv2.putText(frame, label, (det.x1, det.y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)


def main():
    source = 0  # веб-камера; можно "data/test_video.mp4"
    model_path = "models/yolov8n.pt"
    confidence = 0.4

    print(f"Загружаю модель {model_path}...")
    detector = Detector(model_path, confidence=confidence)
    print("Модель загружена.")

    vs = VideoSource(source, reconnect_sec=2.0)
    fps_meter = FPSMeter(window=30)

    try:
        vs.open()
        print(f"Источник открыт: {source}. Клик по окну → 'q' для выхода.")
        while True:
            frame = vs.read()
            detections = detector.predict(frame)
            for det in detections:
                draw_detection(frame, det)

            fps = fps_meter.tick()
            cv2.putText(frame, f"FPS: {fps:.1f} | Objects: {len(detections)}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow("YOLOv8 Detector Test", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), ord('Q'), ord('й'), 27):
                break
    except RuntimeError as e:
        print(f"Ошибка: {e}")
    finally:
        vs.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()