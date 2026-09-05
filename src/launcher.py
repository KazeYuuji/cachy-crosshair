#!/usr/bin/env python3
"""
src/launcher.py — Entry point HYBRID
Auto-detect DE → load backend yang tepat (qt/gtk/tauri)
Usage:
  python src/launcher.py                  # auto
  python src/launcher.py --backend qt     # force Qt (KDE)
  python src/launcher.py --backend gtk    # force GTK (Hyprland)
  python src/launcher.py --toggle         # toggle via config
"""
import sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.detector import detect_backend, explain
from core.config import load_config, ensure_default_presets

def main():
    parser = argparse.ArgumentParser(description="Cachy Crosshair — Hybrid Launcher")
    parser.add_argument("--backend", choices=["auto","qt","gtk","tauri"], default="auto", help="force backend")
    parser.add_argument("--preset", type=str, help="load preset by name")
    parser.add_argument("--list-backends", action="store_true")
    args = parser.parse_args()

    if args.list_backends:
        print("qt (KDE) | gtk (Hyprland/Sway/GNOME) | tauri (universal)")
        return

    backend = detect_backend(args.backend)
    explain()
    print(f"[LAUNCH] backend = {backend}")

    ensure_default_presets()
    cfg = load_config()
    if args.preset:
        from core.config import load_preset
        try:
            cfg = load_preset(args.preset)
            print(f"[PRESET] loaded {args.preset}")
        except Exception as e:
            print(f"[ERR] preset {args.preset}: {e}")

    if backend == "qt":
        from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
        from PyQt6.QtGui import QAction, QIcon
        from PyQt6.QtCore import Qt
        try:
            from backends.qt.overlay import QtCrosshairOverlay
        except ImportError as e:
            print(f"[ERR] Qt backend gagal: {e}")
            print("Install: sudo pacman -S python-pyqt6 layer-shell-qt")
            sys.exit(1)

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        overlay = QtCrosshairOverlay(cfg)
        overlay.show()
        print(f"[OK] Qt overlay ready — {overlay.width()}x{overlay.height()} — ESC to quit")

        # ESC handler via eventFilter
        from PyQt6.QtCore import QObject, QEvent
        class EscFilter(QObject):
            def eventFilter(self, obj, e):
                if e.type() == QEvent.Type.KeyPress and e.key() == Qt.Key.Key_Escape:
                    print("[EXIT] ESC"); app.quit(); return True
                return False
        filt = EscFilter(); app.installEventFilter(filt)

        # Tray
        if QSystemTrayIcon.isSystemTrayAvailable():
            tray = QSystemTrayIcon(QIcon.fromTheme("applications-games"))
            if tray.icon().isNull():
                tray.setIcon(QIcon.fromTheme("crosshair"))
            menu = QMenu()
            a_toggle = QAction("Toggle"); a_toggle.triggered.connect(lambda: overlay.setVisible(not overlay.isVisible()))
            a_quit = QAction("Quit"); a_quit.triggered.connect(app.quit)
            menu.addAction(a_toggle); menu.addSeparator(); menu.addAction(a_quit)
            tray.setContextMenu(menu); tray.setToolTip(f"Cachy Crosshair [{backend}] — ESC to quit"); tray.show()
            print("[OK] Tray aktif")

        # Watch config file untuk live reload (Fase 3)
        sys.exit(app.exec())

    elif backend == "gtk":
        print("[TODO] GTK backend Fase 2 — belum implement")
        print("  sudo pacman -S gtk4 gtk4-layer-shell python-gobject")
        print("  lalu: python src/backends/gtk/overlay.py")
        sys.exit(0)

    elif backend == "tauri":
        print("[TODO] Tauri backend Fase 3 — scaffold di src/backends/tauri/")
        print("  cd src/backends/tauri && cargo tauri dev")
        sys.exit(0)

if __name__ == "__main__":
    main()
