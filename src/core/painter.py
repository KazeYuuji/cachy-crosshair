"""
core/painter.py — Shared logic hitung koordinat crosshair
Dipakai semua backend (Qt, GTK, Tauri) — pure python, no UI deps
"""
from dataclasses import dataclass
from typing import Literal

CrosshairType = Literal["dot", "cross", "cross_dot", "circle", "circle_cross", "t"]

@dataclass
class CrosshairConfig:
    type: CrosshairType = "cross_dot"
    color: str = "#FF0000"
    size: int = 18          # panjang garis / diameter circle/dot
    thickness: int = 2
    opacity: float = 0.9
    gap: int = 4            # jarak dari center
    outline: bool = True
    outline_color: str = "#000000"
    outline_thickness: int = 1
    center_dot_size: int = 6
    offset_x: int = 0
    offset_y: int = 0

    def to_dict(self): return self.__dict__
    @classmethod
    def from_dict(cls, d): return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

def compute_cross_lines(cx: int, cy: int, cfg: CrosshairConfig):
    """Return list of lines (x1,y1,x2,y2) untuk cross. Dipakai Qt QPainter, Cairo, Canvas."""
    s, g = cfg.size, cfg.gap
    return [
        (cx - s - g, cy, cx - g, cy),  # left
        (cx + g, cy, cx + g + s, cy),  # right
        (cx, cy - s - g, cx, cy - g),  # top
        (cx, cy + g, cx, cy + g + s),  # bottom
    ]

def compute_circle(cx: int, cy: int, cfg: CrosshairConfig):
    """Return (x, y, w, h) untuk circle"""
    return (cx - cfg.size // 2, cy - cfg.size // 2, cfg.size, cfg.size)

def compute_dot(cx: int, cy: int, cfg: CrosshairConfig):
    d = cfg.center_dot_size if cfg.type == "cross_dot" else cfg.size
    return (cx - d // 2, cy - d // 2, d, d)
