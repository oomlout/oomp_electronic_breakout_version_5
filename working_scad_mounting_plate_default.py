import copy
import oobb
import yaml
import os
import scad_help
from mounting_geometry import normalize_kwargs
import mounting_layouts

def get_plate_dimensions(**kwargs):
    """Size the plate in OOBB units, adding optional per-axis extras in mm."""
    return mounting_layouts.dimensions(**kwargs)

def get_base(thing, **kwargs):
    kwargs = normalize_kwargs(kwargs)
    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("depth", 3)                    
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")
    
    breakout_pcb_width = kwargs.get("breakout_pcb_width", 49)
    breakout_pcb_height = kwargs.get("breakout_pcb_height", 38)
    mounting_holes = kwargs.get("mounting_holes", [])
    mounting_hole_radius_name = kwargs.get("mounting_hole_radius_name", "m3")

    width, height = get_plate_dimensions(**kwargs)
    kwargs["width"] = width
    kwargs["height"] = height
    layout = mounting_layouts.plan(**kwargs)
    #add plate
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"oobb_plate"
        left, right, bottom, top = layout['bounds_mm']
        p3['width'] = (right-left+1)/15
        p3['height'] = (top-bottom+1)/15
        p3["depth"] = depth
        #p3["holes"] = True         uncomment to include default holes
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)         
        pos1[0] += (left+right)/2
        pos1[1] += (bottom+top)/2
        p3["pos"] = pos1
        oobb.append_full(thing,**p3)
    
    # Keep the 15 mm M6 grid and its optional, empty half-grid M3 holes.
    for key, radius_name in [('m6_centres_mm', 'm6'), ('m3_centres_mm', 'm3')]:
        for x, y in layout[key]:
            oobb.append_full(thing, type='negative', shape='oobb_hole', radius_name=radius_name,
                             depth=depth+2, pos=[pos[0]+x, pos[1]+y, pos[2]-1])

    # Add PCB standoffs; the default lift is 3 mm.
    mounting_holes = kwargs.get("mounting_holes", [])
    radius_names = kwargs.get("mounting_hole_radius_names")
    if radius_names is not None and len(radius_names) != len(mounting_holes):
        raise ValueError("Each mounting hole must have a screw size")
    for index, hole in enumerate(mounting_holes):
        hole_kwargs = dict(kwargs)
        if radius_names is not None:
            hole_kwargs["mounting_hole_radius_name"] = radius_names[index]
        add_mounting_hole(thing, hole, **hole_kwargs)


    #add a test screw_countersunk
    if False:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "p"
        p3["shape"] = f"screw_countersunk"
        p3["depth"] = depth
        p3["radius_name"] = "m3"
        pos1 = copy.deepcopy(pos)         
        pos1[2] += depth
        p3["pos"] = pos1
        p3["m"] = "#"
        oobb.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)

def add_mounting_hole(thing, hole, **kwargs):
    pos = kwargs.get("pos", [0, 0, 0])
    depth = kwargs.get("depth", 3)
    lift = kwargs.get("mounting_lift", 3)
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "negative"
    p3["shape"] = f"oobb_screw_countersunk"
    p3["depth"] = depth + lift
    mounting_hole_radius_name = kwargs.get("mounting_hole_radius_name", "m3")
    p3["radius_name"] = mounting_hole_radius_name
    pos1 = copy.deepcopy(pos)
    pos1[0] += hole[0]
    pos1[1] += hole[1]
    p3["pos"] = pos1
    rot1 = copy.deepcopy(kwargs.get("rot", [0, 0, 0]))
    rot1[1] += 180
    p3["rot"] = rot1
    oobb.append_full(thing, **p3)
    #add_cylinder
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "positive"
    p3["shape"] = f"oobb_cylinder"
    dep = lift
    p3["depth"] = dep
    radius = float(mounting_hole_radius_name.replace("m", "").replace("_",".")) + 1.5/2
    p3["radius"] = radius
    pos1 = copy.deepcopy(pos)
    pos1[0] += hole[0]
    pos1[1] += hole[1]
    pos1[2] += dep/2 + depth
    p3["pos"] = pos1
    oobb.append_full(thing, **p3)
