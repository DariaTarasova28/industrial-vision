import os
import sys
import cv2

# Позволяем запускать скрипт из корня проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture.video_capture import VideoSource
from src.capture.fps_meter import FPSMeter


def main():
    # ВАРИАНТ A: видеофайл (положите mp4 в data/)
    # source = "data/test_video.mp4"
    # ВАРИАНТ B: USB-камера
    source = 0

    vs = VideoSource(source, reconnect_sec=2.0)
    fps_meter = FPSMeter(window=30)

    try:
        vs.open()
        print(f"Источник открыт: {source}. Нажмите 'q' для выхода.")
        while True:
            frame = vs.read()
            fps = fps_meter.tick()
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv2.imshow("Video Capture Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except RuntimeError as e:
        print(f"Ошибка: {e}")
    finally:
        vs.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()