# 02 — Tech Stack & Arsitektur CachyOS

> Stack khusus CachyOS KDE Wayland — Arch rolling, bun 1.4.0

## 2.1 Tantangan Utama: Overlay di Wayland

| Aspek | X11 (legacy) | Wayland KDE (kamu sekarang) |
|-------|--------------|------------------------------|
| Transparent overlay | Mudah: `XShape`, `Qt::WA_TranslucentBackground` + `override_redirect` | Lebih ketat: compositor control |
| Click-through | `Xfixes` input shape kosong | `layer-shell` + `inputRegion` kosong atau `Qt::WindowTransparentForInput` (butuh compositor support) |
| Always on top | `WM_HINTS` `alwaysOnTop` | `layer-shell` layer `overlay` / `top`, atau `KWin::setOnAllDesktops` |
| Deteksi session | `DISPLAY` | `XDG_SESSION_TYPE=wayland`, `WAYLAND_DISPLAY` |
| KWin KDE | Works | Butuh `layer-shell-qt` atau `qwindow` flags khusus |

**Kesimpulan**: Harus pakai **layer-shell** untuk click-through sempurna di Wayland. KDE KWin 6.x sudah support `wlr-layer-shell` via `layer-shell-qt`.

## 2.2 Opsi Stack (Rekomendasi 3)

### Opsi A — PyQt6 + layer-shell-qt ⭐ (REKOMENDASI untuk CachyOS KDE)
**Stack**: Python 3.12 + PyQt6 / PySide6 + `layer-shell-qt` + `python-xlib` fallback

**Pros**:
- Native KDE, Breeze theme auto
- Paling ringan (20-30MB RAM)
- AUR package gampang (`python-pyqt6`, `layer-shell-qt`)
- Click-through proven di KDE Wayland (pakai `LayerShellQt.Window`)
- Tray via `QSystemTrayIcon` native
- Tidak butuh WebView / browser engine

**Cons**:
- Python packaging agak ribet (butuh `pipx` / `venv`)
- Custom drawing pakai QPainter (perlu coding manual untuk crosshair shapes)

**Arsitektur**:
```
src/
├── main.py              # QApp + tray + hotkey
├── overlay/
│   ├── wayland.py       # LayerShellQt.Window overlay
│   ├── x11.py           # fallback X11
│   └── painter.py       # QPainter crosshair renderer
├── editor/
│   └── settings.py      # QWidget settings window
└── config.py            # JSON load/save
```

**Snippet overlay (Qt)**:
```python
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen

class CrosshairOverlay(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint 
                         | Qt.WindowType.WindowStaysOnTopHint
                         | Qt.WindowType.Tool
                         | Qt.WindowType.WindowTransparentForInput
                         | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        # Layer-shell untuk KDE Wayland
        try:
            import LayerShellQt
            LayerShellQt.Window.get(self.windowHandle()).setLayer(LayerShellQt.Window.LayerOverlay)
            LayerShellQt.Window.get(self.windowHandle()).setKeyboardInteractivity(LayerShellQt.Window.KeyboardInteractivityNone)
        except: pass
        self.showFullScreen()
```

### Opsi B — Tauri v2 (Rust + WebKitGTK) 🚀 (REKOMENDASI jika mau Web Tech)
**Stack**: Rust + Tauri v2 + HTML/CSS/Canvas + `webkit2gtk-4.1`

**Pros**:
- UI modern (HTML/CSS, color picker bagus, preview canvas)
- Binary kecil Rust (~5MB), RAM ~40-60MB (lebih kecil dari Electron 150MB)
- Transparent overlay support via `tauri.conf.json`:
```json
{
  "windows": [{
    "label": "overlay",
    "transparent": true,
    "decorations": false,
    "alwaysOnTop": true,
    "skipTaskbar": true,
    "resizable": false,
    "fullscreen": true
  }]
}
```
- Click-through via `appWindow.setIgnoreCursorEvents(true)` (Tauri API)
- Cross-platform (Linux/Windows/Mac)

