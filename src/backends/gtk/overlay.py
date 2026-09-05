#!/usr/bin/env python3
"""
backends/gtk/overlay.py — Backend B untuk Hyprland/Sway/GNOME + KDE Gaming
GTK4 + gtk4-layer-shell (stay above fullscreen, termasuk Sober/Roblox)
Jika gtk4-layer-shell tidak ada, fallback ke window biasa (masih bisa di X11)

Usage standalone:
  python src/backends/gtk/overlay.py
  python src/backends/gtk/overlay.py --type cross_dot --color "#FF0000"
  CACHY_CROSSHAIR_DEBUG=1 python src/backends/gtk/overlay.py

Dipanggil dari main_gui Gaming Mode via subprocess
"""
import sys, os, json, argparse, signal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, Gdk, GLib
    HAS_GTK = True
except Exception as e:
    print(f"[GTK] Gtk4 not available: {e}")
    HAS_GTK = False

# Try GtkLayerShell (gtk4-layer-shell)
HAS_LAYER = False
GtkLayerShell = None
try:
    gi.require_version('GtkLayerShell', '0.1')
    from gi.repository import GtkLayerShell
    HAS_LAYER = True
    print("[GTK] GtkLayerShell 0.1 available")
except Exception as e:
    # Try alternative namespace (some distros use 0.8?)
    try:
        gi.require_version('Gtk4LayerShell', '1.0')
        from gi.repository import Gtk4LayerShell as GtkLayerShell
        HAS_LAYER = True
        print("[GTK] Gtk4LayerShell 1.0 available")
    except Exception as e2:
        print(f"[GTK] LayerShell not available: {e} / {e2} — will fallback to normal window (may hide behind fullscreen)")
        HAS_LAYER = False

from core.painter import CrosshairConfig
from core.config import load_config

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--type", dest="type", default=None)
    p.add_argument("--color", default=None)
    p.add_argument("--size", type=int, default=None)
    p.add_argument("--config", type=str, default=None, help="path to config.json")
    return p.parse_args()

