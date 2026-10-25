import os
import json
import cv2
from src.events.event_engine import Event

class EventStorage:
    def __init__(self, base_dir: str = "events"):
        self.base_dir = base_dir

    def save_event(self, event: Event, frame) -> str:
        date_str = event.timestamp[:10].replace("-", "/")
        event_dir = os.path.join(self.base_dir, date_str, event.event_id)
        os.makedirs(event_dir, exist_ok=True)

        snapshot_path = os.path.join(event_dir, "snapshot.jpg")
        cv2.imwrite(snapshot_path, frame)
        event.snapshot = snapshot_path.replace("\\", "/")

        json_path = os.path.join(event_dir, "event.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(event.__dict__, f, indent=2, ensure_ascii=False)

        return event_dir