"""
backends/qt/settings.py — GUI Settings Window Hybrid
Preview canvas 200x200 + controls live → update overlay realtime + save config.json
Breeze theme, KWin friendly
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox, QColorDialog,
    QGroupBox, QGridLayout, QMessageBox, QFileDialog, QFrame, QApplication
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from core.painter import CrosshairConfig, compute_cross_lines, compute_circle, compute_dot
from core.config import save_config, save_preset, list_presets, load_preset
import json

PRESET_TYPES = ["dot", "cross", "cross_dot", "circle", "circle_cross", "t"]

COLOR_PRESETS = [
    ("#FF0000", "Merah"), ("#00FF00", "Hijau"), ("#00FFFF", "Cyan"),
    ("#FFFF00", "Kuning"), ("#FF00FF", "Magenta"), ("#FFFFFF", "Putih"),
    ("#FF8800", "Orange"), ("#0088FF", "Biru"),
]

class PreviewCanvas(QWidget):
    def __init__(self, cfg: CrosshairConfig):
        super().__init__()
        self.cfg = cfg
        self.setFixedSize(220, 220)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px;")

    def update_config(self, cfg: CrosshairConfig):
        self.cfg = cfg
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # grid tipis
        p.setPen(QPen(QColor("#2a2a2a"), 1, Qt.PenStyle.DotLine))
        p.drawLine(self.width()//2, 0, self.width()//2, self.height())
        p.drawLine(0, self.height()//2, self.width(), self.height()//2)
        # crosshair center preview
        p.setOpacity(self.cfg.opacity)
        cx, cy = self.width()//2 + self.cfg.offset_x, self.height()//2 + self.cfg.offset_y
        color = QColor(self.cfg.color)
        outline = QColor(self.cfg.outline_color)

        def draw_line(x1,y1,x2,y2):
            if self.cfg.outline:
                p.setPen(QPen(outline, self.cfg.thickness+2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawLine(x1,y1,x2,y2)
            p.setPen(QPen(color, self.cfg.thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(x1,y1,x2,y2)

        t = self.cfg.type
        if t in ("cross","cross_dot","circle_cross"):
            for x1,y1,x2,y2 in compute_cross_lines(cx, cy, self.cfg):
                draw_line(x1,y1,x2,y2)
        if t in ("dot","cross_dot"):
            x,y,w,h = compute_dot(cx,cy,self.cfg)
            if self.cfg.outline:
                p.setBrush(outline); p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(x-1,y-1,w+2,h+2)
            p.setBrush(color); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(x,y,w,h)
        if t in ("circle","circle_cross"):
            x,y,w,h = compute_circle(cx,cy,self.cfg)
            if self.cfg.outline:
                p.setPen(QPen(outline, self.cfg.thickness+2)); p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(x,y,w,h)
            p.setPen(QPen(color, self.cfg.thickness)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(x,y,w,h)
        if t == "t":
            s,g = self.cfg.size, self.cfg.gap
            draw_line(cx - s - g, cy, cx - g, cy)
            draw_line(cx + g, cy, cx + g + s, cy)
            draw_line(cx, cy - s - g, cx, cy - g)
        # label center
        p.setOpacity(1.0)
        p.setPen(QColor("#666"))
        p.setFont(QFont("Monospace", 7))
        p.drawText(6, self.height()-8, f"{self.cfg.type} {self.cfg.size}px")

class SettingsWindow(QWidget):
    configChanged = pyqtSignal(object)  # emit CrosshairConfig
    toggleRequested = pyqtSignal()
    quitRequested = pyqtSignal()

    def __init__(self, cfg: CrosshairConfig, overlay=None):
        super().__init__()
        self.cfg = cfg
        self.overlay = overlay
        self.setWindowTitle("Cachy Crosshair — Settings")
        self.setWindowIcon(QIcon.fromTheme("crosshair"))
        self.resize(820, 560)
        self.setMinimumSize(780, 520)

        # Layout utama: kiri preview, kanan controls
        root = QHBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(16,16,16,16)

        # === LEFT: Preview + presets ===
        left = QVBoxLayout()
        left.setSpacing(12)

        self.canvas = PreviewCanvas(self.cfg)
        left.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)

        # color presets row
        colorRow = QHBoxLayout()
        colorRow.addWidget(QLabel("Warna cepat:"))
        for hexc, _name in COLOR_PRESETS:
            b = QPushButton()
            b.setFixedSize(26,26)
            b.setStyleSheet(f"background:{hexc}; border-radius:13px; border:2px solid #333;")
            b.clicked.connect(lambda _, c=hexc: self.set_color(c))
            colorRow.addWidget(b)
        colorRow.addStretch()
        left.addLayout(colorRow)

        # preset grid
        presetBox = QGroupBox("Preset")
        pg = QGridLayout(presetBox)
        self.presetCombo = QComboBox()
        self.refresh_presets()
        self.presetCombo.currentTextChanged.connect(self.on_preset_selected)
        btnSave = QPushButton("💾 Save")
        btnSave.clicked.connect(self.save_current_preset)
        btnExport = QPushButton("📤 Export JSON")
        btnExport.clicked.connect(self.export_json)
        btnImport = QPushButton("📥 Import")
        btnImport.clicked.connect(self.import_json)
        pg.addWidget(self.presetCombo, 0, 0, 1, 2)
        pg.addWidget(btnSave, 1, 0)
        pg.addWidget(btnExport, 1, 1)
        pg.addWidget(btnImport, 2, 0, 1, 2)
        left.addWidget(presetBox)

        # live info
        self.infoLabel = QLabel(f"Config: {self.cfg.type} • {self.cfg.color} • {self.cfg.size}px • {int(self.cfg.opacity*100)}%")
        self.infoLabel.setStyleSheet("color:#888; font-size:11px;")
        left.addWidget(self.infoLabel)

        # control buttons
        btnRow = QHBoxLayout()
        self.btnToggle = QPushButton("👁 Toggle Overlay")
        self.btnToggle.setCheckable(True)
        self.btnToggle.setChecked(True)
        self.btnToggle.clicked.connect(lambda: self.toggleRequested.emit())
        btnQuit = QPushButton("Quit")
        btnQuit.clicked.connect(lambda: self.quitRequested.emit())
        btnRow.addWidget(self.btnToggle)
        btnRow.addWidget(btnQuit)
        left.addLayout(btnRow)

        left.addStretch()
        root.addLayout(left, 0)

        # separator
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine); sep.setStyleSheet("color:#333;")
        root.addWidget(sep)

        # === RIGHT: Controls ===
        right = QVBoxLayout()
        right.setSpacing(10)

        title = QLabel("Pengaturan Crosshair")
        title.setStyleSheet("font-size:16px; font-weight:700;")
        right.addWidget(title)

        # Type
        right.addWidget(QLabel("Jenis:"))
        self.typeCombo = QComboBox()
        self.typeCombo.addItems(PRESET_TYPES)
        self.typeCombo.setCurrentText(self.cfg.type)
        self.typeCombo.currentTextChanged.connect(self.on_type_changed)
        right.addWidget(self.typeCombo)

        # Color picker
        colorBox = QHBoxLayout()
        colorBox.addWidget(QLabel("Warna:"))
        self.colorBtn = QPushButton(self.cfg.color)
        self.colorBtn.setStyleSheet(f"background:{self.cfg.color}; color:{'white' if self.cfg.color!=' #FFFFFF' else 'black'}; padding:6px; border-radius:6px;")
        self.colorBtn.clicked.connect(self.pick_color)
        colorBox.addWidget(self.colorBtn)
        self.outlineCheck = QCheckBox("Outline")
        self.outlineCheck.setChecked(self.cfg.outline)
        self.outlineCheck.toggled.connect(self.on_outline_toggled)
        colorBox.addWidget(self.outlineCheck)
        colorBox.addStretch()
        right.addLayout(colorBox)

        # Outline color
        ocRow = QHBoxLayout()
        ocRow.addWidget(QLabel("Outline:"))
        self.outlineColorBtn = QPushButton(self.cfg.outline_color)
        self.outlineColorBtn.setStyleSheet(f"background:{self.cfg.outline_color}; color:white; padding:4px; border-radius:4px;")
        self.outlineColorBtn.clicked.connect(self.pick_outline_color)
        ocRow.addWidget(self.outlineColorBtn)
        ocRow.addStretch()
        right.addLayout(ocRow)

        # Sliders
        self.sizeSlider = self._slider_row(right, "Ukuran", 2, 60, self.cfg.size, self.on_size)
        self.thickSlider = self._slider_row(right, "Tebal", 1, 10, self.cfg.thickness, self.on_thickness)
        self.gapSlider = self._slider_row(right, "Gap", 0, 20, self.cfg.gap, self.on_gap)
        self.opacitySlider = self._slider_row(right, "Opacity", 10, 100, int(self.cfg.opacity*100), self.on_opacity, suffix="%")
        self.dotSlider = self._slider_row(right, "Center Dot", 2, 10, self.cfg.center_dot_size, self.on_dot)

        # Offset
        offRow = QHBoxLayout()
        offRow.addWidget(QLabel("Offset X:"))
        self.offX = QSpinBox(); self.offX.setRange(-200,200); self.offX.setValue(self.cfg.offset_x); self.offX.valueChanged.connect(self.on_offx)
        offRow.addWidget(self.offX)
        offRow.addWidget(QLabel("Y:"))
        self.offY = QSpinBox(); self.offY.setRange(-200,200); self.offY.setValue(self.cfg.offset_y); self.offY.valueChanged.connect(self.on_offy)
        offRow.addWidget(self.offY)
        offRow.addStretch()
        right.addLayout(offRow)

        right.addStretch()

        # Bottom actions
        bottom = QHBoxLayout()
        btnReset = QPushButton("Reset Default")
        btnReset.clicked.connect(self.reset_default)
        btnApply = QPushButton("💾 Simpan & Apply")
        btnApply.setStyleSheet("background:#1E90FF; color:white; font-weight:700; padding:8px 16px; border-radius:6px;")
        btnApply.clicked.connect(self.save_and_apply)
        bottom.addWidget(btnReset)
        bottom.addStretch()
        bottom.addWidget(btnApply)
        right.addLayout(bottom)

        root.addLayout(right, 1)

        self._sync_outline_state()

    def _slider_row(self, parent, label, mn, mx, val, cb, suffix="px"):
        row = QHBoxLayout()
        row.addWidget(QLabel(f"{label}:"))
        s = QSlider(Qt.Orientation.Horizontal)
        s.setRange(mn,mx); s.setValue(val); s.setFixedWidth(180)
        s.valueChanged.connect(cb)
        lbl = QLabel(f"{val}{suffix}")
        lbl.setFixedWidth(48)
        lbl.setStyleSheet("color:#aaa;")
        # store label ref via slider property
        s._label = lbl
        s._suffix = suffix
        row.addWidget(s); row.addWidget(lbl); row.addStretch()
        parent.addLayout(row)
        return s

    # --- handlers ---
    def _emit(self):
        self.canvas.update_config(self.cfg)
        self.infoLabel.setText(f"Config: {self.cfg.type} • {self.cfg.color} • {self.cfg.size}px • {int(self.cfg.opacity*100)}%")
        self.configChanged.emit(self.cfg)
        if self.overlay:
            self.overlay.update_config(self.cfg)

    def set_color(self, hexc):
        self.cfg.color = hexc
        self.colorBtn.setText(hexc)
        self.colorBtn.setStyleSheet(f"background:{hexc}; color:white; padding:6px; border-radius:6px;")
        self._emit()

    def pick_color(self):
        c = QColorDialog.getColor(QColor(self.cfg.color), self, "Pilih Warna Crosshair")
        if c.isValid():
            self.set_color(c.name())

    def pick_outline_color(self):
        c = QColorDialog.getColor(QColor(self.cfg.outline_color), self, "Warna Outline")
        if c.isValid():
            self.cfg.outline_color = c.name()
            self.outlineColorBtn.setText(c.name())
            self.outlineColorBtn.setStyleSheet(f"background:{c.name()}; color:white; padding:4px; border-radius:4px;")
            self._emit()

    def on_type_changed(self, t):
        self.cfg.type = t
        self._emit()

    def on_outline_toggled(self, v):
        self.cfg.outline = v
        self._sync_outline_state()
        self._emit()

    def _sync_outline_state(self):
        self.outlineColorBtn.setEnabled(self.cfg.outline)

    def on_size(self, v):
        self.cfg.size = v
        self.sizeSlider._label.setText(f"{v}{self.sizeSlider._suffix}")
        self._emit()
    def on_thickness(self, v):
        self.cfg.thickness = v
        self.thickSlider._label.setText(f"{v}{self.thickSlider._suffix}")
        self._emit()
    def on_gap(self, v):
        self.cfg.gap = v
        self.gapSlider._label.setText(f"{v}{self.gapSlider._suffix}")
        self._emit()
    def on_opacity(self, v):
        self.cfg.opacity = v/100
        self.opacitySlider._label.setText(f"{v}{self.opacitySlider._suffix}")
        self._emit()
    def on_dot(self, v):
        self.cfg.center_dot_size = v
        self.dotSlider._label.setText(f"{v}{self.dotSlider._suffix}")
        self._emit()
    def on_offx(self, v):
        self.cfg.offset_x = v
        self._emit()
    def on_offy(self, v):
        self.cfg.offset_y = v
        self._emit()

    def refresh_presets(self):
        self.presetCombo.clear()
        self.presetCombo.addItems(list_presets() or ["(no presets)"])

    def on_preset_selected(self, name):
        if not name or name.startswith("("):
            return
        try:
            self.cfg = load_preset(name)
            # sync UI
            self.typeCombo.setCurrentText(self.cfg.type)
            self.colorBtn.setText(self.cfg.color)
            self.colorBtn.setStyleSheet(f"background:{self.cfg.color}; color:white; padding:6px; border-radius:6px;")
            self.outlineCheck.setChecked(self.cfg.outline)
            self.outlineColorBtn.setText(self.cfg.outline_color)
            self.sizeSlider.setValue(self.cfg.size)
            self.thickSlider.setValue(self.cfg.thickness)
            self.gapSlider.setValue(self.cfg.gap)
            self.opacitySlider.setValue(int(self.cfg.opacity*100))
            self.dotSlider.setValue(self.cfg.center_dot_size)
            self.offX.setValue(self.cfg.offset_x)
            self.offY.setValue(self.cfg.offset_y)
            self._emit()
        except Exception as e:
            QMessageBox.warning(self, "Preset Error", str(e))

    def save_current_preset(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Preset", "Nama preset:")
        if ok and name:
            save_preset(name, self.cfg)
            self.refresh_presets()
            QMessageBox.information(self, "Saved", f"Preset '{name}' disimpan!")

    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export JSON", f"{self.cfg.type}.json", "JSON (*.json)")
        if path:
            with open(path, "w") as f:
                json.dump(self.cfg.to_dict(), f, indent=2)
            QMessageBox.information(self, "Export", f"Tersimpan ke {path}")

    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import JSON", "", "JSON (*.json)")
        if path:
            try:
                with open(path) as f:
                    from core.painter import CrosshairConfig
                    self.cfg = CrosshairConfig.from_dict(json.load(f))
                    self._emit()
                    QMessageBox.information(self, "Import", "Berhasil load!")
            except Exception as e:
                QMessageBox.warning(self, "Import Error", str(e))

    def save_and_apply(self):
        save_config(self.cfg)
        QMessageBox.information(self, "Saved", "Config disimpan ke ~/.config/cachy-crosshair/config.json")
        self._emit()

    def reset_default(self):
        from core.painter import CrosshairConfig
        self.cfg = CrosshairConfig()
        self.typeCombo.setCurrentText(self.cfg.type)
        self.set_color(self.cfg.color)
        self.sizeSlider.setValue(self.cfg.size)
        self.thickSlider.setValue(self.cfg.thickness)
        self.gapSlider.setValue(self.cfg.gap)
        self.opacitySlider.setValue(int(self.cfg.opacity*100))
        self._emit()
