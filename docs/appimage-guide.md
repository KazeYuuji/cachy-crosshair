# Guide Lengkap — AppImage + GUI Cachy Crosshair

## Apa yang sudah dibuat

1. **GUI Settings** (`src/backends/qt/settings.py`):
   - Window 820x560, Breeze style, 2 panel (kiri preview, kanan controls)
   - Preview canvas 220x220 realtime (grid + crosshair)
   - Controls: type, warna, color picker cepat 8 warna, outline, slider size/thickness/gap/opacity/dot, offset X/Y, preset save/export/import, reset, save & apply
   - Live update: drag slider → overlay langsung repaint

2. **Main GUI** (`src/main_gui.py`):
   - Overlay transparan fullscreen + Settings window + Tray icon
   - Tray: Settings (klik), Toggle Overlay, Autostart toggle, Quit
   - Autostart: generate `~/.config/autostart/cachy-crosshair.desktop` otomatis
   - Arg: `--hidden` untuk start tray only

3. **AppImage**:
   - `packaging/cachy-crosshair.desktop` + `icons/cachy-crosshair.svg` (512px, biru CachyOS + target)
   - `packaging/appimage/AppRun` (handle AppImage + fallback)
   - `packaging/appimage/build-appimage.sh` (build via appimagetool, auto download)

## Cara Build AppImage di CachyOS

### Opsi A — Cepat (pakai system PyQt6, AppImage ringan, butuh host punya python-pyqt6)
```bash
sudo pacman -S python-pyqt6 layer-shell-qt librsvg
cd crosshair-workflow
bash packaging/appimage/build-appimage.sh
# → dist/Cachy-Crosshair-0.1.0-x86_64.AppImage (kecil, ~5-10MB)
# Note: di PC lain yang tidak ada python-pyqt6, akan error — untuk share, pakai Opsi B
```

### Opsi B — Portable (bundle PyQt6 via pip, AppImage jalan di semua distro)
```bash
sudo pacman -S python-pip
# pip akan bundle PyQt6 ke AppDir saat build
bash packaging/appimage/build-appimage.sh
# → AppImage ~40-60MB, portable ke Ubuntu/Fedora/Arch tanpa deps
```

### Test
```bash
chmod +x dist/Cachy-Crosshair-*.AppImage
./dist/Cachy-Crosshair-*.AppImage              # muncur overlay + tray
# klik tray → Settings → ubah warna/size → preview live
```

## Screenshot Flow GUI
```
Tray icon → klik → Settings Window
┌──────────────────┬────────────────────────────┐
│ Preview 220x220  │ Type, Color, Outline,      │
│ grid + crosshair │ Sliders live, Offset,      │
│ 8 warna cepat    │ Preset combo, Save/Export, │
│ Preset save      │ Reset, Save & Apply        │
└──────────────────┴────────────────────────────┘
         ↕ live signal
Overlay fullscreen transparan (center, click-through)
```

## Next: Jika mau publish
- AppImage: upload ke GitHub Releases → user download 1 file
- AUR: buat PKGBUILD (Fase 4) → `yay -S cachy-crosshair`

## Dev tanpa AppImage (lebih cepat iterate)
```bash
# Tanpa build, langsung run GUI
python src/main_gui.py
python src/main_gui.py --hidden
```
