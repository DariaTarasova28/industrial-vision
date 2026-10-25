import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.tracking.tracker import Track
from src.zones.geometry import point_in_polygon
from src.events.temporal import TemporalConfirm
from src.events.cooldown import CooldownManager

logger = logging.getLogger(__name__)

@dataclass
class Event:
    event_id: str
    event_type: str
    timestamp: str
    camera_id: str
    confidence: float
    track_id: int
    coordinates: dict

class EventEngine:
    def __init__(self, restricted_polygon: list[tuple[int, int]], cooldown_sec: float = 5.0):
        self.polygon = restricted_polygon
        self.cooldown = CooldownManager(cooldown_sec)
        # Создаем отдельный TemporalConfirm для каждого трека
        self.temporal_states: dict[int, TemporalConfirm] = {}

    def process(self, tracks: list[Track], camera_id: str = "cam_01") -> list[Event]:
        events = []
        for track in tracks:
            # Нас интересуют только люди
            if track.class_name != "Person":
                continue

            # Инициализируем состояние для нового трека
            if track.track_id not in self.temporal_states:
                self.temporal_states[track.track_id] = TemporalConfirm(n=3, m=5)

            # Проверяем, находится ли человек в зоне
            is_in_zone = point_in_polygon(track.bottom_center, self.polygon)

            # Подтверждаем по времени
            if self.temporal_states[track.track_id].update(is_in_zone):
                # Защита от спама
                event_key = f"person_in_zone_{track.track_id}"
                if self.cooldown.is_allowed(event_key):
                    events.append(Event(
                        event_id=str(uuid4()),
                        event_type="person_in_restricted_zone",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        camera_id=camera_id,
                        confidence=track.confidence,
                        track_id=track.track_id,
                        coordinates={"x": track.bottom_center[0], "y": track.bottom_center[1]}
                    ))
                    logger.warning("EVENT: %s (ID: %d)", "person_in_restricted_zone", track.track_id)
        return events