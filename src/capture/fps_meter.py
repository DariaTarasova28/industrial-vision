import time
from collections import deque


class FPSMeter:
    """
    Скользящая оценка FPS по временным меткам последних N кадров.
    """

    def __init__(self, window: int = 30):
        self.times = deque(maxlen=window)

    def tick(self) -> float:
        """Вызывать после обработки каждого кадра. Возвращает текущий FPS."""
        now = time.perf_counter()
        self.times.append(now)
        if len(self.times) < 2:
            return 0.0
        dt = self.times[-1] - self.times[0]
        return (len(self.times) - 1) / dt if dt > 0 else 0.0