#!/usr/bin/env python2

from gimpfu import *
from colormath.color_objects import sRGBColor, LabColor, LCHabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
import os

def find_closest_color_in_palette(target_color, search_palette):
    palette_size, colors = pdb.gimp_palette_get_colors(search_palette)
    rgb = sRGBColor(target_color.red, target_color.green, target_color.blue, is_upscaled=False)
    target_color_lab = convert_color(rgb, LabColor)

    # Initialize minimum distance and best match color
    min_distance = float('inf')
    closest_color = None
    closest_color_name = None
    
    # Iterate through each color in the palette
    for i in range(palette_size):
        color_rgb = pdb.gimp_palette_entry_get_color(search_palette, i)  # Get the GimpRGB value by index
        color_name = pdb.gimp_palette_entry_get_name(search_palette, i)  # Get the color name by index
        
        # Calculate Euclidean distance between target color and palette color
        rgb = sRGBColor(color_rgb.red, color_rgb.green, color_rgb.blue, is_upscaled=False)
        color_lab = convert_color(rgb, LabColor)
        
        distance = delta_e_cie1976(target_color_lab, color_lab)
        
        # Update closest color if this one is a better match
        if distance < min_distance:
            min_distance = distance
            closest_color = color_rgb
            closest_color_name = color_name
    
    # Print or return the closest color
    return closest_color_name, closest_color, min_distance

