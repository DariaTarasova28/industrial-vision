# Industrial Vision — прототип системы компьютерного зрения
 Лабораторная работа 
«Компьютерное зрение и Edge AI»
## Назначение

Модуль анализирует видеопоток с камеры мобильной платформы и формирует
структурированные события:

- детекция людей и транспорта;
- контроль средств индивидуальной защиты (каска, жилет);
- детекция дыма и огня;
- исследовательская детекция разлива жидкости;
- tracking объектов, контроль ROI-зон, Event Engine, REST API.

Основная обработка выполняется локально (Edge AI), без зависимости от
внешнего канала связи.

## Требования

- Python 3.9+ (проверено на 3.9.13)
- Windows / Linux / macOS
- (опционально) GPU NVIDIA с CUDA для ускорения обучения
- (опционально) веб-камера или видеофайл для тестирования

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/DariaTarasova28/industrial-vision.git
   cd industrial-vision
   ```

2. Создайте виртуальное окружение и активируйте:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Windows cmd:
   .venv\Scripts\activate.bat
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. Установите зависимости:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Скачайте предобученную модель YOLOv8n (~6 МБ):
   ```bash
   mkdir -p models
   # Windows PowerShell:
   Invoke-WebRequest -Uri "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt" -OutFile "models/yolov8n.pt"
   # Linux / macOS:
   curl -L -o models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
   ```

## Запуск

### Тест видеозахвата (Этап 2)

```bash
python scripts/test_capture.py
```

По умолчанию открывается веб-камера (`source = 0`). Чтобы читать видеофайл,
положите mp4 в `data/test_video.mp4` и поменяйте `source` в скрипте.

**Управление:** кликнуть по окну с видео, затем нажать `q` (или `Esc`) для
выхода. Клик по окну обязателен: клавиатурные события получает только окно в
фокусе.

**Что вы увидите:** окно с видео и зелёная надпись `FPS: XX.X` в левом
верхнем углу.


## Структура проекта

```
industrial-vision/
├── configs/          # конфигурационные YAML (пороги, ROI, камеры)
├── data/             # локальные тестовые видео (в .gitignore)
├── datasets/         # датасеты для обучения (в .gitignore)
├── docs/             # схемы архитектуры, Dataset Card, Model Card
├── models/           # веса моделей (в .gitignore)
├── scripts/          # вспомогательные скрипты запуска
├── src/
│   ├── capture/      # захват видео, FPS, reconnect
│   ├── inference/    # обёртка над YOLO, единый формат Detection
│   ├── tracking/     # трекинг (ByteTrack / BoT-SORT)
│   ├── zones/        # ROI-полигоны и проверка попадания
│   ├── analytics/    # логика СИЗ, дыма, огня, разлива
│   ├── events/       # Event Engine, JSON-сериализация
│   ├── api/          # FastAPI-сервис
│   ├── logging/      # логирование с ротацией
│   └── monitoring/   # сбор CPU/RAM/GPU/температуры
├── tests/            # pytest unit и integration тесты
├── requirements.txt
├── README.md
└── .gitignore
```

## Статус разработки

- [x] **Этап 1.** Архитектура, Git, рабочее окружение
- [x] **Этап 2.** Видеопоток, FPS, восстановление соединения
- [ ] **Этап 3.** Baseline-детектор людей и транспорта (YOLOv8)
- [ ] **Этап 4.** Набор данных, разметка, первый эксперимент обучения
- [ ] **Этап 5.** Метрики, tracking, ROI, Event Logic
- [ ] **Этап 6.** Контроль средств индивидуальной защиты (PPE)
- [ ] **Этап 7.** Детекция дыма и огня, hard negatives
- [ ] **Этап 8.** Разлив, Event Engine, JSON, logging, evidence
- [ ] **Этап 9.** REST API, Edge AI, benchmark (ONNX / TensorRT)
- [ ] **Этап 10.** Системные испытания, отчёт, индивидуальная защита
