#!/usr/bin/env python3
"""
Prototype Overlay — CachyOS KDE Wayland
Test kuick click-through + transparent overlay.

Run: python src/prototype_overlay.py
Expected: fullscreen transparan, dot merah di center, bisa klik tembus.
Tekan ESC atau klik tray Quit untuk exit.
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QPainter, QColor, QPen, QIcon, QAction
from PyQt6.QtCore import Qt, QTimer

class CrosshairOverlay(QWidget):
    def __init__(self, config=None):
        super().__init__(None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Config default
        self.cfg = config or {
            "type": "cross_dot",
            "color": "#FF0000",
            "size": 12,
            "thickness": 2,
            "opacity": 0.9,
            "gap": 4,
            "outline": True,
            "outlineColor": "#000000",
            "centerDotSize": 4,
        }

        # Layer-shell untuk Wayland KDE (jika ada)
        try:
            from LayerShellQt import Window as LSWindow
            ls = LSWindow.get(self.windowHandle())
            if ls:
                ls.setLayer(LSWindow.LayerOverlay)
                ls.setKeyboardInteractivity(LSWindow.KeyboardInteractivityNone)
                ls.setExclusiveZone(-1)
                print("[OK] LayerShellQt overlay layer aktif")
        except ImportError:
            print("[INFO] LayerShellQt tidak ada, pakai Qt flags fallback")
        except Exception as e:
            print(f"[WARN] LayerShellQt error: {e}")

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # Fullscreen ke screen primary
        self.showFullScreen()
        print(f"[OK] Overlay fullscreen: {self.width()}x{self.height()} — center {self.width()//2},{self.height()//2}")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setOpacity(self.cfg["opacity"])
        cx, cy = self.width() // 2, self.height() // 2
        color = QColor(self.cfg["color"])
        outlineColor = QColor(self.cfg["outlineColor"])
        size = self.cfg["size"]
        thick = self.cfg["thickness"]
        gap = self.cfg["gap"]

        # Helper draw dengan outline
        def draw_line(x1, y1, x2, y2):
            if self.cfg["outline"]:
                p.setPen(QPen(outlineColor, thick + 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawLine(x1, y1, x2, y2)
            p.setPen(QPen(color, thick, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(x1, y1, x2, y2)

        typ = self.cfg["type"]
        if typ in ("cross", "cross_dot"):
            # horizontal
            draw_line(cx - size - gap, cy, cx - gap, cy)
            draw_line(cx + gap, cy, cx + gap + size, cy)
            # vertical
            draw_line(cx, cy - size - gap, cx, cy - gap)
            draw_line(cx, cy + gap, cx, cy + gap + size)
        if typ in ("dot", "cross_dot"):
            dot = self.cfg["centerDotSize"] if typ == "cross_dot" else size
            if self.cfg["outline"]:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(outlineColor)
                p.drawEllipse(cx - dot//2 -1, cy - dot//2 -1, dot+2, dot+2)
            p.setBrush(color)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(cx - dot//2, cy - dot//2, dot, dot)
        if typ == "circle":
            if self.cfg["outline"]:
                p.setPen(QPen(outlineColor, thick+2))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(cx - size//2, cy - size//2, size, size)
            p.setPen(QPen(color, thick))
            p.drawEllipse(cx - size//2, cy - size//2, size, size)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            print("[EXIT] ESC pressed")
            QApplication.quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    overlay = CrosshairOverlay()
    overlay.show()

    # Tray (opsional, jika system tray tersedia)
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = QSystemTrayIcon(QIcon.fromTheme("crosshair"), app)
        # fallback icon jika theme tidak ada
        if tray.icon().isNull():
            tray.setIcon(QIcon.fromTheme("applications-games"))
        menu = QMenu()
        act_toggle = QAction("Toggle Crosshair", menu)
        act_quit = QAction("Quit", menu)
        act_toggle.triggered.connect(lambda: overlay.setVisible(not overlay.isVisible()))
        act_quit.triggered.connect(app.quit)
        menu.addAction(act_toggle)
        menu.addSeparator()
        menu.addAction(act_quit)
        tray.setContextMenu(menu)
        tray.setToolTip("Cachy Crosshair — prototype (ESC to quit)")
        tray.show()
        tray.showMessage("Cachy Crosshair", "Prototype overlay aktif — dot merah center. Klik tray untuk toggle. ESC untuk quit.", QSystemTrayIcon.MessageIcon.Information, 3000)
        print("[OK] Tray icon aktif")
    else:
        print("[WARN] System tray tidak tersedia — pakai ESC untuk quit")

    print("[INFO] Prototype jalan. Test: buka Firefox F11 fullscreen, coba klik — harus tembus.")
    print("[INFO] Tekan ESC untuk quit.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