def inksplit(image, drawable, canvas_width, canvas_height, canvas_margin, resolution, location, center_offset, vert_offset, print_width, print_height, generate_ub, ub_threshold, font, font_size, label_spacing, export, do_color_match):
    # Start an undo group, so that all operations can be undone in one go
    original_file_name = os.path.splitext(os.path.basename(image.filename))[0]
    pdb.gimp_image_undo_group_start(image)

    original_layer = image.active_layer
    original_layer.name = "ORIG"

    pdb.gimp_layer_add_alpha(original_layer)

    # Step 1: Adjust scaling
    if print_height or print_width: # Check if either print height or width is specified
        pdb.plug_in_autocrop(image, drawable) # Autocrop the image to remove blank space around it
        pdb.gimp_image_set_resolution(image, resolution, resolution)

        width_orig = pdb.gimp_image_width(image)
        height_orig = pdb.gimp_image_height(image)
        
        if print_width:
            scale_height = (print_width * resolution) / width_orig

        if print_height:
            scale_width = (print_height * resolution) / height_orig

        # Initialize the final scaling factor to 1 (no scaling by default)
        final_scale = 1

        # Determine the final scale based on the smaller of the two scaling factors if both are calculated
        if 'scale_width' in locals() and 'scale_height' in locals():
            if scale_width == scale_height:
                final_scale = scale_width  # Both scales are the same
            elif scale_width < scale_height:
                final_scale = scale_width  # Width scaling factor is smaller, use it
            elif scale_height < scale_width:
                final_scale = scale_height  # Height scaling factor is smaller, use it
        elif 'scale_width' in locals():
            final_scale = scale_width  # Only width scaling is defined
        elif 'scale_height' in locals():
            final_scale = scale_height  # Only height scaling is defined

        # Apply scaling only if final scaling factor is different from 1
        if final_scale != 1:
            pdb.gimp_image_scale(image, width_orig * final_scale, height_orig * final_scale)
            if final_scale > 1:
                pdb.gimp_message("Image was scaled up by a factor of " + "{:.2f}".format(final_scale) + "!")

    # Step 2: Convert to Indexed color palette
    current_palette = pdb.gimp_context_get_palette()  # Get the name of the current palette
    pdb.gimp_image_convert_indexed(image, CONVERT_DITHER_FS, CUSTOM_PALETTE, 0, False, False, current_palette) # Floyd-Steinberg (normal) dithering

    # Step 3: Convert back to RGB - Several operations fail in Indexed mode
    pdb.gimp_image_convert_rgb(image)

    # Step 4: Create Underbase layer
    if generate_ub:
        ub_layer = pdb.gimp_layer_copy(original_layer, True) # Copy original layer
        pdb.gimp_image_add_layer(image, ub_layer, 0)
        ub_layer.name = "UB"
        pdb.gimp_layer_set_lock_alpha(ub_layer, True) # Lock pixels
        pdb.gimp_context_set_foreground((0, 0, 0)) # Set foreground color to black
        pdb.gimp_edit_fill(ub_layer, FOREGROUND_FILL) # Fill the new layer
        pdb.gimp_layer_set_lock_alpha(ub_layer, False) # Allow for removal of dark colors

    pdb.gimp_image_set_active_layer(image, original_layer)
    pdb.gimp_layer_set_lock_alpha(original_layer, True) # Prevent edits

    # Step 6: Extract colors
    palette_size, palette = pdb.gimp_palette_get_colors(current_palette)
    color_layers = [] # Keep track of which colors get generated
    color_matches = [] # Keep track of PMS color matches

    for i in range(palette_size): # For each color in the palette
        color_rgb = pdb.gimp_palette_entry_get_color(current_palette, i)  # Get the GimpRGB value by index
        color_name = pdb.gimp_palette_entry_get_name(current_palette, i)  # Get the color name by index

        # 6.1 Select by color        
        pdb.gimp_context_set_antialias(False)
        pdb.gimp_context_set_feather(False)
        pdb.gimp_context_set_sample_transparent(False)
        pdb.gimp_context_set_sample_merged(False)
        pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, original_layer, color_rgb)  # Use specific color from palette

        if pdb.gimp_selection_is_empty(image): # Skip empty colors
            continue        

        # 6.2 Cut and paste to new layer
        pdb.gimp_edit_cut(original_layer)

        # 6.3 Create a new layer with the same dimensions as the image
        new_layer = pdb.gimp_layer_new(
            image,                       # The image to which the layer will be added
            image.width,                 # Width of the new layer
            image.height,                # Height of the new layer
            RGBA_IMAGE,                  # Type of the new layer (RGB, RGBA, etc.)
            color_name,                  # Name of the new layer
            100,                         # Opacity (0-100)
            0                            # Layer mode (0 for normal)
        )

        # 6.4 Add the new layer to the image
        pdb.gimp_image_insert_layer(image, new_layer, None, 0)
        
        # 6.5 Paste the cut pixels into the new layer
        floating_sel = pdb.gimp_edit_paste(new_layer, False)
        
        # 6.6 Anchor the floating selection to the new layer
        pdb.gimp_floating_sel_anchor(floating_sel)

        # 6.7 Lock new layer alpha
        pdb.gimp_layer_set_lock_alpha(new_layer, True)

        # 6.8 Fill with black
        pdb.gimp_context_set_foreground((0, 0, 0))  # Set foreground color to black
        pdb.gimp_edit_fill(new_layer, FOREGROUND_FILL)  # Fill with black
        
        # 6.9 Remove color from underbase if below lightness threshold
        if generate_ub:
            # Convert RGB to sRGBColor (0-1 scale)
            rgb = sRGBColor(color_rgb.red, color_rgb.green, color_rgb.blue, is_upscaled=False)

            # Convert sRGB to LAB, then to LCH
            lab = convert_color(rgb, LabColor)
            lch = convert_color(lab, LCHabColor)

            # Lightness is in the L component of LCH
            L = lch.lch_l / 100.0 # (0-1 scale)

            # Remove pixels from UB if under threshold
            if L < ub_threshold:
                pdb.gimp_selection_layer_alpha(new_layer)
                pdb.gimp_edit_clear(ub_layer)

        # 6.10 Add color to final color list
        color_layers.append(new_layer)

        # 6.11 Perform color match
        if do_color_match:
            match_color_name, match_color_rgb, distance = find_closest_color_in_palette(color_rgb,"graphic-design")
            color_matches.append(new_layer.name + " ({})\n".format(match_color_name))
            new_layer.name = match_color_name

    # Step 8: Hide Original Layer
    pdb.gimp_layer_set_visible(original_layer, False)

    # Step 8.1: Clear Selection
    pdb.gimp_selection_none(image)

    # Step 9: Resize canvas
    new_width = int(canvas_width * resolution)
    new_height = int(canvas_height * resolution)

    offset_y = int((canvas_margin * resolution) + (vert_offset * resolution))

    layer_width = pdb.gimp_image_width(image)
    if location == 0: # Left
        offset_x = int((new_width / 2) + (center_offset * resolution) - (layer_width / 2))
    elif location == 1: # Right
        offset_x = int((new_width / 2) - (center_offset * resolution) - (layer_width / 2))
    elif location == 2: # Center
        offset_x = int((new_width / 2) - (layer_width / 2))
    
    pdb.gimp_image_resize(image, new_width, new_height, offset_x, offset_y)

    # Step 10: Add registration mark
    script_dir = os.path.dirname(__file__) # Get the directory where this script is located
    file_path = os.path.join(script_dir, "registration.png") # Build the path to the image in the same folder
    reg_layer = pdb.gimp_file_load_layer(image, file_path)
    pdb.gimp_image_add_layer(image, reg_layer, -1)
    reg_layer.name = "REG"

    reg_offset_y = int((vert_offset * resolution) + (0.8 * resolution)) # Offset print below printer safe area

    reg_width = pdb.gimp_drawable_width(reg_layer)
    
    if location == 0: # Left
        reg_offset_x = int((new_width / 2) + (center_offset * resolution) - (reg_width / 2))
    elif location == 1: # Right
        reg_offset_x = int((new_width / 2) - (center_offset * resolution) - (reg_width / 2))
    elif location == 2: # Center
        reg_offset_x = int((new_width / 2) - (reg_width / 2))

    pdb.gimp_layer_set_offsets(reg_layer, reg_offset_x, reg_offset_y)

    # Step 11: Add text labels
    pdb.gimp_context_set_foreground((0, 0, 0)) # Set foreground color to black

    label_x_offset = reg_offset_x
    
    if generate_ub:
        color_layers.insert(0, ub_layer)
    
    for layer in color_layers:
        pdb.gimp_layer_set_lock_alpha(layer, False)
        label = pdb.gimp_text_fontname(image, layer, label_x_offset, reg_offset_y - font_size - 5, layer.name, -1, True, font_size, 0, font)
        label_width = pdb.gimp_drawable_width(label)
        pdb.gimp_floating_sel_anchor(label)
        pdb.gimp_layer_set_lock_alpha(layer, True)
        label_x_offset = label_x_offset + label_width + label_spacing

    for layer in image.layers:
        pdb.gimp_layer_set_lock_alpha(layer, True)

    # Step 12: Export to PostScript    
    if export:
        pdb.gimp_layer_set_visible(reg_layer, True)
        
        for layer in color_layers:
            pdb.gimp_layer_set_visible(layer, True)
            temp_layer = pdb.gimp_image_merge_visible_layers(image, CLIP_TO_IMAGE)
            export_path = "{}_{}.ps".format(original_file_name, layer.name)

            pdb.file_ps_save(image, temp_layer, export_path, export_path,
                             0,  # output width, 0 keeps the current width
                             0,  # output height, 0 keeps the current height
                             0,  # X offset
                             0,  # Y offset
                             0,  # Inches
                             0,  # Use width/height for aspect ratio
                             0,  # rotation angle
                             0,  # Don't use Encapsulated PostScript
                             0,  # Don't use preview
                             2)  # PostScript level 2

            pdb.gimp_layer_set_visible(layer, False)
        
    # Output color matches
    if do_color_match:
        pdb.gimp_message(''.join(color_matches))

    # End undo group
    pdb.gimp_image_undo_group_end(image)

