# Backend C — Tauri v2 (Universal)

## Status: Fase 3 (placeholder)

Folder ini akan berisi Tauri app untuk:
- Overlay fallback (jika Qt/GTK tidak ada)
- Settings UI web modern (dipakai semua backend)

## Scaffold nanti (Fase 3)
```bash
cd src/backends/tauri
cargo create-tauri-app --template vanilla
# atau
npm create tauri-app@latest
```

## Kenapa Tauri di hybrid?
- Settings UI 1x (HTML/CSS/Canvas) dipakai Qt/GTK juga — mereka baca config.json yang sama
- Tidak wajib install untuk KDE user — optdepends
- Fallback jika tidak ada layer-shell-qt / gtk-layer-shell

## Config shared
Tauri backend baca/tulis `~/.config/cachy-crosshair/config.json` sama seperti Qt/GTK.
File watcher (notify) → Qt/GTK auto-reload saat Tauri ubah config.
