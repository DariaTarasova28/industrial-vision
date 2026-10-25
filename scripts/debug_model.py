import os
os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"

import cv2
from ultralytics import YOLO

def main():
    # ПУТЬ К НАШЕЙ НОВОЙ МОДЕЛИ
    model_path = "models/yolov8n_ppe_v2.pt"
    
    if not os.path.exists(model_path):
        print(f"❌ Файл не найден: {model_path}")
        return
        
    print(f"Загружаю {model_path}...")
    model = YOLO(model_path)
    
    # Посмотрим, какие классы зашиты в модель
    print("Классы модели:", model.names)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Камера не открылась")
        return
        
    print("Нажмите 'q' для выхода. Смотрите в камеру.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Делаем предсказание напрямую, без трекера, с очень низким порогом (0.1)
        results = model.predict(frame, conf=0.1, verbose=False)
        
        # Выводим в консоль, что нашла модель
        boxes = results[0].boxes
        if len(boxes) > 0:
            print(f"\n--- Найдено объектов: {len(boxes)} ---")
            for box in boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                print(f"  Класс: {model.names[cls_id]} | Уверенность: {conf:.3f}")
        
        # Рисуем результат (встроенными средствами Ultralytics)
        annotated_frame = results[0].plot()
        cv2.imshow("Debug Model", annotated_frame)
        
        if cv2.waitKey(1000) & 0xFF == ord('q'): # Ждем 1 сек между кадрами
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()