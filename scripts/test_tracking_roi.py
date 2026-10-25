import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture.video_capture import VideoSource
from src.tracking.tracker import Tracker
from src.events.event_engine import EventEngine
from src.events.storage import EventStorage  # <--- ДОБАВИЛИ ИМПОРТ

# Определяем запретную зону. 
POLYGON = [
    (400, 300),  # левый верх
    (900, 300),  # правый верх
    (900, 700),  # правый низ
    (400, 700),  # левый низ
]

def draw_polygon(frame, polygon):
    pts = np.array(polygon, np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], True, (0, 0, 255), 2)
    cv2.putText(frame, "RESTRICTED ZONE", (polygon[0][0], polygon[0][1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

def main():
    source = "data/build.mp4"
    model_path = "models/yolov8n_ppe_v2.pt"

    tracker = Tracker(model_path, confidence=0.4)
    event_engine = EventEngine(restricted_polygon=POLYGON, cooldown_sec=5.0)
    
    # <--- ДОБАВИЛИ ИНИЦИАЛИЗАЦИЮ ХРАНИЛИЩА
    storage = EventStorage(base_dir="events") 

    vs = VideoSource(source, reconnect_sec=2.0)

    try:
        vs.open()
        print("Запущено. Клик по окну → 'q' для выхода.")
        while True:
            frame = vs.read()
            tracks = tracker.track(frame)

            # Рисуем зону
            draw_polygon(frame, POLYGON)

            # Рисуем треки
            for t in tracks:
                color = (0, 255, 0) if t.class_name == "Person" else (255, 100, 0)
                cv2.rectangle(frame, (t.x1, t.y1), (t.x2, t.y2), color, 2)
                label = f"ID:{t.track_id} {t.class_name} {t.confidence:.2f}"
                cv2.putText(frame, label, (t.x1, t.y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Формируем события
            events = event_engine.process(tracks)
            if events:
                event = events[0]
                
                # <--- ДОБАВИЛИ СОХРАНЕНИЕ СОБЫТИЯ И СНИМКА
                saved_path = storage.save_event(event, frame)
                print(f"🔥 СОБЫТИЕ СОХРАНЕНО: {event.event_type} | ID: {event.track_id} -> {saved_path}")

                # Выводим на экран
                cv2.putText(frame, f"!!! EVENT: {event.event_type} !!!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

            cv2.imshow("Tracking & ROI Test", frame)
            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q'), ord('й'), 27):
                break
    except RuntimeError as e:
        print(f"Ошибка: {e}")
    finally:
        vs.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()