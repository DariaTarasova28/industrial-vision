from __future__ import annotations
import time
import cv2
from typing import Optional, Union


class VideoSource:
    """
    Источник видео: файл, USB-камера (int) или RTSP-поток (str).
    Умеет переподключаться при обрыве.
    """

    def __init__(self, source: Union[str, int], reconnect_sec: float = 2.0):
        self.source = source
        self.reconnect_sec = reconnect_sec
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            # Первая попытка не удалась — ждём и пробуем снова один раз
            time.sleep(self.reconnect_sec)
            self.cap.release()
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                raise RuntimeError(
                    f"Cannot open video source after retry: {self.source}"
                )

    def read(self):
        """
        Читает кадр. При неудаче пытается переподключиться.
        Возвращает кадр (numpy.ndarray). При полной неудаче — RuntimeError.
        """
        if self.cap is None or not self.cap.isOpened():
            self.open()

        ok, frame = self.cap.read()
        if ok and frame is not None:
            return frame

        # Поток оборвался — пробуем восстановить
        time.sleep(self.reconnect_sec)
        self.open()
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Video stream is unavailable after reconnect")
        return frame

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None