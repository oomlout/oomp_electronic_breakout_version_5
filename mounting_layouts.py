"""M6-clear OOBB mounting margins; coordinates remain relative to PCB centre."""
import math
from mounting_geometry import normalize_kwargs

LAYOUTS = ('full_wrap', 'short_sides', 'long_side')
LABELS = {'full_wrap': 'Full wrap', 'short_sides': 'Two short sides', 'long_side': 'One long side'}
PITCH = 15.0
HEAD_RADIUS = 6.5
EDGE = 7.0


def supports(kwargs):
    points = kwargs.get('mounting_holes', [])
    names = kwargs.get('mounting_hole_radius_names')
    return [(float(p[0]), float(p[1]), float((names[i] if names else kwargs.get('mounting_hole_radius_name', 'm3')).replace('m', '').replace('_', '.')) + .75)
            for i, p in enumerate(points)]


def dimensions(**kwargs):
    k = normalize_kwargs(kwargs)
    half = [float(k.get('breakout_pcb_width', 49))/2, float(k.get('breakout_pcb_height', 38))/2]
    for x, y, radius in supports(k):
        half[0] = max(half[0], abs(x) + radius)
        half[1] = max(half[1], abs(y) + radius)
    result = []
    for axis, h in zip(('width', 'height'), half):
        span = 2 * (h + HEAD_RADIUS) + max(0, k.get(f'breakout_pcb_{axis}_extra', 0))
        result.append(max(3, math.ceil((span - 1e-9) / PITCH) + 1))
    return tuple(result)


def adapter_positions(width, height):
    x = 0 if width % 2 else PITCH / 2
    y = 0 if height % 2 else PITCH / 2
    if width >= height:
        delta = (width - 3) * PITCH / 2
        return ([(-delta, y, False)] if width >= 6 else []) + [(delta, y, False)]
    delta = (height - 3) * PITCH / 2
    return ([(x, -delta, True)] if height >= 6 else []) + [(x, delta, True)]


def plan(**kwargs):
    k = normalize_kwargs(kwargs)
    variant = k.get('mounting_layout', 'full_wrap')
    if variant not in LAYOUTS:
        raise ValueError(f'Unknown mounting_layout: {variant}')
    width, height = dimensions(**k)
    pcb = [float(k.get('breakout_pcb_width', 49)), float(k.get('breakout_pcb_height', 38))]
    xs = [(i - (width - 1)/2) * PITCH for i in range(width)]
    ys = [(i - (height - 1)/2) * PITCH for i in range(height)]
    full = [xs[0]-EDGE, xs[-1]+EDGE, ys[0]-EDGE, ys[-1]+EDGE]
    bounds = [-pcb[0]/2-3, pcb[0]/2+3, -pcb[1]/2-3, pcb[1]/2+3]
    for x, y, radius in supports(k):
        bounds = [min(bounds[0], x-radius-1.5), max(bounds[1], x+radius+1.5),
                  min(bounds[2], y-radius-1.5), max(bounds[3], y+radius+1.5)]
    # Keep all 44 mm wire-holder attachment footprints when trimming margins.
    adapters = adapter_positions(width, height) if k.get('wire_adapter', False) else []
    for x, y, _ in adapters:
        bounds = [min(bounds[0], x-22), max(bounds[1], x+22), min(bounds[2], y-22), max(bounds[3], y+22)]
    portrait = pcb[0] <= pcb[1]  # Square boards: short sides are +/-Y; long side is +X.
    edges = ('left', 'right', 'bottom', 'top') if variant == 'full_wrap' else (
        ('bottom', 'top') if portrait else ('left', 'right')) if variant == 'short_sides' else (
        ('right',) if portrait else ('top',))
    # Tangential stations within the PCB span, with at least two on each edge.
    for grid, extent, lo, hi in ((xs, pcb[0]/2, 0, 1), (ys, pcb[1]/2, 2, 3)):
        tangential = [p for p in grid if abs(p) <= extent + 1e-9]
        if len(tangential) < 2:
            tangential = sorted(grid, key=lambda p: (abs(p), p))[:2]
        bounds[lo] = min(bounds[lo], min(tangential)-EDGE)
        bounds[hi] = max(bounds[hi], max(tangential)+EDGE)
    if variant == 'full_wrap':
        bounds = full[:]
    else:
        for side, index in (('left', 0), ('right', 1), ('bottom', 2), ('top', 3)):
            if side in edges:
                bounds[index] = full[index]
    stations = set()
    for side in edges:
        if side in ('top', 'bottom'):
            y = ys[-1] if side == 'top' else ys[0]
            stations.update((x, y) for x in xs if bounds[0]+EDGE-1e-8 <= x <= bounds[1]-EDGE+1e-8)
        else:
            x = xs[-1] if side == 'right' else xs[0]
            stations.update((x, y) for y in ys if bounds[2]+EDGE-1e-8 <= y <= bounds[3]-EDGE+1e-8)
    half_stations = set()
    for x, y in stations:
        for dx, dy in ((PITCH, 0), (0, PITCH)):
            if (x+dx, y+dy) in stations:
                half_stations.add((x+dx/2, y+dy/2))
    result = dict(layout=variant, label=LABELS[variant], grid_units=[width,height], pcb_mm=pcb,
                  bounds_mm=bounds, m6_centres_mm=sorted(stations), m3_centres_mm=sorted(half_stations),
                  m6_hole_diameter_mm=6.5, head_clear_diameter_mm=13, edges=list(edges),
                  adapter_positions=adapters)
    audit(result, k)
    return result


def audit(layout, kwargs):
    bounds, pcb = layout['bounds_mm'], layout['pcb_mm']
    points = layout['m6_centres_mm']
    if len(points) < 2:
        raise ValueError('Each layout requires at least two M6 mounting stations')
    for x, y in points:
        distance = math.hypot(max(abs(x)-pcb[0]/2, 0), max(abs(y)-pcb[1]/2, 0))
        if distance < HEAD_RADIUS - 1e-7:
            raise ValueError('M6 head/nut envelope intersects the PCB')
        for sx, sy, radius in supports(kwargs):
            if math.hypot(x-sx, y-sy) < HEAD_RADIUS + radius - 1e-7:
                raise ValueError('M6 head/nut envelope intersects a PCB support')
        if min(x-bounds[0], bounds[1]-x, y-bounds[2], bounds[3]-y) < EDGE - 1e-7:
            raise ValueError('M6 station lacks its plate edge margin')
    return True
