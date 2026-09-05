#!/usr/bin/env python3
"""
src/main_gui.py — Hybrid Main App (Qt)
Overlay transparent + Settings GUI + Tray + Autostart
Entry untuk AppImage & development
Usage:
  python src/main_gui.py
  python src/main_gui.py --hidden   # start tray only
"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import subprocess, signal

from core.config import load_config, ensure_default_presets, save_config
from core.detector import detect_backend, explain

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cachy Crosshair — GUI")
    parser.add_argument("--hidden", action="store_true", help="start hidden (tray only)")
    parser.add_argument("--backend", choices=["auto","qt"], default="auto")
    args = parser.parse_args()

    explain()
    ensure_default_presets()
    cfg = load_config()

    # Gaming mode: track GTK subprocess
    gtk_proc = {"proc": None}

    def start_gtk_overlay():
        if gtk_proc["proc"] and gtk_proc["proc"].poll() is None:
            print("[GAMING] GTK already running")
            return
        gtk_script = str(Path(__file__).parent / "backends" / "gtk" / "overlay.py")
        print(f"[GAMING] Starting GTK layer-shell: {gtk_script}")
        # Check if gtk4-layer-shell available
        try:
            import gi
            gi.require_version('Gtk','4.0')
            try:
                gi.require_version('GtkLayerShell','0.1')
                has_ls = True
            except:
                try:
                    gi.require_version('Gtk4LayerShell','1.0')
                    has_ls = True
                except:
                    has_ls = False
            if not has_ls:
                QMessageBox.warning(None, "Gaming Mode", "gtk4-layer-shell belum terinstall!\n\nOverlay mungkin tetap hilang di fullscreen Sober.\n\nInstall:\nsudo pacman -S gtk4-layer-shell\n\nSementara, coba mode XWayland:\nQT_QPA_PLATFORM=xcb ~/.local/bin/cachy-crosshair.AppImage")
        except: pass
        try:
            env = os.environ.copy()
            # Ensure PYTHONPATH for core
            env["PYTHONPATH"] = str(Path(__file__).parent) + ":" + env.get("PYTHONPATH","")
            gtk_proc["proc"] = subprocess.Popen([sys.executable, gtk_script], env=env)
            print(f"[GAMING] GTK PID {gtk_proc['proc'].pid}")
            # hide Qt overlay while GTK is active (avoid double)
            overlay.hide()
        except Exception as e:
            QMessageBox.warning(None, "Gaming Mode Error", str(e))

    def stop_gtk_overlay():
        if gtk_proc["proc"]:
            try:
                print(f"[GAMING] Stopping GTK PID {gtk_proc['proc'].pid}")
                gtk_proc["proc"].terminate()
                try: gtk_proc["proc"].wait(timeout=2)
                except: gtk_proc["proc"].kill()
            except: pass
            gtk_proc["proc"] = None
        overlay.show()
        overlay.raise_()

    def toggle_gaming(checked):
        if checked:
            start_gtk_overlay()
        else:
            stop_gtk_overlay()
        # save autostart gaming state?
        print(f"[GAMING] toggled {checked}")

    def restart_xcb():
        # Restart app with QT_QPA_PLATFORM=xcb via subprocess and quit current
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "xcb"
        app_path = os.environ.get("APPIMAGE", str(Path(__file__).resolve()))
        if app_path.endswith(".py"):
            cmd = [sys.executable, app_path]
        else:
            cmd = [app_path]
        print(f"[XCB] Restarting with xcb: {cmd}")
        subprocess.Popen(cmd, env=env)
        app.quit()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Cachy Crosshair")
    app.setApplicationVersion("0.1.0")
    app.setDesktopFileName("cachy-crosshair")

    # Icon: prefer bundled, fallback theme
    icon = QIcon(str(Path(__file__).parent / "shared" / "assets" / "cachy-crosshair.png"))
    if icon.isNull():
        icon = QIcon.fromTheme("crosshair") or QIcon.fromTheme("applications-games")
    app.setWindowIcon(icon)

    # Overlay
    from backends.qt.overlay import QtCrosshairOverlay
    from PyQt6.QtCore import QTimer
    overlay = QtCrosshairOverlay(cfg)
    if args.hidden:
        overlay.hide()
        print("[MAIN] overlay hidden (--hidden)")
    else:
        # ensure visible after event loop
        QTimer.singleShot(200, lambda: (overlay.show(), overlay.showFullScreen(), overlay.raise_(), print(f"[MAIN] overlay ensure visible {overlay.width()}x{overlay.height()}")))
        print("[MAIN] overlay will show")

    # Settings window (lazy show)
    from backends.qt.settings import SettingsWindow
    settings = SettingsWindow(cfg, overlay=overlay)
    settings.configChanged.connect(lambda c: save_config(c))
    settings.toggleRequested.connect(lambda: overlay.setVisible(not overlay.isVisible()))
    def quit_all():
        if gtk_proc["proc"]:
            try: gtk_proc["proc"].terminate()
            except: pass
        app.quit()
    settings.quitRequested.connect(quit_all)

    # Auto-show settings on first run? No, tray only unless toggled
    # settings.show()

    # Tray
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.warning(None, "Tray", "System tray tidak tersedia — pakai ESC untuk quit")
        # ESC handler
        from PyQt6.QtCore import QObject, QEvent
        class EscFilter(QObject):
            def eventFilter(self, obj, e):
                if e.type() == QEvent.Type.KeyPress and e.key() == Qt.Key.Key_Escape:
                    app.quit(); return True
                return False
        filt = EscFilter(); app.installEventFilter(filt)
    else:
        tray = QSystemTrayIcon(icon, app)
        tray.setToolTip("Cachy Crosshair — klik untuk Settings")
        menu = QMenu()

        act_show = QAction("⚙ Settings", menu)
        act_show.triggered.connect(lambda: (settings.show(), settings.raise_(), settings.activateWindow()))
        act_toggle = QAction("👁 Toggle Overlay", menu)
        act_toggle.triggered.connect(lambda: overlay.setVisible(not overlay.isVisible()))
        # Gaming Mode (GTK layer-shell for Sober)
        act_gaming = QAction("🎮 Gaming Mode (Sober fullscreen)", menu)
        act_gaming.setCheckable(True)
        act_gaming.setToolTip("Pakai GTK layer-shell agar tetap di atas Sober fullscreen")
        act_gaming.toggled.connect(toggle_gaming)
        act_xcb = QAction("🔧 Restart as XWayland (fix fullscreen hide)", menu)
        act_xcb.triggered.connect(restart_xcb)
        act_autostart = QAction("🔄 Autostart", menu)
        act_autostart.setCheckable(True)
        autostart_path = Path.home() / ".config" / "autostart" / "cachy-crosshair.desktop"
        act_autostart.setChecked(autostart_path.exists())
        def toggle_autostart(checked):
            autostart_path.parent.mkdir(parents=True, exist_ok=True)
            if checked:
                # For AppImage, Exec is AppImage path; fallback to launcher
                exec_path = os.environ.get("APPIMAGE", str(Path(__file__).resolve()))
                # If running via python, use launcher path
                if exec_path.endswith(".py") or "python" in exec_path:
                    exec_path = f"python {Path(__file__).resolve()}"
                desktop = f"""[Desktop Entry]
