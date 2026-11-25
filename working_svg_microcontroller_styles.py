"""Named stylesheet for board drawings; dimensions are in millimetres."""

import copy

STYLES = {
    "board": {
        "color": "#22685b",
        "stroke": "#17483e",
        "stroke_width": 0.25,
    },
    "pad": {
        "color": "#e9bd57",
        "stroke": "#805d12",
        "stroke_width": 0.15,
    },
    "pad.analog": {
        "color": "#ab8fe0",
    },
    "pad.power": {
        "color": "#eea06c",
    },
    "pad.ground": {
        "color": "#b9c4c9",
    },
    "pad.reserved": {
        "color": "#d7d7d7",
        "stroke": "#a84848",
        "stroke_width": 0.3,
    },
    "hole": {
        "color": "#ffffff",
        "stroke": "#8c7948",
        "stroke_width": 0.18,
    },
    "label": {
        "color": "#203b44",
        "stroke": "none",
        "stroke_width": 0,
        "font": "DejaVu Sans, Arial, sans-serif",
        "size": 1.35,
        "halign": "center",
        "valign": "center",
    },
    "label.title": {
        "size": 2.1,
    },
    "label.detail": {
        "size": 1.2,
        "color": "#52666b",
    },
    "label.board": {
        "color": "#ffffff",
        "size": 1.4,
    },
}


def get_stylesheet(**kwargs):
    return copy.deepcopy(STYLES)
