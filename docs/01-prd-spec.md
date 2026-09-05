# 01 — PRD Spec Aplikasi Crosshair CachyOS

> Product Requirements Document — CachyOS KDE Wayland Gaming Overlay

## 1. Ringkasan Produk
**Nama kerja**: `cachy-crosshair` / `hypr-cross` (final tergantung branding)
**Tujuan**: Aplikasi overlay crosshair transparan, always-on-top, click-through untuk gaming FPS di CachyOS. Solusi native Linux yang ringan, tidak seperti Windows Crosshair X yang tidak ada di Linux.

**Target user**:
- Gamer FPS CachyOS/Arch (Valorant via Wine, CS2 native, Apex, Overwatch, Fortnite)
- User hip-fire / no-ADS, butuh crosshair center statis
- Streamer / casual yang mau custom crosshair tanpa monitor feature

## 2. Problem Statement
- Linux tidak punya app crosshair mainstream (Windows punya Crosshair X, Custom Desktop Logo, dll)
- Solusi existing Linux: `Crossover` (game), `Custom HUD` manual, `GOverlay` — tidak fokus crosshair
- Di Wayland, overlay transparan lebih sulit (X11 `xprop` tidak works)
- Monitor crosshair (hardware) tidak customizable & terbatas

## 3. User Stories
| ID | Story | Prioritas |
|----|-------|-----------|
| US-01 | Sebagai gamer, saya bisa toggle crosshair ON/OFF dengan hotkey global (mis. `Ctrl+Alt+X`) | P0 |
| US-02 | Saya bisa pilih preset: dot, cross, circle, T, cross+dot, custom image | P0 |
| US-03 | Saya bisa atur warna (color picker), size, thickness, opacity, outline | P0 |
| US-04 | Crosshair selalu di center layar, stay-on-top, click-through (tidak block input game) | P0 |
| US-05 | Settings auto-save & auto-start di boot | P1 |
| US-06 | Saya bisa atur offset X/Y (untuk multi-monitor / aim tidak center) | P1 |
| US-07 | Saya bisa atur hotkey custom | P1 |
| US-08 | Tray icon di system tray KDE untuk quick toggle | P1 |
| US-09 | Multi-monitor: pilih monitor target | P2 |
| US-10 | Import/export preset JSON, share ke teman | P2 |
| US-11 | Opacity auto-adjust saat ADS / hide saat menu (opsional) | P2 |
| US-12 | CLI: `cachy-crosshair --preset dot --color red --toggle` | P2 |

## 4. Functional Requirements

### 4.1 Overlay Engine
- [ ] Window transparent `RGBA`, frameless, always-on-top, fullscreen (cover semua layar)
- [ ] Click-through: `inputRegion` kosong / `Qt::WindowTransparentForInput` / `layer-shell` keyboardInteractivity none
- [ ] Render crosshair di center (calc `screen.geometry().center()`)
- [ ] Support Wayland + fallback X11 (deteksi `XDG_SESSION_TYPE`)
- [ ] Tidak muncul di taskbar / alt-tab
- [ ] Hide saat screen lock / logout

### 4.2 Crosshair Types
- Dot (filled circle)
- Cross (2 garis)
- Cross + Dot
- Circle (outline)
- Circle + Cross
- T-shape
- Custom image (PNG/SVG, user upload)
- Future: animated (pulsating)

### 4.3 Customization
- Color: HEX picker + preset (red, green, cyan, yellow, white, magenta)
- Size: 2 - 100 px (slider)
- Thickness: 1 - 10 px
- Opacity: 10% - 100%
- Outline: toggle + outline color + outline thickness (1-3px)
- Gap: jarak center (untuk cross)
- Center dot: toggle + size
- Shadow / glow (opsional)

### 4.4 Presets
- Simpan di `~/.config/cachy-crosshair/presets/*.json`
- Default presets: 8 bawaan
- User preset unlimited
- Contoh JSON:
```json
{
  "name": "Valorant Red Dot",
  "type": "dot",
  "color": "#FF0000",
  "size": 4,
  "opacity": 0.9,
  "outline": true,
  "outlineColor": "#000000",
  "outlineThickness": 1
}
```

### 4.5 Controls
- Global hotkey: default `Ctrl+Alt+C` (toggle), `Ctrl+Alt+Arrow` (adjust offset) — configurable via `kglobalaccel` / `xbindkeys` fallback
- System tray: icon + menu (Toggle, Settings, Quit)
- Settings window: GUI untuk edit semua param, live preview
- CLI: untuk scripting / autostart

### 4.6 Persistence & Autostart
- Config: `~/.config/cachy-crosshair/config.json`
- Autostart: `~/.config/autostart/cachy-crosshair.desktop` (XDG)
- D-Bus service? (optional untuk KDE integration)

## 5. Non-Functional Requirements
- **Ringan**: < 50 MB RAM, < 1% CPU idle, startup < 500ms
- **No lag**: render 60fps, tidak drop FPS game
- **Native KDE**: ikut tema Breeze, tray integrates
- **Wayland-first**: prioritas Wayland, X11 fallback
- **AUR ready**: PKGBUILD untuk `yay -S cachy-crosshair`
- **Offline**: tidak butuh internet
- **Open source**: MIT, GitHub

## 6. Scope Fase

### Fase 1 — MVP (1-2 minggu)
- Overlay dot + cross, color + size + opacity
- Toggle hotkey
- Wayland click-through works di KDE
- Settings window minimal

### Fase 2 — Polish (2-3 minggu)
- Semua preset types, outline, gap, shadow
- Tray icon, autostart, config save
- Multi-monitor, offset

### Fase 3 — Pro (1 bulan)
- Custom image, import/export, CLI
- PKGBUILD AUR, .desktop, icon
- Animated crosshair, gap tuning

## 7. Acceptance Criteria (Definition of Done)
- [ ] Overlay muncul di center, tidak block klik game (test di CS2 / Minecraft)
- [ ] Toggle hotkey works global (walau game fullscreen)
- [ ] Setting diubah → preview real-time tanpa restart
- [ ] Restart PC → crosshair balik sesuai config terakhir
- [ ] Works di Wayland KDE + test X11 fallback

## 8. Out of Scope (V1)
- Aimbot / memory reading (cheat) — TIDAK
- Auto-detect game
- Cloud sync

---
*Next: pilih stack di 02-tech-stack-cachyos.md*