Type=Application
Name=Cachy Crosshair
Comment=Crosshair overlay untuk CachyOS
Exec={exec_path} --hidden
Icon=cachy-crosshair
Terminal=false
Categories=Game;Utility;
X-GNOME-Autostart-enabled=true
"""
                autostart_path.write_text(desktop)
                QMessageBox.information(settings, "Autostart", f"Autostart aktif: {autostart_path}")
            else:
                if autostart_path.exists():
                    autostart_path.unlink()
                QMessageBox.information(settings, "Autostart", "Autostart dimatikan")
        act_autostart.toggled.connect(toggle_autostart)

        act_quit = QAction("❌ Quit", menu)
        def do_quit():
            if gtk_proc["proc"]:
                try: gtk_proc["proc"].terminate()
                except: pass
            app.quit()
        act_quit.triggered.connect(do_quit)

        menu.addAction(act_show)
        menu.addAction(act_toggle)
        menu.addSeparator()
        menu.addAction(act_gaming)
        menu.addAction(act_xcb)
        menu.addSeparator()
        menu.addAction(act_autostart)
        menu.addSeparator()
        menu.addAction(act_quit)

        tray.setContextMenu(menu)
        tray.activated.connect(lambda reason: (settings.show(), settings.raise_()) if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        tray.show()
        # Click tray → show settings
        # Some DE need message
        tray.showMessage("Cachy Crosshair", "Berjalan di tray — klik kanan untuk menu, double-click untuk Settings", QSystemTrayIcon.MessageIcon.Information, 3000)
        # Also connect single click to show
        def on_activated(reason):
            if reason == QSystemTrayIcon.ActivationReason.Trigger:
                settings.show(); settings.raise_(); settings.activateWindow()
        tray.activated.connect(on_activated)

        print("[OK] Tray aktif — double-click / klik untuk Settings")

    # Global shortcut fallback: Ctrl+Alt+C to toggle (via QShortcut if window focused)
    # Real global hotkey via KGlobalAccel portal Fase next

    print("[OK] Cachy Crosshair GUI ready")
    print("     Overlay: fullscreen transparent center")
    print("     Settings: klik tray → Settings")
    print("     Toggle: tray menu → Toggle Overlay")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
