# 04 — Roadmap Crosshair CachyOS

## Fase 0 — Setup Workflow (Hari ini, 2026-09-03) ✅
- [x] Buat `crosshair-workflow/` + 6 dokumen
- [x] Deteksi system KDE Wayland
- [ ] Pilih stack final (A/B/C)
- [ ] Set nama app + repo GitHub

## Fase 1 — Prototype Overlay MVP (Minggu 1)
**Goal**: Dot merah di center, click-through, toggle.

- [ ] Buat `src/prototype_overlay.py` (PyQt6 minimal 80 baris)
- [ ] Test di KDE Wayland: `python prototype_overlay.py` → cek click-through
- [ ] Jika gagal layer-shell, fallback test Qt flags
- [ ] Buat `src/overlay/painter.py` (render dot + cross)
- [ ] Hotkey toggle sederhana (tray click dulu)
- **Deliverable**: Overlay works di game windowed (test di Minecraft / CS2 / browser fullscreen F11)

## Fase 2 — Settings UI (Minggu 2)
- [ ] `src/editor/settings.py` — QWidget dengan preview canvas 200x200
- [ ] Kontrol: preset dropdown, color picker, slider size/thickness/opacity
- [ ] Live preview (slider → repaint overlay realtime via signal)
- [ ] Config save/load JSON `~/.config/cachy-crosshair/config.json`
- [ ] Tray icon `QSystemTrayIcon` + menu Toggle/Settings/Quit

## Fase 3 — Full Features (Minggu 3-4)
- [ ] Semua crosshair types (dot, cross, circle, T, custom image)
- [ ] Outline, gap, center dot, shadow
- [ ] Multi-monitor picker + offset X/Y
- [ ] Autostart `.desktop` generation
- [ ] Global hotkey (KGlobalAccel / portal)
- [ ] Import/export preset JSON

## Fase 4 — Polish & Packaging (Minggu 5)
- [ ] Icon SVG + `.desktop` file
- [ ] PKGBUILD untuk AUR (`cachy-crosshair` / `cachy-crosshair-git`)
- [ ] Test install: `makepkg -si` + `yay -S cachy-crosshair`
- [ ] README GitHub + screenshot + demo GIF (peek)
- [ ] CLI args: `--toggle`, `--preset`, `--config`
- [ ] Wayland + X11 CI test (jika ada runner)

## Fase 5 — Launch (Minggu 6)
- [ ] Publish GitHub public
- [ ] Submit AUR (`aurpublish` / `ssh aur@aur.archlinux.org`)
- [ ] Post di r/cachyos, r/archlinux, r/linux_gaming
- [ ] Tag v0.1.0, release binary (optional AppImage)

## Estimasi Total: 4-6 minggu (part-time, 1-2 jam/hari)

## Blokir Risiko
| Risiko | Mitigasi |
|--------|----------|
| Click-through tidak works di KWin | Test awal Fase 1, fallback ke `gtk-layer-shell` atau `wtype` + KWin script |
| Global hotkey tidak works Wayland | MVP pakai tray dulu, hotkey stage 3 pakai portal |
| Game fullscreen exclusive (Wine/Proton) overlay ketutup | Cek gamescope, pakai `layer=overlay` harus di atas. Jika tidak, pakai windowed fullscreen. |

## Milestone Check
- MVP done = overlay dot click-through ✅ → lanjut Fase 2
- Settings done = slider realtime ✅ → lanjut Fase 3
- AUR done = `yay -S` works ✅ → launch

---
*Lanjut: cek TODO.md untuk checklist harian.*
