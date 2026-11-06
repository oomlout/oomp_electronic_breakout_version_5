
import copy
import itertools

from requests import options

from oomp_populate_helper import build_oomp_id, write_extras


def get_options(**kwargs):
    
    options = []

    #input
    if True:
        import working_oomp_populate_input_remote_control
        options.extend(working_oomp_populate_input_remote_control.main(**kwargs))
    #output
    if True:
        import working_oomp_populate_output
        options.extend(working_oomp_populate_output.main(**kwargs))
    #power
    if True:
        import working_oomp_populate_power
        options.extend(working_oomp_populate_power.main(**kwargs))
    #microcontroller
    if True:
        import working_oomp_populate_microcontroller
        options.extend(working_oomp_populate_microcontroller.main(**kwargs))

    # Researched I2C peripherals and the separately identified analog ADXL335.
    import working_oomp_populate_i2c
    options.extend(working_oomp_populate_i2c.main(**kwargs))
    
###### populate taxonomy details and oobb details
    if True:
        for option in options:       
            # Explicit catalogues supply fixed taxonomy, variants and output details.
            if option.get("item_kind") == "breakout" and (
                option.get("type_1") == "microcontroller"
                or option.get("taxonomy_schema") == "breakout_function_v1"
            ):
                continue
            option["taxonomy_1"] = f"electronic"  
            option["taxonomy_2"] = f"breakout"             
            count = 3
            value_name = "type_1"
            value = option.get(value_name, None)
            option[f"taxonomy_{count}"] = f"{value}"
            count += 1
            if "type_2" in option:
                value_name = "type_2"
                value = option.get(value_name, None)
                option[f"taxonomy_{count}"] = f"{value}"
                count += 1
            if "type_3" in option:
                value_name = "type_3"
                value = option.get(value_name, None)
                option[f"taxonomy_{count}"] = f"{value}"
                count += 1
            if "type_4" in option:
                value_name = "type_4"
                value = option.get(value_name, None)
                option[f"taxonomy_{count}"] = f"{value}"
                count += 1
            value_name = "breakout_description"
            value = option.get(value_name, None)
            option[f"taxonomy_{count}"] = f"{value}"
            count += 1
            if "manufacturer" in option:
                value_name = "manufacturer"
                value = option.get(value_name, None)
                option[f"taxonomy_14"] = f"{value}"            
            if "part_number" in option:
                value_name = "part_number"
                value = option.get(value_name, None)
                option[f"taxonomy_15"] = f"{value}"
            #oobb details
            if True:
                pass
                oobb_details = {}
                #taxonomy_4 hole_cover
                oobb_details["oobb_name"] = "mounting_plate_default"
                oobb_details.update(option)
                oobb_details_wire = copy.deepcopy(oobb_details)
                oobb_details_wire["oobb_name"] = "mounting_plate_oobb"
                oobb_details_wire["scad_output"] = "working_oobb"
                option["oobb_details"] = [oobb_details, oobb_details_wire]
            #svg details
            if False:
                pass
                svg_details = {}
                svg_details["svg_name"] = option_type
                svg_details["svg_width"] = option.get("width", None)            
                svg_details["svg_height"] = option.get("height", None)
                option["svg_details"] = svg_details
    
    #load the options into full list
    extras = []
    for option in options:
        extra = {}
        extra.update(option)
        extras.append(extra)

    
    ######### add notes from an id string
    import working_oomp_populate_extra_detail
    working_oomp_populate_extra_detail.main(extras=extras)


    if kwargs.get("apply_mounting", True):
        from working_oomp_populate_mounting import apply_mounting
        apply_mounting(extras)
    from mounting_variants import apply_variants
    apply_variants(extras)
    return extras


def main(**kwargs):
    extras = get_options(**kwargs)
    selected = kwargs.get('part_ids')
    if selected is not None:
        selected = {selected} if isinstance(selected, str) else set(selected)
        extras = [e for e in extras if build_oomp_id(e) in selected]
        missing = selected - {build_oomp_id(e) for e in extras}
        if missing:
            raise ValueError('Unknown populate part IDs: ' + ', '.join(sorted(missing)))
    write_extras(extras)
    return extras



# Call main automatically
if __name__ == "__main__":
    main()
