# Research — Wayland vs X11 Overlay di CachyOS KDE

## Ringkasan
Kamu di Wayland (`XDG_SESSION_TYPE=wayland`, KDE KWin). Overlay transparan di Wayland tidak bisa pakai trik X11 lama.

## Cara Overlay Click-Through di Wayland

### 1. Layer Shell (Recommended)
- Protokol `wlr-layer-shell-unstable-v1`
- Window ditempatkan di layer `overlay` / `top` oleh compositor
- `inputRegion` dikosongkan → click-through
- Implementasi:
  - **Qt**: `layer-shell-qt` → `LayerShellQt.Window.setLayer(Overlay)`
  - **GTK**: `gtk4-layer-shell` → `gtk_layer_init_for_window()`
  - **Tauri**: perlu patch `gtk-layer-shell` manual atau Tauri plugin

### 2. Qt Flags Fallback (Coba dulu, kadang works di KWin 6)
```python
Qt.WindowTransparentForInput | Qt.WA_TransparentForMouseEvents
+ WA_TranslucentBackground + FramelessWindowHint + WindowStaysOnTopHint + Tool
```
Di KWin 6.2+ flag ini sudah diteruskan ke compositor sebagai inputRegion kosong.

### 3. XWayland (Jangan)
- Jangan paksa XWayland untuk overlay — tidak click-through di Wayland native game.

## Test Plan di CachyOS Kamu
```bash
# 1. Cek KWin version
kwin_wayland --version
plasmashell --version

# 2. Cek layer-shell support
qdbus org.kde.KWin /KWin supportInformation | grep layer

# 3. Test overlay minimal (akan dibuat di src/prototype.py)
python src/prototype_overlay.py
# Expected: fullscreen transparan dengan dot merah di center, bisa klik tembus ke window di belakang
```

## Reference
- layer-shell-qt docs: https://invent.kde.org/plasma/layer-shell-qt
- gtk-layer-shell: https://github.com/wmww/gtk-layer-shell
- KWin Wayland inputRegion: https://wayland-book.com
