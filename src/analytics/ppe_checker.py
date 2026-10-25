import logging
from src.tracking.tracker import Track
from src.events.temporal import TemporalConfirm
from src.events.cooldown import CooldownManager  # <--- ДОБАВИЛИ ИМПОРТ

logger = logging.getLogger(__name__)

def is_inside_or_intersect(inner_box, outer_box) -> bool:
    """Проверяет, пересекаются ли две рамки (bbox)."""
    x1 = max(inner_box.x1, outer_box.x1)
    y1 = max(inner_box.y1, outer_box.y1)
    x2 = min(inner_box.x2, outer_box.x2)
    y2 = min(inner_box.y2, outer_box.y2)
    return x1 < x2 and y1 < y2

class PPEChecker:
    """Аналитика контроля СИЗ."""
    def __init__(self):
        self.temporal_states = {}
        # Добавляем кулдаун на 10 секунд, чтобы не спамить событиями по одному человеку
        self.cooldown = CooldownManager(cooldown_sec=10.0)

    def check_tracks(self, tracks: list[Track]) -> list[dict]:
        violations = []
        
        persons = [t for t in tracks if t.class_name == "Person"]
        no_helmets = [t for t in tracks if t.class_name == "no_helmet"]

        for person in persons:
            if person.track_id not in self.temporal_states:
                self.temporal_states[person.track_id] = {
                    "helmet_missing": TemporalConfirm(n=3, m=5)
                }
            
            states = self.temporal_states[person.track_id]

            has_violation = False
            for nh in no_helmets:
                if is_inside_or_intersect(nh, person):
                    has_violation = True
                    break
            
            # Если N из M подтвердилось, проверяем кулдаун
            if states["helmet_missing"].update(has_violation):
                event_key = f"{person.track_id}_helmet_missing"
                if self.cooldown.is_allowed(event_key):
                    violations.append({
                        "type": "ppe_helmet_missing",
                        "track": person
                    })
            
        return violations