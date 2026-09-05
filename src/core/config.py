"""
core/config.py — Shared config manager (JSON)
Dipakai semua backend, 1 file config
"""
import json, os
from pathlib import Path
from .painter import CrosshairConfig

CONFIG_DIR = Path.home() / ".config" / "cachy-crosshair"
CONFIG_FILE = CONFIG_DIR / "config.json"
PRESETS_DIR = CONFIG_DIR / "presets"

DEFAULT_CONFIG = CrosshairConfig()

def ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> CrosshairConfig:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return CrosshairConfig.from_dict(json.load(f))
        except Exception as e:
            print(f"[WARN] load config failed: {e}, pakai default")
    return CrosshairConfig()

def save_config(cfg: CrosshairConfig):
    ensure_dirs()
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg.to_dict(), f, indent=2)
    print(f"[OK] Config saved → {CONFIG_FILE}")

def list_presets():
    ensure_dirs()
    return [p.stem for p in PRESETS_DIR.glob("*.json")]

def load_preset(name: str) -> CrosshairConfig:
    p = PRESETS_DIR / f"{name}.json"
    with open(p) as f:
        return CrosshairConfig.from_dict(json.load(f))

def save_preset(name: str, cfg: CrosshairConfig):
    ensure_dirs()
    with open(PRESETS_DIR / f"{name}.json", "w") as f:
        json.dump(cfg.to_dict(), f, indent=2)
    print(f"[OK] Preset saved → {name}")

# Buat 8 presets default jika belum ada
DEFAULT_PRESETS = {
    "dot-red": {"type": "dot", "color": "#FF0000", "size": 6},
    "cross-green": {"type": "cross", "color": "#00FF00", "size": 12, "thickness": 2},
    "cross-dot-cyan": {"type": "cross_dot", "color": "#00FFFF", "size": 12},
    "circle-yellow": {"type": "circle", "color": "#FFFF00", "size": 20, "thickness": 2},
    "t-white": {"type": "t", "color": "#FFFFFF", "size": 14},
    "dot-small": {"type": "dot", "color": "#FF00FF", "size": 3},
    "cross-large": {"type": "cross", "color": "#FF8800", "size": 20, "thickness": 3, "gap": 6},
    "circle-cross-red": {"type": "circle_cross", "color": "#FF0000", "size": 24},
}

def ensure_default_presets():
    ensure_dirs()
    for name, data in DEFAULT_PRESETS.items():
        p = PRESETS_DIR / f"{name}.json"
        if not p.exists():
            cfg = CrosshairConfig(**data)
            save_preset(name, cfg)
