import cv2
import numpy as np
from src.inference.types import Detection

def bottom_center(det: Detection) -> tuple[int, int]:
    """Возвращает нижнюю центральную точку объекта (x, y)."""
    return ((det.x1 + det.x2) // 2, det.y2)

def point_in_polygon(point: tuple[int, int], polygon_px: list[tuple[int, int]]) -> bool:
    """Проверяет, находится ли точка внутри полигона."""
    contour = np.array(polygon_px, dtype=np.int32)
    return cv2.pointPolygonTest(contour, point, False) >= 0