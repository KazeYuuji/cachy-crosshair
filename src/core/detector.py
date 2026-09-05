"""
core/detector.py — Auto-detect DE & Wayland/X11
"""
import os

def detect_session():
    return {
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP", ""),
        "session_type": os.environ.get("XDG_SESSION_TYPE", ""),
        "wayland_display": os.environ.get("WAYLAND_DISPLAY", ""),
        "display": os.environ.get("DISPLAY", ""),
    }

def detect_backend(preferred: str = "auto") -> str:
    """Return 'qt' | 'gtk' | 'tauri'"""
    if preferred != "auto":
        return preferred
    info = detect_session()
    desktop = info["desktop"]
    session = info["session_type"]
    wayland = bool(info["wayland_display"])

    if "KDE" in desktop:
        return "qt"  # KDE → Qt paling native
    if any(x in desktop for x in ["Hyprland", "sway", "GNOME"]):
        return "gtk" if wayland else "qt"
    if session == "wayland" and wayland:
        # Wayland generic → coba qt dulu, fallback gtk
        return "qt"
    if session == "x11":
        return "qt"
    return "tauri"  # fallback universal

def explain():
    info = detect_session()
    backend = detect_backend()
    print(f"[DETECT] DESKTOP={info['desktop']} SESSION={info['session_type']} WAYLAND={info['wayland_display']}")
    print(f"[DETECT] → backend auto = {backend}")
    return backend
