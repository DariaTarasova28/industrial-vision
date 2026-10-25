import os
import json
import glob
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Industrial Vision API")

EVENTS_DIR = "events"

def get_all_events():
    """Собирает все event.json из папки events/"""
    events = []
    # Ищем все event.json во всех подпапках (годы/месяцы/дни)
    search_pattern = os.path.join(EVENTS_DIR, "**", "event.json")
    for path in glob.glob(search_pattern, recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            events.append(json.load(f))
    # Сортируем по времени (новые сначала)
    events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return events

@app.get("/health")
def health():
    return {"status": "ok", "service": "vision-api"}

@app.get("/status")
def status():
    # В реальной системе мы бы брали это из мониторинга, а пока заглушка
    return {
        "camera": "connected",
        "fps": 15.0,
        "model_ppe": "loaded (yolov8n_ppe_v2)",
        "model_fire": "loaded (yolov8n_dfire)"
    }

@app.get("/events")
def events(limit: int = 10):
    """Возвращает последние N событий."""
    all_events = get_all_events()
    return all_events[:limit]

@app.get("/events/{event_id}")
def event_by_id(event_id: str):
    """Ищет конкретное событие по ID."""
    all_events = get_all_events()
    for e in all_events:
        if e.get("event_id") == event_id:
            return e
    raise HTTPException(status_code=404, detail="Event not found")

@app.get("/cameras")
def cameras():
    return [{"camera_id": "cam_01", "status": "connected"}]