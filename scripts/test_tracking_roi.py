import os
import sys
import cv2
import numpy as np
from datetime import datetime, timezone
from uuid import uuid4

# ВАЖНО: sys.path должен быть в самом верху, до всех локальных импортов!
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture.video_capture import VideoSource
from src.tracking.tracker import Tracker
from src.events.event_engine import EventEngine, Event
from src.events.storage import EventStorage
from src.analytics.ppe_checker import PPEChecker
from src.inference.detector import Detector

# Определяем запретную зону (подстройте координаты под ваше видео).
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
    source = "data/steam.mp4"  # Убедитесь, что видео на месте!
    ppe_model_path = "models/yolov8n_ppe_v2.pt"
    fire_model_path = "models/yolov8n_dfire.pt"

    print(f"Загружаю модель СИЗ: {ppe_model_path}...")
    tracker = Tracker(ppe_model_path, confidence=0.4)
    
    print(f"Загружаю модель Дым/Огонь: {fire_model_path}...")
    fire_detector = Detector(fire_model_path, confidence=0.4)

    event_engine = EventEngine(restricted_polygon=POLYGON, cooldown_sec=5.0)
    storage = EventStorage(base_dir="events")
    ppe_checker = PPEChecker()

    vs = VideoSource(source, reconnect_sec=2.0)

    try:
        vs.open()
        print("Запущено. Клик по окну → 'q' для выхода.")
        
        while True:
            frame = vs.read()
            
            # 1. Детекция и трекинг людей и СИЗ
            tracks = tracker.track(frame)
            
            # 2. Детекция дыма и огня
            fire_dets = fire_detector.predict(frame)

            # 3. Рисуем зону
            draw_polygon(frame, POLYGON)

            # 4. Рисуем треки (людей и СИЗ)
            for t in tracks:
                color = (0, 255, 0) if t.class_name == "Person" else (255, 100, 0)
                cv2.rectangle(frame, (t.x1, t.y1), (t.x2, t.y2), color, 2)
                label = f"ID:{t.track_id} {t.class_name} {t.confidence:.2f}"
                cv2.putText(frame, label, (t.x1, t.y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 5. Рисуем дым и огонь
            for det in fire_dets:
                if det.class_name in ["smoke", "fire"]:
                    # Оранжевый для дыма, красный для огня
                    color = (0, 165, 255) if det.class_name == "smoke" else (0, 0, 255)
                    cv2.rectangle(frame, (det.x1, det.y1), (det.x2, det.y2), color, 2)
                    label = f"{det.class_name} {det.confidence:.2f}"
                    cv2.putText(frame, label, (det.x1, det.y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # 6. Проверяем события ВХОДА В ЗОНУ (ROI)
            roi_events = event_engine.process(tracks)
            if roi_events:
                event = roi_events[0]
                saved_path = storage.save_event(event, frame)
                print(f"🔥 СОБЫТИЕ ROI: {event.event_type} | ID: {event.track_id}")
                cv2.putText(frame, f"!!! {event.event_type.upper()} !!!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

            # 7. Проверяем события СИЗ (Каска)
            ppe_violations = ppe_checker.check_tracks(tracks)
            for v in ppe_violations:
                person = v["track"]
                
                event = Event(
                    event_id=str(uuid4()),
                    event_type=v["type"], # "ppe_helmet_missing"
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    camera_id="cam_01",
                    confidence=person.confidence,
                    track_id=person.track_id,
                    coordinates={"x": person.bottom_center[0], "y": person.bottom_center[1]}
                )
                
                saved_path = storage.save_event(event, frame)
                print(f"🔥 НАРУШЕНИЕ СИЗ: {event.event_type} | ID: {event.track_id} -> {saved_path}")
                
                cv2.putText(frame, f"!!! {event.event_type.upper()} !!!", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 3)

            # 8. Показываем результат
            cv2.imshow("Full Vision Pipeline (PPE + Fire + ROI)", frame)
            
            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q'), ord('й'), 27):
                break
                
    except RuntimeError as e:
        print(f"Ошибка: {e}")
    finally:
        vs.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()