**Cons**:
- Butuh Rust toolchain (`rustup`, `cargo`)
- WebKitGTK di CachyOS kadang butuh `webkit2gtk-4.1` + `javascriptcoregtk`
- Layer-shell di Tauri masih perlu `gtk-layer-shell` manual untuk Wayland sempurna

**Arsitektur**:
```
src-tauri/          # Rust backend
src/                # Frontend Svelte/React/Vanilla
  ├── overlay.html  # Canvas crosshair
  └── settings.html # Settings UI
```

### Opsi C — GTK4 + GtkLayerShell (untuk Hyprland/GNOME)
**Stack**: Python + GTK4 + `gtk4-layer-shell` + Cairo

**Pros**:
- Best untuk Hyprland/Sway (gtk-layer-shell proven)
- Libadwaita looks bagus

**Cons**:
- Di KDE kurang native vs Qt (tray & theme agak mismatch)
- Butuh `gtk4-layer-shell` AUR

### Opsi D — Electron (tidak direkomendasikan)
- Berat, 150MB+ RAM, startup lambat — skip untuk CachyOS yang ngebut.

## 2.3 Rekomendasi Final Hermes

| Kriteria | Pilih |
|----------|-------|
| **Mau paling native KDE, ringan, AUR gampang** | **Opsi A — PyQt6** ⭐ |
| **Mau UI web modern, preview canvas fleksibel** | **Opsi B — Tauri** |
| **Pake Hyprland nanti** | **Opsi C — GTK4** |

> **Saran Hermes (default)**: Mulai dengan **Opsi A PyQt6** untuk MVP (cepat jadi + Wayland click-through paling proven di KDE). Jika kamu suka web stack, kita bisa port ke Tauri nanti — logic crosshair sama.

## 2.4 Dependencies CachyOS

```bash
# Cek yang sudah terinstall
pacman -Q | grep -E "qt6|pyqt|webkit|gtk|layer-shell"

# Untuk Opsi A (PyQt6)
sudo pacman -S python-pyqt6 python-pyside6 layer-shell-qt qt6-base

# Untuk Opsi B (Tauri)
sudo pacman -S webkit2gtk-4.1 base-devel curl wget file openssl appmenu-gtk-module gtk3 libappindicator-gtk3 librsvg
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install tauri-cli

# Untuk Opsi C (GTK4)
sudo pacman -S gtk4 gtk4-layer-shell python-gobject cairo
```

## 2.5 Hotkey Global (Wayland tricky)

| DE | Cara |
|----|------|
| KDE Wayland | `KGlobalAccel` + `QAction` shortcut, atau `khotkeys` D-Bus. Fallback: `ydotool` / `evdev` (butuh permission) |
| X11 fallback | `pynput`, `keyboard` lib, atau `xbindkeys` |
| Universal | Tauri `globalShortcut` plugin (pakai `libxdo` + Wayland portal) |

Untuk MVP: pakai `QShortcut` + tray toggle dulu, global hotkey stage 2 pakai `kglobalaccel` + portal `org.freedesktop.portal.GlobalShortcuts` (baru di Plasma 6).

## 2.6 Config & Packaging

```
Config: ~/.config/cachy-crosshair/
  ├── config.json
  └── presets/*.json

Autostart: ~/.config/autostart/cachy-crosshair.desktop
AUR: PKGBUILD → cachy-crosshair-git
Icon: /usr/share/icons/hicolor/scalable/apps/cachy-crosshair.svg
Desktop: /usr/share/applications/cachy-crosshair.desktop
```

## 2.7 Keputusan yang Perlu Kamu Buat
- [ ] Pilih stack: **A PyQt6** vs **B Tauri** vs **C GTK4**?
- [ ] Nama app final: `cachy-crosshair`? `crosshair-cachy`? `kcrosshair`?
- [ ] License: MIT?
- [ ] Bahasa settings: Indonesia / English / bilingual?

> Jawab: "pilih A" / "pilih B" atau "kamu putuskan A" → Hermes langsung scaffold boilerplate di `src/`.