register(
    "inksplit",
    "Automatically separate colors into solid black layers",
    "Automatically separate colors into solid black layers",
    "Otacon",
    "Your Copyright Information",
    "2024",
    "InkSplit Color Separations",
    "RGB*, GRAY*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_FLOAT, "canvas_width", "Canvas Width (in):", 17.5),
        (PF_FLOAT, "canvas_height", "Canvas Height (in):", 21.5),
        (PF_FLOAT, "canvas_margin", "Canvas Margin (in):", 1.25),
        (PF_INT, "resolution", "DPI:", 300),
        (PF_OPTION, "location", "Print Location:", 0, ["LEFT", "RIGHT", "CENTER"]),
        (PF_FLOAT, "center_offset", "Center Offset (in):", 4),
        (PF_FLOAT, "vert_offset", "Vertical Offset (in):", 0),
        (PF_FLOAT, "print_width", "Max Width (in):", 3.5),
        (PF_FLOAT, "print_height", "Max Height (in):", 0),
        (PF_TOGGLE, "generate_ub", "Generate Underbase?", True),
        (PF_SLIDER, "ub_threshold", "Underbase Lightness Threshold:\n(lower value = less UB)", 0.35, (0.0, 1.0, 0.05)),
        (PF_FONT, "font", "Font:", "Sans-Serif Bold"),
        (PF_INT, "font_size", "Font Size (px):", 60),
        (PF_INT, "label_spacing", "Label Spacing (px):", 40),
        (PF_TOGGLE, "export", "Export?", False),
        (PF_TOGGLE, "do_color_match", "Perform Color Match? (SLOW!)", False)
    ],
    [],
    inksplit,
    menu="<Image>/Filters"
)

main()
