# Build Success — Cachy Crosshair 0.1.0 AppImage

> Built: 2026-09-03 16:21 CachyOS KDE Wayland

## Artifacts
```
dist/
├── appimagetool-x86_64.AppImage (15M, downloader)
├── cachy-crosshair.AppDir/ (AppDir, 257M uncompressed)
└── Cachy-Crosshair-0.1.0-x86_64.AppImage (82M, portable) ✅

Install:
~/.local/bin/cachy-crosshair.AppImage (82M, copy of above) ✅
~/.local/share/applications/cachy-crosshair.desktop ✅
~/.config/cachy-crosshair/presets/*.json (8 presets) ✅
```

## Tests Passed
- [x] PyQt6 6.11.0 via pip --user (no sudo needed)
- [x] QT_QPA_PLATFORM=offscreen → --help, live preview signal, painter compute
- [x] QT_QPA_PLATFORM=wayland → AppDir/AppRun --hidden PID alive 5s, tray warning only, overlay WindowDoesNotAcceptFocus correct
- [x] AppImage wayland --hidden + normal both PID alive, killed cleanly
- [x] AppImage --appimage-extract → squashfs-root valid
- [x] SettingsWindow 820x560, Preview 220x220, sliders live update overlay cfg

## How to Run (User)
```bash
# GUI + overlay (visible)
~/.local/bin/cachy-crosshair.AppImage
./dist/Cachy-Crosshair-0.1.0-x86_64.AppImage

# Tray only (autostart style)
~/.local/bin/cachy-crosshair.AppImage --hidden

# From project dev without AppImage
python src/main_gui.py
python src/main_gui.py --hidden
```

## Tray Usage
1. Run AppImage → overlay dot merah center muncul (click-through)
2. Tray icon → double-click atau klik kanan → Settings → ubah warna/size → preview live → Save & Apply
3. Tray → Toggle Overlay (hide/show)
4. Tray → Autostart (generate ~/.config/autostart/cachy-crosshair.desktop)
5. Game fullscreen → overlay tetap di atas (layer-shell overlay)

## Next
- Test live di game (CS2 / Minecraft / browser F11)
- Publish GitHub Releases: upload .AppImage
- AUR PKGBUILD Fase 4
