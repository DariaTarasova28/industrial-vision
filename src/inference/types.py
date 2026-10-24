from dataclasses import dataclass


@dataclass
class Detection:
    """
    Единый формат детекции. Не зависит от конкретной библиотеки.
    Координаты в пикселях изображения: (x1, y1) — левый верхний угол,
    (x2, y2) — правый нижний.
    """
    class_id: int
    class_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def center(self) -> tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    @property
    def bottom_center(self) -> tuple[int, int]:
        return ((self.x1 + self.x2) // 2, self.y2)