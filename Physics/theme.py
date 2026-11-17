DARK = {
    "window": "#0b1424",
    "panel": "#101d31",
    "panel_alt": "#14243b",
    "workspace": "#0a1322",
    "grid": "#182943",
    "text": "#d8e1ed",
    "muted": "#8293aa",
    "border": "#263a55",
    "hover": "#1a304d",
    "accent": "#7f9fca",
    "selected": "#9bb9df",
    "component": "#c2d0e1",
    "danger": "#873d4b",
}

LIGHT = {
    "window": "#e7edf4",
    "panel": "#f4f7fb",
    "panel_alt": "#dce5ef",
    "workspace": "#edf2f7",
    "grid": "#d7e0eb",
    "text": "#1c2b40",
    "muted": "#667991",
    "border": "#c4d0de",
    "hover": "#dce7f2",
    "accent": "#456b9b",
    "selected": "#315f98",
    "component": "#243a55",
    "danger": "#a84c58",
}

CURRENT = dict(DARK)


def set_current(colors):
    CURRENT.clear()
    CURRENT.update(colors)


def color(name):
    return CURRENT[name]
