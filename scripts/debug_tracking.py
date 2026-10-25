import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture.video_capture import VideoSource
from src.tracking.tracker import Tracker

def main():
    # Используем НАШУ новую модель
    model_path = "models/yolov8n_ppe_v2.pt" 
    tracker = Tracker(model_path, confidence=0.4)
    vs = VideoSource(0, reconnect_sec=2.0)

    vs.open()
    print(f"Модель {model_path} загружена. Читаю кадры...")
    
    try:
        while True:
            frame = vs.read()
            tracks = tracker.track(frame)
            
            # Выводим в консоль, сколько объектов нашлось на кадре
            if len(tracks) > 0:
                print(f"Найдено объектов: {len(tracks)}")
                for t in tracks:
                    print(f"  ID:{t.track_id} | {t.class_name} | conf: {t.confidence:.2f}")
            
            # Ждем 0.5 секунды, чтобы не засорять консоль
            import cv2
            if cv2.waitKey(500) & 0xFF == ord('q'):
                break
    finally:
        vs.close()

if __name__ == "__main__":
    main()