# 03 — UI/UX Design Crosshair CachyOS

## 3.1 Konsep UX
- **Overlay**: tidak ada UI, hanya crosshair di center. Invisible, tidak ganggu.
- **Settings window**: muncul saat klik tray atau hotkey `Ctrl+Alt+C` → buka window KDE Breeze, ada preview + kontrol.
- **Tray**: icon target 🎯, klik kiri toggle, klik kanan menu.

## 3.2 Settings Window Layout (KDE Breeze style)

```
┌─────────────────────────────────────────────────┐
│  Cachy Crosshair — Settings              [—][□][×] │
├──────────────────┬──────────────────────────────┤
│  PREVIEW         │  CONTROLS                    │
│  ┌────────────┐  │  Preset: [Dot ▼] [★ Save]     │
│  │            │  │  ───────────────────────────  │
│  │      +     │  │  Color:  [🟥 #FF0000] [Picker] │
│  │   (center) │  │  Size:      ●─────  12px       │
│  │            │  │  Thickness: ●──    2px        │
│  └────────────┘  │  Opacity:   ●────── 80%       │
│  [200x200 canvas]│  Gap:       ●─      4px       │
│                  │                              │
│  Monitor: [1▼]   │  ☑ Outline  [⬛ #000] 1px      │
│  Offset X/Y: 0,0 │  ☑ Center Dot      4px       │
│                  │  ☐ Shadow / Glow            │
│                  │                              │
│                  │  ───────────────────────────  │
│                  │  Hotkey: [Ctrl+Alt+C] [Change]│
│                  │  ☑ Autostart at login       │
│                  │  ☑ Start hidden (tray only) │
│                  ├──────────────────────────────┤
│                  │  [ Reset ]  [ Export JSON ]  │
│                  │  [  Apply  ]  [  Toggle  ]    │
└──────────────────┴──────────────────────────────┘
```

## 3.3 Preset Grid (Tab Presets)

```
┌─────────────────────────────────────────┐
│  Presets  [ + New ] [ Import ]          │
├─────────────────────────────────────────┤
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐            │
│  │ •  │ │  + │ │ ⊕  │ │  T │  Dot      │
│  └────┘ └────┘ └────┘ └────┘  Cross    │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐  Circle   │
│  │ ⊙  │ │ ╋  │ │ ◯  │ │IMG │  T-shape  │
│  └────┘ └────┘ └────┘ └────┘            │
│                                         │
│  Selected: Dot Red → click to load      │
└─────────────────────────────────────────┘
```

## 3.4 Crosshair Rendering Spec

| Type | Render | Param |
|------|--------|-------|
| Dot | `drawEllipse(center, size)` | size, color, opacity |
| Cross | 2x `drawLine` horizontal + vertical | size (length), thickness, gap |
| Cross+Dot | Cross + dot di center | + dotSize |
| Circle | `drawEllipse` outline | size (diameter), thickness |
| T | 3 garis (tanpa atas) | size, thickness |
| Custom Image | `drawPixmap` PNG/SVG scaled | image path, size |

**Outline**: draw 2x — dulu outline lebih besar (thickness+outlineThickness) warna outline, lalu draw utama di atas.

**Contoh QPainter**:
```python
def paintEvent(self, e):
    p = QPainter(self)
    p.setRenderHint(QPainter.Antialiasing)
    cx, cy = self.width()//2, self.height()//2
    # outline
    pen = QPen(QColor(outlineColor), thickness+2)
    # main
    pen = QPen(QColor(color), thickness)
    p.setOpacity(opacity)
    # cross
    p.drawLine(cx - size - gap, cy, cx - gap, cy)
    p.drawLine(cx + gap, cy, cx + gap + size, cy)
    p.drawLine(cx, cy - size - gap, cx, cy - gap)
    p.drawLine(cx, cy + gap, cx, cy + gap + size)
```

## 3.5 Icon & Branding
- Icon: target 🎯 atau crosshair `⊕` dengan warna CachyOS biru `#1E90FF` + aksen hijau
- Tray icon: SVG 22px, monochrome ikut tema (light/dark)
- App icon: 512x512 PNG/SVG untuk AUR

## 3.6 Flow Interaksi
1. Install → Autostart → crosshair langsung muncul (preset default dot red)
2. User tekan `Ctrl+Alt+C` → toggle OFF (overlay hide, tray tetep)
3. Klik tray → Settings → ubah color/size → preview update realtime → Apply → overlay update
4. Save preset → JSON ke `~/.config/cachy-crosshair/presets/my.json`
5. Export → share JSON ke teman → Import → load

## 3.7 Aksesibilitas KDE
- Ikut Breeze color scheme (dark/light auto)
- Slider pakai `QSlider` native, spinbox untuk angka presisi
- Color picker pakai `QColorDialog` native KDE
