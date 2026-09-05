# Competitor Analysis — Crosshair Apps

## Linux Native (sedikit)
| App | Stack | Pros | Cons |
|-----|-------|------|------|
| **Crossover** (game) | — | — | Bukan overlay crosshair |
| **GOverlay / MangoHud** | C++ | Overlay FPS | Tidak ada crosshair center |
| `screenkey` / `onboard` | — | Overlay | Bukan crosshair |
| Custom script `xprop` + `feh` | X11 | Simple | Tidak Wayland, tidak click-through |
| **HyprCross** (Hyprland) | Hyprland plugin | Native | Hanya Hyprland |

## Windows (banyak, jadi inspirasi)
| App | Fitur Unggulan |
|-----|----------------|
| **Crosshair X** (Steam, $) | 50+ presets, drag-drop, auto-hide, Workshop |
| **Custom Desktop Logo** | Image overlay transparan |
| **CrossOver** (Windows) | Gratis, 50+ presets, opacity, hide key |
| **GameGlass** | External |

## Fitur yang Wajib Kita Kalahkan
- [x] Gratis & open source (vs Crosshair X bayar)
- [x] Wayland native (vs semua Windows app tidak relevan)
- [x] AUR install 1 command (vs manual Windows exe)
- [x] JSON preset shareable
- [x] < 50MB RAM (vs Electron Windows 200MB)

## Inspirasi UI
- Crosshair X: preset grid + live preview + slider
- Kita: KDE Breeze + grid 3x3 preset + canvas preview 200x200 + sidebar sliders
