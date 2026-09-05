# Cachy Crosshair 🎯

> **Crosshair overlay hybrid untuk CachyOS (KDE Wayland, Hyprland, X11)** — 1 core + 3 backends + AppImage

![CachyOS](https://img.shields.io/badge/CachyOS-Arch-1e90ff) ![KDE](https://img.shields.io/badge/KDE-Wayland-1d99f3) ![Qt6](https://img.shields.io/badge/Qt6-PyQt6-41cd52) ![License](https://img.shields.io/badge/license-MIT-green) ![AppImage](https://img.shields.io/badge/AppImage-82M-blue)

Crosshair overlay transparan, always-on-top, click-through untuk gaming FPS di CachyOS. Solusi native Linux pengganti Crosshair X Windows.

## ✨ Fitur
- **Overlay transparan** fullscreen, click-through (tidak block input game), center 1366x768
- **6 tipe**: dot, cross, cross+dot, circle, circle+cross, T (+ custom image planned)
- **Kustom**: warna picker, size 2-60px, thickness 1-10, opacity 10-100%, gap, outline, center dot, offset X/Y
- **GUI Settings 820x560** live preview 220x220 → slider langsung update overlay
- **Hybrid**: auto-detect DE → Qt (KDE) / GTK (Hyprland/Sway) / Tauri (universal)
- **Tray**: toggle, settings, autostart `~/.config/autostart/`
- **Presets JSON** `~/.config/cachy-crosshair/presets/*.json` — 8 bawaan, import/export
- **AppImage 82M** portable, 1 file

## 🖥️ System
- CachyOS Linux (Arch rolling), KDE Plasma 6.7.4 Wayland `wayland-0` ✅ tested
- Juga support Hyprland, Sway, GNOME, X11

## 📦 Install (AppImage - Recommended)

### Download (GitHub Releases)
```bash
wget https://github.com/KazeYuuji/cachy-crosshair/releases/latest/download/Cachy-Crosshair-0.1.0-x86_64.AppImage
chmod +x Cachy-Crosshair-*.AppImage
./Cachy-Crosshair-*.AppImage              # GUI + overlay
./Cachy-Crosshair-*.AppImage --hidden     # tray only
```

### Install user
```bash
mkdir -p ~/.local/bin
cp Cachy-Crosshair-*.AppImage ~/.local/bin/cachy-crosshair.AppImage
# autostart via tray → Autostart checkbox, atau manual:
mkdir -p ~/.config/autostart
cp packaging/cachy-crosshair.desktop ~/.config/autostart/
sed -i "s|Exec=cachy-crosshair|Exec=$HOME/.local/bin/cachy-crosshair.AppImage|" ~/.config/autostart/cachy-crosshair.desktop
```

### Dari source (dev)
```bash
git clone https://github.com/KazeYuuji/cachy-crosshair
cd cachy-crosshair
pip install --user PyQt6  # atau sudo pacman -S python-pyqt6 layer-shell-qt
python src/main_gui.py
python src/main_gui.py --hidden
```

## 🎮 Penggunaan
1. Run AppImage → overlay dot merah center muncul (click-through)
2. Tray → double-click / klik kanan → Settings → ubah warna/size → preview live → Save & Apply
3. Tray → Toggle Overlay (hide/show), Autostart
4. Game fullscreen (CS2, Minecraft, browser F11) → overlay tetap di atas

## 🛠️ Build AppImage
```bash
# deps
sudo pacman -S python-pyqt6 layer-shell-qt librsvg  # cepat, kecil
# atau portable: sudo pacman -S python-pip  # bundle PyQt6 50M

bash packaging/appimage/build-appimage.sh
# → dist/Cachy-Crosshair-0.1.0-x86_64.AppImage (82M)
```

## 📁 Struktur
```
cachy-crosshair/
├── src/
│   ├── core/{painter,config,detector}.py  # shared logic
│   ├── backends/qt/{overlay,settings}.py  # KDE
│   ├── backends/gtk/overlay.py            # Hyprland (Fase 2)
│   ├── backends/tauri/                    # universal (Fase 3)
│   ├── main_gui.py                        # GUI + tray + autostart
│   └── launcher.py                        # CLI
├── packaging/
│   ├── cachy-crosshair.desktop
│   ├── icons/cachy-crosshair.svg
│   └── appimage/{AppRun,build-appimage.sh}
└── docs/
```

## 🔧 Troubleshooting
- `PyQt6 tidak ditemukan` → `pip install --user PyQt6` atau `sudo pacman -S python-pyqt6`
- Crosshair tidak muncul → coba `CACHY_CROSSHAIR_DEBUG=1 ./AppImage` (layar merah tints), atau `QT_QPA_PLATFORM=xcb ./AppImage`
- Tray tidak ada → `QSystemTrayIcon::setVisible: No Icon` → install `libappindicator`

## Workflow
Docs lengkap di `docs/` — PRD, tech-stack Wayland, roadmap. Original workflow persisten di `crosshair-workflow/` (private).
