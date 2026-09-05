# Packaging — Cachy Crosshair

## AppImage (Recommended untuk CachyOS)

AppImage = 1 file executable, tidak perlu install, bisa di-move, auto integrated.

### Build (di CachyOS kamu)

```bash
# 1. Install deps build (sekali)
sudo pacman -S python-pyqt6 layer-shell-qt librsvg  # untuk icon png

# Jika mau bundle pip (agar AppImage jalan di PC tanpa python-pyqt6 host):
sudo pacman -S python-pip

# 2. Build
cd crosshair-workflow
bash packaging/appimage/build-appimage.sh

# Output: dist/Cachy-Crosshair-0.1.0-x86_64.AppImage
```

### Test
```bash
chmod +x dist/Cachy-Crosshair-*.AppImage
./dist/Cachy-Crosshair-*.AppImage              # GUI + overlay muncul
./dist/Cachy-Crosshair-*.AppImage --hidden     # tray only
```

### Install User (tanpa sudo)
```bash
mkdir -p ~/.local/bin
cp dist/Cachy-Crosshair-*.AppImage ~/.local/bin/cachy-crosshair.AppImage
# autostart (opsional, via GUI Settings → Autostart juga bisa)
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/cachy-crosshair.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Cachy Crosshair
Exec=$HOME/.local/bin/cachy-crosshair.AppImage --hidden
Icon=cachy-crosshair
EOF
```

### Integrasi Desktop (AppImageLauncher)
Jika pakai `appimagelauncher` (AUR: `appimagelauncher`):
```bash
yay -S appimagelauncher
# double-click AppImage → Integrate and run
```

## Alternative: Native Arch Package (AUR)

Untuk nanti (Fase 4):
```bash
makepkg -si  # di folder dengan PKGBUILD
yay -S cachy-crosshair  # setelah publish AUR
```

## Struktur Packaging
```
packaging/
├── cachy-crosshair.desktop      # .desktop universal
├── icons/cachy-crosshair.svg    # icon vector
└── appimage/
    ├── AppRun                   # entry point AppImage
    └── build-appimage.sh        # build script (appimagetool)
```

## Troubleshooting
- `PyQt6 tidak ditemukan` → `sudo pacman -S python-pyqt6` atau rebuild dengan `python-pip` terinstall
- `layer-shell-qt tidak ada` → overlay fallback ke Qt flags (tetap jalan, tapi click-through mungkin tidak sempurna di Wayland)
- AppImage tidak executable → `chmod +x *.AppImage`
