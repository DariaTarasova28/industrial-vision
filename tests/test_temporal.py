import pytest
from src.events.temporal import TemporalConfirm

def test_temporal_confirm_positive():
    tc = TemporalConfirm(n=3, m=5)
    # Заполняем окно 4 раза True (окно еще не полное)
    for _ in range(4):
        assert tc.update(True) is False
    # 5-й раз: окно заполнено, сумма 5 >= 3 -> True
    assert tc.update(True) is True

def test_temporal_confirm_negative():
    tc = TemporalConfirm(n=3, m=5)
    # Заполняем окно 5 раз False
    for _ in range(4):
        assert tc.update(False) is False
    # 5-й раз: окно заполнено, сумма 0 < 3 -> False
    assert tc.update(False) is False

def test_temporal_confirm_mixed():
    tc = TemporalConfirm(n=3, m=5)
    # 3 True и 2 False (сумма 3)
    results = [tc.update(v) for v in [True, True, True, False, False]]
    # На 5-м обновлении окно заполнено, сумма 3 >= 3 -> True
    assert results[-1] is True