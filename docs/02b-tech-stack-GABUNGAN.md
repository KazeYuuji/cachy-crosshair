# 02b — Tech Stack GABUNGAN (Hybrid Universal) ⭐

> Menggabungkan PyQt6 + GTK4 + Tauri jadi 1 project universal — works di semua DE CachyOS

## Konsep: 1 Core + 3 Backend + Auto-Detect DE

Jangan pilih salah satu — pakai semua dengan **arsitektur modular**. User install 1 app, app otomatis pilih backend yang paling pas untuk DE yang sedang jalan.

```
Cachy Crosshair — Hybrid Architecture

┌─────────────────────────────────────────────────────────┐
│                    USER LAYER                           │
│  Preset JSON, Config, CLI, Tray, Hotkey                 │
│  ~/.config/cachy-crosshair/{config.json, presets/*.json}│
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 CORE (shared, 100% sama)                │
│  • preset schema (JSON)                                 │
│  • config manager (load/save)                           │
│  • painter logic (hitung koordinat crosshair)           │
│  • Bahasa: Python ATAU Rust (shared lib)                │
│  • Lokasi: core/                                        │
└──────┬──────────────┬──────────────┬────────────────────┘
       │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────────┐
│ BACKEND A   │ │ BACKEND B  │ │ BACKEND C    │
│ PyQt6       │ │ GTK4       │ │ Tauri v2     │
│ layer-shell-│ │ gtk-layer- │ │ WebKitGTK +  │
│ qt          │ │ shell      │ │ Canvas       │
│             │ │            │ │              │
│ Untuk: KDE  │ │ Hyprland/  │ │ Fallback /   │
│ Plasma      │ │ Sway/GNOME │ │ Universal /  │
│ (kamu now)  │ │ Wayland    │ │ X11 / Demo   │
│ Paling      │ │ Paling     │ │ UI paling    │
│ native &    │ │ ringan     │ │ modern       │
│ ringan      │ │ Hyprland   │ │ cross-plat   │
└──────┬──────┘ └─────┬──────┘ └────┬─────────┘
       │              │             │
       └──────────────┼─────────────┘
                      │
        ┌─────────────▼──────────────┐
        │   DETECTOR (runtime)       │
        │   XDG_CURRENT_DESKTOP      │
        │   XDG_SESSION_TYPE         │
        │   → auto pilih backend     │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │   SETTINGS UI (shared)     │
        │   Opsi hybrid:             │
        │   1. Tauri Web (utama)     │
        │   2. Qt/GTK native fallback│
        └────────────────────────────┘
```

## Cara Kerja Auto-Detect (1 binary, 3 mode)

```python
# src/launcher.py (atau core/detector.rs)
import os

def detect_backend():
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
    session = os.environ.get("XDG_SESSION_TYPE", "")
    wayland = os.environ.get("WAYLAND_DISPLAY", "")

    if "KDE" in desktop and wayland:
        return "qt"      # → PyQt6 + layer-shell-qt (kamu)
    elif any(x in desktop for x in ["Hyprland", "sway", "GNOME"]) and wayland:
        return "gtk"     # → GTK4 + gtk-layer-shell
    elif session == "x11":
        return "qt"      # atau gtk, keduanya works X11
    else:
        return "tauri"   # fallback universal

backend = detect_backend()
overlay = load_overlay(backend)  # factory
overlay.show()
```

User cukup: `cachy-crosshair` → otomatis benar. Mau force: `cachy-crosshair --backend gtk`.

## Struktur Monorepo Gabungan

```
crosshair-workflow/src/
├── core/                     # SHARED — 1x tulis, dipakai semua backend
│   ├── config.py             # JSON load/save (atau config.rs jika Rust)
│   ├── presets.py            # schema + validation
│   ├── painter.py            # hitung koordinat crosshair (pure logic)
│   └── detector.py           # auto-detect DE
│
├── backends/
│   ├── qt/                   # BACKEND A — KDE Plasma
│   │   ├── overlay.py        # PyQt6 + LayerShellQt.Window
│   │   ├── settings_qt.py    # QWidget settings (optional)
│   │   └── tray_qt.py
│   ├── gtk/                  # BACKEND B — Hyprland/Sway/GNOME
│   │   ├── overlay.py        # GTK4 + GtkLayerShell + Cairo
│   │   ├── settings_gtk.py
│   │   └── tray_gtk.py
│   └── tauri/                # BACKEND C — Universal / Web
│       ├── src-tauri/        # Rust backend Tauri
│       ├── src/              # Frontend HTML/CSS/JS + Canvas
│       │   ├── overlay.html  # Canvas crosshair
│       │   └── settings.html # Settings UI (dipakai semua backend juga!)
│       └── tauri.conf.json
│
├── shared/
│   ├── presets/              # *.json (dipakai semua)
│   │   ├── dot-red.json
│   │   ├── cross-green.json
│   │   └── ...
│   └── assets/               # icon, svg
│
├── launcher.py               # entry point: detect → load backend
└── cli.py                    # CLI shared
```

