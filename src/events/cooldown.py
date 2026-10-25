import time

class CooldownManager:
    """Отвечает за то, чтобы одно и то же событие не спамилось слишком часто."""
    def __init__(self, cooldown_sec: float = 5.0):
        self.cooldown_sec = cooldown_sec
        self.last_events: dict[str, float] = {}

    def is_allowed(self, event_key: str) -> bool:
        now = time.time()
        last_time = self.last_events.get(event_key, 0)
        if now - last_time >= self.cooldown_sec:
            self.last_events[event_key] = now
            return True
        return False