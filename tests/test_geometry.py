import pytest
from src.zones.geometry import point_in_polygon

def test_point_inside_polygon():
    polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert point_in_polygon((50, 50), polygon) is True

def test_point_outside_polygon():
    polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert point_in_polygon((150, 50), polygon) is False

def test_point_on_edge():
    polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert point_in_polygon((0, 50), polygon) is True