# Install Guide — CachyOS

## Untuk User (setelah AUR publish)
```bash
yay -S cachy-crosshair
# atau
paru -S cachy-crosshair
cachy-crosshair # run
```

Autostart otomatis, tray muncul.

## Untuk Dev (sekarang)
```bash
# Opsi A PyQt6
sudo pacman -S python-pyqt6 layer-shell-qt
python -m venv venv
source venv/bin/activate
pip install PyQt6
python src/prototype_overlay.py

# Opsi B Tauri
sudo pacman -S webkit2gtk-4.1 rustup
rustup default stable
npm create tauri-app@latest # atau cargo create-tauri-app
```

## Build PKGBUILD (Fase 4)
```bash
cd crosshair-workflow
makepkg -si
```
