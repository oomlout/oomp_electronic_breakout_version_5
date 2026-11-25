"""Portable board catalogue assembled from editable chip-family definitions."""

import copy

import working_oomp_populate_microcontroller_rp2040
import working_oomp_populate_microcontroller_rp2350
import working_oomp_populate_microcontroller_esp32
import working_oomp_populate_microcontroller_esp32_c3
import working_oomp_populate_microcontroller_esp32_s2
import working_oomp_populate_microcontroller_esp32_s3
import working_oomp_populate_microcontroller_esp32_c6
import working_oomp_populate_microcontroller_esp32_h2


def main(**kwargs):
    options = []
    options.extend(working_oomp_populate_microcontroller_rp2040.main(**kwargs))
    options.extend(working_oomp_populate_microcontroller_rp2350.main(**kwargs))
    options.extend(working_oomp_populate_microcontroller_esp32.main(**kwargs))
    options.extend(working_oomp_populate_microcontroller_esp32_c3.main(**kwargs))
    options.extend(working_oomp_populate_microcontroller_esp32_s2.main(**kwargs))
    options.extend(working_oomp_populate_microcontroller_esp32_s3.main(**kwargs))
    options.extend(working_oomp_populate_microcontroller_esp32_c6.main(**kwargs))
    options.extend(working_oomp_populate_microcontroller_esp32_h2.main(**kwargs))
    identifiers = set()
    for option in options:
        identifier = get_identifier(option=option)
        if identifier in identifiers:
            raise ValueError("Duplicate microcontroller board: " + identifier)
        identifiers.add(identifier)
        validate(option=option)
        geometry = {
            "breakout_pcb_width": option["breakout_pcb_width"],
            "breakout_pcb_height": option["breakout_pcb_height"],
            "mounting_holes": copy.deepcopy(option["mounting_holes"]),
            "mounting_hole_radius_name": option.get("mounting_hole_radius_name", "m2"),
        }
        option["oobb_details"] = []
        default_plate = copy.deepcopy(geometry)
        default_plate["oobb_name"] = "mounting_plate_default"
        option["oobb_details"].append(default_plate)
        wire_plate = copy.deepcopy(geometry)
        wire_plate["oobb_name"] = "mounting_plate_oobb"
        wire_plate["scad_output"] = "working_oobb"
        option["oobb_details"].append(wire_plate)
    return options


def get_identifier(**kwargs):
    option = kwargs["option"]
    fields = []
    for number in range(1, 16):
        value = option.get("taxonomy_" + str(number), "")
        if value:
            fields.append(value)
    return "_".join(fields)


def get_chips(**kwargs):
    options = []
    options.extend(working_oomp_populate_microcontroller_rp2040.get_chips(**kwargs))
    options.extend(working_oomp_populate_microcontroller_rp2350.get_chips(**kwargs))
    options.extend(working_oomp_populate_microcontroller_esp32_c3.get_chips(**kwargs))
    return options


def validate(**kwargs):
    option = kwargs["option"]
    for number in range(1, 16):
        if not isinstance(option.get("taxonomy_" + str(number)), str):
            raise ValueError("Every taxonomy level must be explicit")
    source_ids = set()
    for source in option["sources"]:
        if source["id"] in source_ids:
            raise ValueError("Duplicate source ID: " + source["id"])
        source_ids.add(source["id"])
    dimensions = option["dimensions_mm"]
    if dimensions["width"] <= 0 or dimensions["height"] <= 0:
        raise ValueError("PCB dimensions must be positive")
    if dimensions["source_id"] not in source_ids:
        raise ValueError("Unknown dimension source")
    physical_pins = set()
    for key, pin in option["pins"].items():
        physical = (pin["connector"], str(pin["number"]))
        if physical in physical_pins:
            raise ValueError("Duplicate physical pad: " + key)
        physical_pins.add(physical)
        if (pin["x_mm"] is None) != (pin["y_mm"] is None):
            raise ValueError("Pin coordinates must be provided as a pair: " + key)
        if pin["source_id"] not in source_ids:
            raise ValueError("Unknown pin source: " + key)
        if (pin.get("gpio") is not None) != (pin["type"] == "gpio"):
            raise ValueError("GPIO type disagrees with mapping: " + key)
        if (pin.get("adc_channel") is not None) != ("analog_input" in pin["capabilities"]):
            raise ValueError("ADC type disagrees with mapping: " + key)
        if pin.get("input_only") and "digital_output" in pin["capabilities"]:
            raise ValueError("Input-only pin cannot drive output: " + key)
    if len(option["mounting_holes"]) != len(option["mounting_hole_details"]):
        raise ValueError("Mounting-hole lists disagree")
    for position, hole in zip(option["mounting_holes"], option["mounting_hole_details"]):
        if position != [hole["x_mm"], hole["y_mm"]] or hole["diameter_mm"] <= 0:
            raise ValueError("Invalid mounting hole")
        if hole["source_id"] not in source_ids:
            raise ValueError("Unknown mounting-hole source")
    validate_default_interfaces(option=option)


