#!/bin/bash
# build-appimage.sh — Build Cachy Crosshair AppImage (hybrid)
# Works di CachyOS Arch, tanpa sudo untuk build (butuh sudo untuk install deps sekali)
# Metode: AppDir manual + appimagetool (paling compatible)
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$PROJECT_ROOT/src"
PKG="$PROJECT_ROOT/packaging"
APPDIR="$PROJECT_ROOT/dist/cachy-crosshair.AppDir"
VERSION="${VERSION:-0.1.0}"
ARCH="$(uname -m)"

echo "=== Cachy Crosshair AppImage Builder ==="
echo "Project: $PROJECT_ROOT"
echo "Version: $VERSION"
echo "Arch: $ARCH"
echo ""

# 1. cek deps build
echo "[1/6] Cek dependencies..."
if ! command -v python3 &>/dev/null; then echo "ERR: python3 tidak ada"; exit 1; fi
# pip via ensurepip fallback atau pacman
if ! python3 -m pip --version &>/dev/null; then
    echo "WARN: pip tidak ada — akan pakai system python-pyqt6 via pacman"
    echo "      Jalankan sekali: sudo pacman -S python-pip python-pyqt6 python-pyside6"
    USE_SYSTEM_QT=1
else
    USE_SYSTEM_QT=0
fi

# 2. siapkan dist
echo "[2/6] Siapkan AppDir: $APPDIR"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/src" "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/scalable/apps" "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# 3. copy source
echo "[3/6] Copy source..."
cp -r "$SRC/core" "$APPDIR/usr/src/"
cp -r "$SRC/backends" "$APPDIR/usr/src/"
cp -r "$SRC/shared" "$APPDIR/usr/src/"
cp "$SRC/main_gui.py" "$APPDIR/usr/src/"
cp "$SRC/launcher.py" "$APPDIR/usr/src/"
cp "$PKG/cachy-crosshair.desktop" "$APPDIR/cachy-crosshair.desktop"
cp "$PKG/cachy-crosshair.desktop" "$APPDIR/usr/share/applications/"
# icon
if [ -f "$PKG/icons/cachy-crosshair.svg" ]; then
    cp "$PKG/icons/cachy-crosshair.svg" "$APPDIR/cachy-crosshair.svg"
    cp "$PKG/icons/cachy-crosshair.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/"
    # generate png 256 via rsvg if available
    if command -v rsvg-convert &>/dev/null; then
        rsvg-convert -w 256 -h 256 "$PKG/icons/cachy-crosshair.svg" -o "$APPDIR/cachy-crosshair.png"
        cp "$APPDIR/cachy-crosshair.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/cachy-crosshair.png"
    elif command -v convert &>/dev/null; then
        convert -background none "$PKG/icons/cachy-crosshair.svg" -resize 256x256 "$APPDIR/cachy-crosshair.png"
        cp "$APPDIR/cachy-crosshair.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/cachy-crosshair.png"
    else
        cp "$PKG/icons/cachy-crosshair.svg" "$APPDIR/cachy-crosshair.png" 2>/dev/null || true
    fi
else
    echo "WARN: icon tidak ditemukan"
fi
cp "$PKG/appimage/AppRun" "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"

# 4. buat AppDir desktop + icon symlink (appimagetool butuh)
ln -sf cachy-crosshair.desktop "$APPDIR/cachy-crosshair.desktop" 2>/dev/null || true
ln -sf cachy-crosshair.svg "$APPDIR/cachy-crosshair.svg" 2>/dev/null || true

# 5. bundle python deps
echo "[4/6] Bundle Python dependencies..."
if [ "$USE_SYSTEM_QT" = "0" ]; then
    echo "  → pakai pip (venv AppDir)"
    python3 -m pip install --target="$APPDIR/usr/lib/python" PyQt6 --quiet || {
        echo "  pip install gagal, fallback ke system Qt"
        USE_SYSTEM_QT=1
    }
fi
if [ "$USE_SYSTEM_QT" = "1" ]; then
    echo "  → pakai system python-pyqt6 (AppImage akan butuh host install python-pyqt6)"
    echo "  Untuk bundle penuh, install pip: sudo pacman -S python-pip && rerun"
    # tulis wrapper yang cek system PyQt6
    cat > "$APPDIR/usr/bin/cachy-crosshair" <<'WRAP'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")/../.."
export PYTHONPATH="$APPDIR/usr/src:$PYTHONPATH"
exec python3 "$APPDIR/usr/src/main_gui.py" "$@"
WRAP
    chmod +x "$APPDIR/usr/bin/cachy-crosshair"
fi

# Also create AppRun fallback check
cat > "$APPDIR/AppRun.check" <<'CHECK'
# Check PyQt6 at runtime
python3 -c "import PyQt6" 2>/dev/null || { echo "ERROR: PyQt6 tidak ditemukan."; echo "Install: sudo pacman -S python-pyqt6 layer-shell-qt"; echo "Atau build dengan pip: python -m pip install PyQt6 && ./build-appimage.sh"; exit 1; }
CHECK

# 6. download appimagetool jika belum ada
echo "[5/6] Siapkan appimagetool..."
APPIMAGETOOL="$PROJECT_ROOT/dist/appimagetool-$ARCH.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "  Download appimagetool..."
    mkdir -p "$PROJECT_ROOT/dist"
    curl -L -o "$APPIMAGETOOL" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage" || wget -O "$APPIMAGETOOL" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage" || {
        echo "Gagal download appimagetool — install manual dari https://github.com/AppImage/appimagetool"
        echo "Atau build AppDir saja (tanpa AppImage) di $APPDIR"
        exit 1
    }
    chmod +x "$APPIMAGETOOL"
fi

# 6. build AppImage
echo "[6/6] Build AppImage..."
OUT="$PROJECT_ROOT/dist/Cachy-Crosshair-${VERSION}-${ARCH}.AppImage"
ARCH=$ARCH "$APPIMAGETOOL" "$APPDIR" "$OUT" || {
    echo "Build via appimagetool gagal, coba fallback: mksquashfs"
    if command -v mksquashfs &>/dev/null; then
        echo "Fallback belum implement — AppDir tersedia di $APPDIR"
    fi
    exit 1
}
chmod +x "$OUT"
echo ""
echo "✅ Selesai! AppImage: $OUT"
echo "   Size: $(du -h "$OUT" | cut -f1)"
echo ""
echo "Cara test:"
echo "  chmod +x $OUT"
echo "  ./$OUT                # GUI + overlay"
echo "  ./$OUT --hidden       # tray only"
echo ""
echo "Cara install (optional):"
echo "  mkdir -p ~/.local/bin && cp \"$OUT\" ~/.local/bin/cachy-crosshair.AppImage"
echo "  ~/.local/bin/cachy-crosshair.AppImage &"
echo ""
echo "Integrasi desktop:"
echo "  ./$OUT --appimage-extract  # test AppDir"