**Alternatif Rust Core** (lebih pro, tapi butuh Rust):
```
core/  → Rust lib (cargo) yang di-bind ke Python via PyO3 + ke Tauri via Rust native
```
Untuk MVP, **cukup Python core** — nanti bisa port ke Rust kalau mau AUR super ringan.

## Settings UI Gabungan (1 UI untuk semua backend)

Jangan bikin 3 settings berbeda. Buat **1 Tauri Web UI** yang dipakai semua backend:

- Tauri frontend (`settings.html` + Canvas preview) → generate `config.json`
- Backend Qt/GTK cukup baca `config.json` yang sama → overlay update

Jadi:
- Jika Tauri terinstall → settings web modern (color picker bagus, slider smooth)
- Jika tidak → fallback Qt `QColorDialog` / GTK `GtkColorChooser` (tetap jalan)

## Keuntungan Gabungan

| Aspek | Gabungan | Pilih 1 stack saja |
|-------|----------|---------------------|
| Support DE | KDE, Hyprland, Sway, GNOME, X11 — semua works | Hanya 1 DE optimal |
| Future-proof | Ganti DE (KDE → Hyprland) tetap works tanpa reinstall | Harus ganti app |
| AUR | 1 package `cachy-crosshair` support semua | 1 DE saja |
| Share preset | 1 format JSON, share ke teman beda DE tetap bisa | sama |
| Maintenance | Core 1x, backend 3x (tapi 70% logic shared) | lebih simpel |

## Kekurangan Gabungan (jujur)

| Kekurangan | Mitigasi |
|------------|----------|
| Dependencies lebih banyak: `python-pyqt6` + `gtk4` + `webkit2gtk` + `rust` | Buat PKGBUILD dengan `optdepends` — user KDE cukup install `qt`, Hyprland cukup `gtk`, Tauri optional |
| Build lebih berat (dev) | Dev pakai `venv` per backend, tidak wajib install semua sekaligus |
| Complexity +30% | Core shared 70%, backend cuma wrapper overlay → tidak 3x lipat |
| Binary size jika full Tauri + Qt | Pakai `feature flags` cargo / `extras_require` python — build minimal KDE cuma 20MB |

## Strategi Build — Optdepends (Arch style)

```bash
# PKGBUILD (konsep)
pkgname=cachy-crosshair
depends=('python')
optdepends=(
  'python-pyqt6: for KDE Plasma (recommended)'
  'layer-shell-qt: for KDE Wayland click-through'
  'gtk4: for Hyprland/Sway/GNOME'
  'gtk4-layer-shell: for Hyprland Wayland'
  'webkit2gtk-4.1: for Tauri web settings (optional)'
  'rust: to build Tauri backend (optional)'
)
# Runtime: cek yang terinstall, pakai yang ada
```

User KDE seperti kamu: `sudo pacman -S python-pyqt6 layer-shell-qt` → jalan Qt, tanpa perlu gtk/webkit.

## Roadmap Gabungan (revisi)

### Fase 1 — Core + Backend Qt (Minggu 1) — PRIORITAS KAMU
- [ ] `core/` (config, presets, painter)
- [ ] `backends/qt/overlay.py` (prototype yang sudah ada → modularize)
- [ ] `launcher.py` detector
- [ ] Test di KDE Wayland kamu

### Fase 2 — Tambah GTK (Minggu 2)
- [ ] `backends/gtk/overlay.py` (port painter ke Cairo)
- [ ] Test di Hyprland (VM atau sesi Hyprland)

### Fase 3 — Tauri Settings Universal (Minggu 3)
- [ ] `backends/tauri/src/settings.html` + canvas preview
- [ ] Tauri baca/tulis `config.json` yang sama
- [ ] Qt/GTK overlay subscribe perubahan config (file watcher `inotify`)

### Fase 4 — Polish & AUR (Minggu 4-5)
- [ ] PKGBUILD dengan optdepends
- [ ] CLI `--backend {qt,gtk,tauri,auto}`
- [ ] Icon + .desktop

## Perintah Dev Gabungan

```bash
# Dev KDE (kamu sekarang)
python src/launcher.py --backend qt
python src/launcher.py --backend qt --preset cross --color "#00FF00"

# Test Hyprland (nanti)
python src/launcher.py --backend gtk

# Test Tauri
cd src/backends/tauri && cargo tauri dev

# Auto (production)
python src/launcher.py  # → auto-detect KDE → qt
```

## Keputusan untuk Kamu

> **Hermes rekomendasikan**: Mulai **Fase 1 Qt dulu** (karena kamu KDE Wayland, biar cepat MVP), tapi struktur dari awal sudah `core/` + `backends/` gabungan — jadi Fase 2-3 tinggal tambah, tidak refactor ulang.

Mau Hermes langsung refactor `src/prototype_overlay.py` jadi struktur gabungan `core/` + `backends/qt/` + `launcher.py` sekarang?
Jawab: `gas gabungan` atau `gas Qt dulu` atau `buat struktur gabungan`.
