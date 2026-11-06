import oomp
import oomp_helper
import copy
import oomlout_roboclick

def main(**kwargs):
    load_parts(**kwargs)

def load_parts(**kwargs):
    make_files = kwargs.get("make_files", True)
    #print "loading parts" plus the module name get the module name from the filename using __name__
    print(f"  loading parts {__name__}")
    create_generic(**kwargs)

def create_generic(**kwargs):
    print(f"  loading parts from part_source")
    things = {}    

    # Optional exact selection for a populate file's own records. Do this before
    # reading sources or creating template actions, so other boards stay untouched.
    part_ids = kwargs.get("part_ids")
    if isinstance(part_ids, str):
        part_ids = [part_ids]
    selected_ids = None if part_ids is None else set(part_ids)
    
    #load parts from parts_source directory
    directory_source = "parts_source"
    import os
    if not os.path.exists(directory_source):
        print(f"      directory {directory_source} does not exist, creating it")
        #create it
        os.makedirs(directory_source)
    directories = os.listdir(directory_source)
    if selected_ids is not None:
        missing = selected_ids.difference(directories)
        if missing:
            raise FileNotFoundError("Missing parts_source records: " + ", ".join(sorted(missing)))
    for directory  in directories:
        if selected_ids is not None and directory not in selected_ids:
            continue
        directory_full = f"{directory_source}/{directory}"
        filenames = os.listdir(f"{directory_full}")
        for filename in filenames:
            import yaml
            #go through directories and load working.yaml files
            # only load .yaml files
            if "working.yaml" in filename:
                file_path = os.path.join(directory_full, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    thing_details = {}
                    for deet in data:
                        thing_details[deet] = data[deet]
                    things[directory] = thing_details
    
    
    if selected_ids is not None:
        missing = selected_ids.difference(things)
        if missing:
            raise FileNotFoundError("Missing working.yaml records: " + ", ".join(sorted(missing)))

    parts = []

    for thing in things:
        current = things[thing]                
        #name stuff        
        part = copy.deepcopy(current)
        
        part["name"] = thing
        part["name_space"] = thing.replace("_", " ")
        part["name_proper"] = part["name_space"].title()
        name_proper = part["name_proper"]
        part["name_upper"] = part["name_space"].upper()
        
        folder = oomlout_roboclick.get_directory(part)   
        part["directory"] = folder  
        url_chat = oomlout_roboclick.get_url(part)   
        part["url_chat"] = url_chat
        files_to_trace = []
        count = 0

        #mode_ai_wait = "fast"
        mode_ai_wait = "slow"

        #load working_manual and add it to surrent if availabe
        if True:
            directory_manual = f"{part['directory']}/working_manual.yaml"
            if os.path.exists(directory_manual):
                with open(directory_manual, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    for deet in data:
                        part[deet] = data[deet]

        #working with variables
        if True:
            if "content" in part:
                content_string = ", ".join(part["content"])
                print(f"      content: {content_string}")
                part["content_string"] = content_string

        #icon
        if False:
            count += 1     
            icon_detail = f"make {name_proper} cute"
            oomp_helper.add_icon(part=part, count=count, mode_ai_wait=mode_ai_wait, icon_detail=icon_detail)

        
        #image chibi
        test_image_chibi = False
        if test_image_chibi:
            content_string = part.get("content_string", "")    
            count += 1
            chibi_detail = f"make {name_proper} cute"
            oomp_helper.add_image_chibi(part=part, count=count, mode_ai_wait=mode_ai_wait, chibi_detail=chibi_detail)       

        #image_from_directory
        if False:
            count += 1
            directory_prompt = f"roboclick\\prompt_1"
            file_name_image = "image_main.png"
            oomp_helper.add_image_from_prompt_directory(part=part, count=count, prompt_folder=directory_prompt, file_name=file_name_image, generate_prompt="", mode_ai_wait=mode_ai_wait)


        # all images
        test_image_all = False
        if test_image_all:
            content_string = part.get("content_string", "")    
            count += 1
            image_detail = f"make {name_proper} cute"
            oomp_helper.add_all_default_prompt_images(part=part, count=count, mode_ai_wait=mode_ai_wait, image_detail=image_detail)

        #folder_project = "helen_personal_chart_bribe_bank"

        #jinja_template replace
        if True:
            templates = []
            templates.append({"template_folder": "default"})
            #templates.append({"template_folder": "source_file\\template_jinja\\template_jinja_postcard_image_main_oomlout_152_4_mm_101_6_mm", "output_filename": "postcard_oomp.svg"})
            convert_to_pdf = False
            convert_to_png = False
            count = oomp_helper.add_jinja_template(part=part, templates=templates, mode_ai_wait=mode_ai_wait, count=count, convert_to_pdf=convert_to_pdf, convert_to_png=convert_to_png)
        #prompt bubble letter        
        if False:
            count = oomp_helper.add_image(
                part=part,
                folder_project=folder_project,
                files_to_trace=files_to_trace,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )

        #prompt image theme
        if False:
            count = oomp_helper.add_prompt_image(
                part=part,
                folder_project=folder_project,
                prompt_folder="prompt_image_main_1",
                file_name="image_main_1.png",
                files_to_trace=files_to_trace,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )
        #value
        if False:
            count = oomp_helper.add_value_images(
                part=part,
                folder_project=folder_project,
                files_to_trace=files_to_trace,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )
            

        #cover_background
        #prompt image
        if False:
            count = oomp_helper.add_cover_background(
                part=part,
                folder_project=folder_project,
                files_to_trace=files_to_trace,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )
       
        #internal border
        #prompt image
        if False:
            count = oomp_helper.add_prompt_image(
                part=part,
                folder_project=folder_project,
                prompt_folder="prompt_inside_border_1",
                file_name="image_inside_border.png",
                files_to_trace=files_to_trace,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )

        #logo back
        #prompt image
        if False:
            count = oomp_helper.add_prompt_image(
                part=part,
                folder_project=folder_project,
                prompt_folder="prompt_logo_back_1",
                file_name="image_logo_back.png",
                files_to_trace=files_to_trace,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )

        #trace
        if False:  
            count = oomp_helper.trace_files(
                part=part,
                files_to_trace=files_to_trace,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )

        #make_card
        if False:
            count = oomp_helper.make_card(part=part, folder_project=folder_project, count=count)

        #research
        if False:
            count = oomp_helper.add_research(
                part=part,
                folder_project=folder_project,
                mode_ai_wait=mode_ai_wait,
                count=count,
            )


        parts.append(part)
    



    generation_kwargs = {key: value for key, value in kwargs.items() if key != "part_ids"}
    if selected_ids is None:
        oomp.add_parts(parts, **generation_kwargs)
    else:
        # The shared add_parts starts unjoined threads. A targeted build must
        # finish its writes and propagate failures before returning to its caller.
        for part in parts:
            part_kwargs = copy.deepcopy(part)
            part_kwargs.update(generation_kwargs)
            oomp.add_part(**part_kwargs)

    #dd file copy
    for part in parts:
        file_copies = part.get("file_copy", [])
        if file_copies != []:
            for file_copy in file_copies:
                directory = part.get("directory", "")
                if directory != "":
                    file_source = f'{file_copy["file_source"]}'
                    file_destination = f'{directory}\\{file_copy["file_destination"]}'
                    import shutil
                    print(f"      copying {file_source} to {file_destination}")
                    try:
                        shutil.copyfile(file_source, file_destination)
                    except Exception as e:
                        print(f"      error copying file: {e}") 

    if selected_ids is None:
        import time
        time.sleep(2)



if __name__ == "__main__":
    # run the function
    load_parts()    
    
