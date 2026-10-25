from collections import deque

class TemporalConfirm:
    """Подтверждает событие, если оно стабильно на протяжении N из M кадров."""
    def __init__(self, n: int = 3, m: int = 5):
        self.n = n
        self.window = deque(maxlen=m)

    def update(self, detected: bool) -> bool:
        self.window.append(bool(detected))
        return len(self.window) == self.window.maxlen and sum(self.window) >= self.n