def validate_default_interfaces(**kwargs):
    """Check both directions of the exported interface-to-contact relationship."""
    option = kwargs["option"]
    if option.get("interface_defaults_version") != 1:
        raise ValueError("Unknown interface defaults schema")
    interfaces = option["default_interfaces"]
    signals_by_protocol = {
        "uart": {"tx", "rx"},
        "i2c": {"sda", "scl"},
        "spi": {"sck", "mosi", "miso", "ss"},
    }
    if not signals_by_protocol.keys() <= interfaces.keys():
        raise ValueError("Every board needs explicit UART, I2C and SPI default status")
    source_ids = {source["id"] for source in option["sources"]}
    expected_roles = {key: [] for key in option["pins"]}
    for name, interface in interfaces.items():
        protocol = interface["protocol"]
        if protocol not in signals_by_protocol or (name in signals_by_protocol and protocol != name):
            raise ValueError("Invalid default interface protocol: " + name)
        signals = signals_by_protocol[protocol]
        if set(interface["pin_keys"]) != signals or set(interface["signal_status"]) != signals:
            raise ValueError("Incomplete default interface signals: " + name)
        if {key[:-5] for key in interface if key.endswith("_gpio")} != signals:
            raise ValueError("Incomplete default interface GPIO fields: " + name)
        status = interface["status"]
        if status not in ("documented", "unverified"):
            raise ValueError("Invalid default interface status: " + name)
        if not isinstance(interface["notes"], list) or not interface["variant_scope"]:
            raise ValueError("Missing default interface context: " + name)
        if not set(interface["source_ids"]) <= source_ids:
            raise ValueError("Unknown default interface source: " + name)
        if status == "documented":
            if not interface["source_ids"] or not interface["framework"] or not interface["variant"]:
                raise ValueError("Documented defaults need source and framework: " + name)
            if interface["basis"] not in ("framework_defaults", "framework_pin_aliases"):
                raise ValueError("Invalid default interface basis: " + name)
        elif (interface["source_ids"] or interface["framework"] is not None
              or interface["variant"] is not None or interface["basis"] != "unknown"
              or interface["api"] is not None or interface["peripheral"] is not None):
            raise ValueError("Unverified defaults must not imply framework assignments: " + name)
        for signal in signals:
            gpio = interface[signal + "_gpio"]
            if gpio is not None and (type(gpio) is not int or gpio < 0):
                raise ValueError("Invalid default GPIO: " + name + "." + signal)
            pins = interface["pin_keys"][signal]
            expected_pins = [key for key, pin in option["pins"].items() if gpio is not None and pin.get("gpio") == gpio]
            if len(pins) != len(set(pins)) or set(pins) != set(expected_pins):
                raise ValueError("Default interface pin/GPIO mapping disagrees: " + name + "." + signal)
            if status == "unverified":
                if gpio is not None or pins:
                    raise ValueError("Unverified defaults must not assign pins: " + name)
                expected_status = "unverified"
            elif gpio is None:
                expected_status = "not_defined"
            elif not pins:
                expected_status = "not_in_pinout"
            elif all(option["pins"][key].get("contact_scope") == "software_alias_not_unique_physical_pad" for key in pins):
                expected_status = "software_alias_only"
            else:
                expected_status = "mapped"
            if interface["signal_status"][signal] != expected_status:
                raise ValueError("Default interface signal status disagrees: " + name + "." + signal)
            for key in pins:
                expected_roles[key].append({"interface": name, "signal": signal})
    for key, pin in option["pins"].items():
        roles = pin.get("default_interface_roles")
        normalize = lambda values: sorted((value["interface"], value["signal"]) for value in values)
        if roles is None or normalize(roles) != normalize(expected_roles[key]):
            raise ValueError("Pin default interface roles disagree: " + key)
