from src.events.event_engine import EventEngine
from src.tracking.tracker import Track

def test_event_engine_creates_event():
    # Полигон 100x100
    polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    engine = EventEngine(restricted_polygon=polygon, cooldown_sec=0.1)

    # Создаем трек человека, нижняя точка которого (50, 60) — внутри полигона
    person = Track(
        track_id=1, class_id=0, class_name="Person", confidence=0.9,
        x1=40, y1=40, x2=60, y2=60
    )

    # N=3, M=5. Первые 4 кадра событие не создается
    for _ in range(4):
        events = engine.process([person])
        assert len(events) == 0

    # На 5-м кадре должно появиться событие
    events = engine.process([person])
    assert len(events) == 1
    assert events[0].event_type == "person_in_restricted_zone"