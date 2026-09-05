# TODO — Crosshair HYBRID + AppImage

## 🔥 Sekarang — DONE ✅
- [x] Core + launcher hybrid ✅
- [x] GUI Settings (preview live) ✅
- [x] main_gui.py (tray+autostart) ✅
- [x] AppImage structure (AppRun, build script, icon) ✅
- [x] **Install deps** via pip --user PyQt6 6.11.0 (tanpa sudo) ✅
- [x] **Test GUI live** (wayland hidden/normal PID alive) ✅
- [x] **Build AppImage** 82M + test --help + wayland ✅
- [x] **Installed** ~/.local/bin/cachy-crosshair.AppImage ✅

## 📋 Backlog
- [ ] Test click-through Wayland (Firefox F11 fullscreen)
- [ ] Implement GTK backend Fase 2 (Hyprland)
- [ ] Scaffold Tauri Fase 3 (web settings)
- [ ] Publish GitHub + AUR

## ✅ Done
- [x] 2026-09-03: Workflow standard + hybrid monorepo + detector auto=qt
- [x] 2026-09-03: 8 presets di ~/.config/cachy-crosshair/presets/
- [x] 2026-09-03: GUI Settings 16KB + main_gui.py + icon svg + AppImage build script (py_compile ✅)
- [x] 2026-09-03 16:21: AppImage 82M built + installed + wayland tests PASS

## Notes
- Tanpa python-pyqt6, `python src/main_gui.py` akan error ModuleNotFound — install dulu.
- Build script auto-download appimagetool (continuous) dari GitHub.

---
*Bil "Hermes, install deps" untuk guide sudo.*
