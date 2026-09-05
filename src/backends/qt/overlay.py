"""
backends/qt/overlay.py — Backend A untuk KDE Plasma (Wayland/X11)
Pakai core/painter.py + core/config.py
Fix Wayland visibility: layer-shell via QTimer + raise + larger default check
"""
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer
from core.painter import compute_cross_lines, compute_circle, compute_dot
import os

class QtCrosshairOverlay(QWidget):
    def __init__(self, cfg):
        super().__init__(None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.BypassWindowManagerHint
        )
        self.cfg = cfg
        # translucent + no bg
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        # ensure we cover all screens
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        # Try layer-shell after windowHandle is created (delayed)
        QTimer.singleShot(100, self._apply_layer_shell)
        # fallback raise timer
        QTimer.singleShot(500, self._ensure_fullscreen_and_raise)

        # Debug: allow env CACHY_CROSSHAIR_DEBUG=1 to show red bg
        self.debug_bg = os.environ.get("CACHY_CROSSHAIR_DEBUG","0") == "1"

        # show fullscreen via screen geometry (more reliable than showFullScreen on Wayland)
        self._show_fullscreen()

    def _show_fullscreen(self):
        # Use primary screen geometry instead of showFullScreen for Wayland reliability
        try:
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.geometry()
                self.setGeometry(geo)
                print(f"[OVERLAY] setGeometry {geo.width()}x{geo.height()} at {geo.x()},{geo.y()}")
        except Exception as e:
            print(f"[OVERLAY] geometry err {e}")
        self.show()
        self.showFullScreen()
        self.raise_()
        print(f"[OVERLAY] showFullScreen called, winId={self.winId()}, visible={self.isVisible()}, size={self.width()}x{self.height()}")

    def _ensure_fullscreen_and_raise(self):
        try:
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.geometry()
                if self.width() != geo.width() or self.height() != geo.height():
                    print(f"[OVERLAY] fix geometry {self.width()}x{self.height()} -> {geo.width()}x{geo.height()}")
                    self.setGeometry(geo)
                    self.showFullScreen()
            self.raise_()
            self.update()
            print(f"[OVERLAY] ensure raise, now {self.width()}x{self.height()}, visible={self.isVisible()}")
        except Exception as e:
            print(f"[OVERLAY] ensure err {e}")

    def _apply_layer_shell(self):
        # Try every possible LayerShellQt import path
        tried = []
        for mod in ["LayerShellQt", "layershellqt", "PyLayerShellQt"]:
            try:
                m = __import__(mod)
                tried.append(f"{mod} found")
                # try Window attr
                Win = getattr(m, "Window", None) or getattr(m, "window", None)
                if Win and self.windowHandle():
                    try:
                        ls = Win.get(self.windowHandle())
                        if ls:
                            # try different enum names
                            for layer_name in ["LayerOverlay", "Overlay", "Top"]:
                                if hasattr(Win, layer_name):
                                    try:
                                        ls.setLayer(getattr(Win, layer_name))
                                        print(f"[LS] setLayer {layer_name} ok via {mod}")
                                        break
                                    except: pass
                            for kbd_name in ["KeyboardInteractivityNone", "None"]:
                                if hasattr(Win, kbd_name):
                                    try:
                                        ls.setKeyboardInteractivity(getattr(Win, kbd_name))
                                        print(f"[LS] setKeyboard {kbd_name} ok")
                                        break
                                    except: pass
                            try:
                                ls.setExclusiveZone(-1)
                            except: pass
                            print(f"[LS] layer-shell applied via {mod}")
                            return
                    except Exception as e:
                        tried.append(f"{mod} Window.get err {e}")
                else:
                    tried.append(f"{mod} no Window or no windowHandle")
            except Exception as e:
                tried.append(f"{mod} import fail {e}")
        # Fallback: try Qt Wayland private?
        print(f"[LS] not applied, tried: {tried}")
        # Wayland fallback: use Qt flags already, should still show but may not be click-through perfect
        # Ensure inputRegion empty via WA_TransparentForMouseEvents already

    def update_config(self, cfg):
        self.cfg = cfg
        self.update()
        print(f"[OVERLAY] update_config {cfg.type} {cfg.color} size={cfg.size}")

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # debug bg
        if self.debug_bg:
            p.fillRect(self.rect(), QColor(255,0,0,25))
            p.setPen(QColor(255,255,0))
            p.drawText(20, 30, f"DEBUG OVERLAY {self.width()}x{self.height()} | {self.cfg.type} {self.cfg.color} size={self.cfg.size} | set CACHY_CROSSHAIR_DEBUG=0 to hide red bg")
        p.setOpacity(self.cfg.opacity)
        cx = self.width() // 2 + self.cfg.offset_x
        cy = self.height() // 2 + self.cfg.offset_y
        color = QColor(self.cfg.color)
        outline = QColor(self.cfg.outline_color)

        def draw_line(x1, y1, x2, y2):
            if self.cfg.outline:
                p.setPen(QPen(outline, self.cfg.thickness + 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawLine(x1, y1, x2, y2)
            p.setPen(QPen(color, self.cfg.thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(x1, y1, x2, y2)

        t = self.cfg.type
        # ensure visible: if paint not called, log
        # print(f"[PAINT] {cx},{cy} type={t}")
        if t in ("cross", "cross_dot", "circle_cross"):
            for x1, y1, x2, y2 in compute_cross_lines(cx, cy, self.cfg):
                draw_line(x1, y1, x2, y2)
        if t in ("dot", "cross_dot"):
            x, y, w, h = compute_dot(cx, cy, self.cfg)
            if self.cfg.outline:
                p.setBrush(outline); p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(x-1, y-1, w+2, h+2)
            p.setBrush(color); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(x, y, w, h)
        if t in ("circle", "circle_cross"):
            x, y, w, h = compute_circle(cx, cy, self.cfg)
            if self.cfg.outline:
                p.setPen(QPen(outline, self.cfg.thickness+2)); p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(x, y, w, h)
            p.setPen(QPen(color, self.cfg.thickness)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(x, y, w, h)
        if t == "t":
            s, g = self.cfg.size, self.cfg.gap
            draw_line(cx - s - g, cy, cx - g, cy)
            draw_line(cx + g, cy, cx + g + s, cy)
            draw_line(cx, cy - s - g, cx, cy - g)
