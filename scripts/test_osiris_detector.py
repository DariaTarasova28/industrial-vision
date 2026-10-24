import json
import time
import cv2
import numpy as np
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.inference.detector import Detector

# Путь к сохранённому JSON
JSON_PATH = "data/osiris_cameras.json"

def load_cameras():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cameras"]

def get_snapshot_url(camera):
    """Возвращает полный URL для скачивания снимка."""
    feed_url = camera["feed_url"]
    if feed_url.startswith("http"):
        return feed_url
    else:
        return "https://osirisai.live" + feed_url

def download_snapshot(url, timeout=10):
    """Скачивает JPEG-снимок и возвращает его как numpy array (BGR)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://osirisai.live/",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    img_array = np.frombuffer(resp.content, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Не удалось декодировать изображение")
    return frame

def draw_detection(frame, det):
    color = (0, 255, 0) if det.class_name == "person" else (255, 100, 0)
    cv2.rectangle(frame, (det.x1, det.y1), (det.x2, det.y2), color, 2)
    label = f"{det.class_name} {det.confidence:.2f}"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (det.x1, det.y1 - th - 6), (det.x1 + tw, det.y1), color, -1)
    cv2.putText(frame, label, (det.x1, det.y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

def main():
    cameras = load_cameras()
    print(f"Загружено {len(cameras)} камер.")

    # Выберите камеру. Например, первую с source == "Houston TranStar" (прямой URL)
    # или любую TxDOT. Для примера возьмём Houston TranStar.
    camera = None
    for cam in cameras:
        if cam["source"] == "Houston TranStar":
            camera = cam
            break
    if camera is None:
        camera = cameras[0]  # fallback

    print(f"Выбрана камера: {camera['name']} ({camera['city']})")
    url = get_snapshot_url(camera)
    print(f"URL снимка: {url}")

    # Инициализация детектора
    print("Загружаю модель YOLOv8n...")
    detector = Detector("models/yolov8n.pt", confidence=0.4)
    print("Модель загружена. Нажмите 'q' для выхода.")

    last_time = 0
    while True:
        try:
            # Скачиваем снимок не чаще, чем раз в 1 секунду
            now = time.time()
            if now - last_time < 1.0:
                time.sleep(0.1)
                continue
            last_time = now

            frame = download_snapshot(url)
            detections = detector.predict(frame)
            for det in detections:
                draw_detection(frame, det)

            cv2.putText(frame, f"Objects: {len(detections)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow("OsirisAI Camera Detection", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), ord('Q'), ord('й'), 27):
                break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(2)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()