class GtkCrosshairWindow(Gtk.Window):
    def __init__(self, cfg: CrosshairConfig):
        super().__init__()
        self.cfg = cfg
        self.debug_bg = os.environ.get("CACHY_CROSSHAIR_DEBUG","0")=="1"
        self.set_title("cachy-crosshair-gtk")
        # Window setup
        self.set_decorated(False)
        # For GTK4 layer-shell, we need to set default size to cover screen
        # Get primary monitor geometry via Gdk
        try:
            display = Gdk.Display.get_default()
            if display:
                monitors = display.get_monitors()
                if monitors and monitors.get_n_items()>0:
                    mon = monitors.get_item(0)
                    geo = mon.get_geometry()
                    print(f"[GTK] monitor 0: {geo.width}x{geo.height} at {geo.x},{geo.y}")
                    self.set_default_size(geo.width, geo.height)
                else:
                    self.set_default_size(1366, 768)
            else:
                self.set_default_size(1366,768)
        except Exception as e:
            print(f"[GTK] monitor detection err {e}")
            self.set_default_size(1366,768)

        # Drawing area
        self.area = Gtk.DrawingArea()
        self.area.set_draw_func(self.do_draw)
        self.area.set_hexpand(True)
        self.area.set_vexpand(True)
        self.set_child(self.area)

        # Layer-shell setup (must be before show)
        if HAS_LAYER and GtkLayerShell:
            try:
                GtkLayerShell.init_for_window(self)
                GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
                # anchor to all edges to cover fullscreen
                for edge in [GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT, GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM]:
                    GtkLayerShell.set_anchor(self, edge, True)
                GtkLayerShell.set_exclusive_zone(self, -1)
                GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)
                # For gtk4-layer-shell, also set namespace for KWin debug
                try:
                    GtkLayerShell.set_namespace(self, "cachy-crosshair")
                except: pass
                print("[GTK] LayerShell Overlay anchored, exclusive -1, keyboard none — will stay above Sober fullscreen")
            except Exception as e:
                print(f"[GTK] LayerShell setup err {e}")

        # Pass through input? GtkLayerShell doesn't have input passthrough directly, but we can set input region empty
        # For now, we make window not focusable and rely on layer-shell keyboard none
        self.set_can_focus(False)
        self.set_focusable(False)

        # Watch config file for live reload
        self.watch_config()

        self.present()
        print(f"[GTK] Window presented, size {self.get_width()}x{self.get_height()}")

    def watch_config(self):
        cfg_path = Path.home() / ".config" / "cachy-crosshair" / "config.json"
        def on_change(monitor, file, other, event):
            if event == 1: # CHANGED
                try:
                    with open(cfg_path) as f:
                        data = json.load(f)
                        self.cfg = CrosshairConfig.from_dict(data)
                        print(f"[GTK] config reload {self.cfg.type} {self.cfg.color}")
                        self.area.queue_draw()
                except Exception as e:
                    print(f"[GTK] reload err {e}")
        try:
            from gi.repository import Gio
            if cfg_path.exists():
                mon = Gio.File.new_for_path(str(cfg_path)).monitor_file(Gio.FileMonitorFlags.NONE, None)
                mon.connect("changed", on_change)
        except Exception as e:
            print(f"[GTK] monitor err {e}")

    def update_config(self, cfg):
        self.cfg = cfg
        self.area.queue_draw()

    def do_draw(self, area, cr, width, height):
        # cr is cairo.Context
        cx = width // 2 + self.cfg.offset_x
        cy = height // 2 + self.cfg.offset_y

        # debug bg
        if self.debug_bg:
            cr.set_source_rgba(1,0,0,0.08)
            cr.rectangle(0,0,width,height)
            cr.fill()
            cr.set_source_rgba(1,1,0,1)
            cr.select_font_face("Monospace")
            cr.set_font_size(12)
            cr.move_to(20,30)
            cr.show_text(f"GTK DEBUG {width}x{height} {self.cfg.type} {self.cfg.color} size={self.cfg.size}")

        # helper to parse hex color
        def hex_to_rgba(hexc, alpha=1.0):
            hexc = hexc.lstrip("#")
            r = int(hexc[0:2],16)/255
            g = int(hexc[2:4],16)/255
            b = int(hexc[4:6],16)/255
            return (r,g,b,alpha)

        r,g,b,_ = hex_to_rgba(self.cfg.color)
        ro,go,bo,_ = hex_to_rgba(self.cfg.outline_color)
        alpha = self.cfg.opacity

        def draw_line(x1,y1,x2,y2):
            if self.cfg.outline:
                cr.set_source_rgba(ro,go,bo,alpha)
                cr.set_line_width(self.cfg.thickness+2)
                cr.set_line_cap(1) # round
                cr.move_to(x1,y1); cr.line_to(x2,y2); cr.stroke()
            cr.set_source_rgba(r,g,b,alpha)
            cr.set_line_width(self.cfg.thickness)
            cr.set_line_cap(1)
            cr.move_to(x1,y1); cr.line_to(x2,y2); cr.stroke()

        from core.painter import compute_cross_lines, compute_circle, compute_dot
        t = self.cfg.type
        if t in ("cross","cross_dot","circle_cross"):
            for x1,y1,x2,y2 in compute_cross_lines(cx,cy,self.cfg):
                draw_line(x1,y1,x2,y2)
        if t in ("dot","cross_dot"):
            x,y,w,h = compute_dot(cx,cy,self.cfg)
            if self.cfg.outline:
                cr.set_source_rgba(ro,go,bo,alpha)
                cr.arc(cx, cy, w/2+1, 0, 6.28)
                cr.fill()
            cr.set_source_rgba(r,g,b,alpha)
            cr.arc(cx, cy, w/2, 0, 6.28)
            cr.fill()
        if t in ("circle","circle_cross"):
            x,y,w,h = compute_circle(cx,cy,self.cfg)
            if self.cfg.outline:
                cr.set_source_rgba(ro,go,bo,alpha)
                cr.set_line_width(self.cfg.thickness+2)
                cr.arc(cx, cy, w/2, 0, 6.28)
                cr.stroke()
            cr.set_source_rgba(r,g,b,alpha)
            cr.set_line_width(self.cfg.thickness)
            cr.arc(cx, cy, w/2, 0, 6.28)
            cr.stroke()
        if t == "t":
            s,g = self.cfg.size, self.cfg.gap
            draw_line(cx - s - g, cy, cx - g, cy)
            draw_line(cx + g, cy, cx + g + s, cy)
            draw_line(cx, cy - s - g, cx, cy - g)

def main():
    if not HAS_GTK:
        print("GTK4 not available — install: sudo pacman -S gtk4 python-gobject")
        sys.exit(1)
    args = parse_args()
    cfg = load_config()
    if args.type: cfg.type = args.type
    if args.color: cfg.color = args.color
    if args.size: cfg.size = args.size
    if args.config and Path(args.config).exists():
        with open(args.config) as f:
            cfg = CrosshairConfig.from_dict(json.load(f))

    print(f"[GTK] starting with {cfg.type} {cfg.color} size={cfg.size} layer={HAS_LAYER}")

    # GTK4 Application
    app = Gtk.Application(application_id="org.cachyos.cachy-crosshair-gtk", flags=0)
    win = None
    def on_activate(a):
        nonlocal win
        win = GtkCrosshairWindow(cfg)
        win.set_application(a)
        win.present()
        # Quit on SIGTERM for subprocess management
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: (app.quit(), True)[1])
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, lambda: (app.quit(), True)[1])

    app.connect("activate", on_activate)
    # Also allow ESC to quit for debug
    exit_code = app.run(None)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
