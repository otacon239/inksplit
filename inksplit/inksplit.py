#!/usr/bin/env python2

from gimpfu import *
from colormath.color_objects import sRGBColor, LabColor, LCHabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
import os

def find_closest_color_in_palette(target_color, search_palette, batch_size=100):
    # Use batch processing for color match - Runs very slow without!
    palette_size, _ = pdb.gimp_palette_get_colors(search_palette)
    rgb = sRGBColor(target_color.red, target_color.green, target_color.blue, is_upscaled=False)
    target_color_lab = convert_color(rgb, LabColor)

    min_distance = float('inf')
    closest_color = None
    closest_color_name = None

    for start_index in range(0, palette_size, batch_size):
        end_index = min(start_index + batch_size, palette_size)

        for i in range(start_index, end_index):
            color_rgb = pdb.gimp_palette_entry_get_color(search_palette, i)
            color_name = pdb.gimp_palette_entry_get_name(search_palette, i)

            rgb = sRGBColor(color_rgb.red, color_rgb.green, color_rgb.blue, is_upscaled=False)
            color_lab = convert_color(rgb, LabColor)

            distance = delta_e_cie1976(target_color_lab, color_lab)

            if distance < min_distance:
                min_distance = distance
                closest_color = color_rgb
                closest_color_name = color_name

    return closest_color_name, closest_color, min_distance

def inksplit(
    image,
    drawable,
    auto_color_match,
    colors_in_image,
    palette, # User-chosen color palette
    canvas_width,
    canvas_height,
    canvas_margin,
    resolution, # DPI
    dithering,
    alpha_dither,
    autocrop,
    location, # Left/Right/Center
    center_offset,
    vert_offset,
    print_width,
    print_height,
    generate_ub,
    ub_threshold,
    font,
    font_size,
    label_spacing,
    export,
    pms_color_match,
    best_fit_palette):
    
    original_file_name = os.path.splitext(os.path.basename(image.filename))[0]
    
    # Start an undo group, so that all operations can be undone in one go
    pdb.gimp_image_undo_group_start(image)

    original_layer = image.active_layer
    original_layer.name = "ORIG"

    pdb.gimp_layer_add_alpha(original_layer)

    # Adjust scaling
    if print_height or print_width: # Check if either print height or width is specified
        if autocrop:
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

    # Convert to Indexed color palette
    if auto_color_match:
        pdb.gimp_image_convert_indexed(
            image,
            CONVERT_DITHER_FS if dithering else CONVERT_DITHER_NONE,
            CONVERT_PALETTE_GENERATE,
            colors_in_image,
            alpha_dither,
            False,
            "")
        
        # Create a new palette - Delete the old one if it already exists
        current_palette = "inksplit_temp"
        if current_palette in pdb.gimp_palettes_get_list(""):
            pdb.gimp_palette_delete(current_palette)
        
        # Create a new, empty palette
        pdb.gimp_palette_new(current_palette)
        pdb.gimp_context_set_palette(current_palette)

        colormap = pdb.gimp_image_get_colormap(image)
        num_colors = len(colormap[1]) // 3  # Each color is represented by 3 values (RGB)

        print(colormap)
        print(num_colors)
        # Add colors to the new palette
        for i in range(num_colors):
            r = colormap[1][i * 3]   # Red
            g = colormap[1][i * 3 + 1]  # Green
            b = colormap[1][i * 3 + 2]  # Blue
            color_name = "Color " + str(i+1)
            pdb.gimp_palette_add_entry(current_palette, color_name, (r, g, b))
    
    else:
        current_palette = palette # Get the name of the current palette
        pdb.gimp_image_convert_indexed(
            image,
            CONVERT_DITHER_FS if dithering else CONVERT_DITHER_NONE,
            CUSTOM_PALETTE,
            0,
            alpha_dither,
            False,
            current_palette)

    # Convert back to RGB - Several operations require RGB mode
    pdb.gimp_image_convert_rgb(image)

    pdb.gimp_layer_set_lock_alpha(original_layer, True) # Prevent edits

    # Create Underbase layer
    if generate_ub:
        ub_layer = pdb.gimp_layer_copy(original_layer, True) # Copy original layer
        pdb.gimp_image_add_layer(image, ub_layer, 0)
        ub_layer.name = "UB"
        pdb.gimp_layer_set_lock_alpha(ub_layer, True) # Lock pixels
        pdb.gimp_context_set_foreground((0, 0, 0)) # Set foreground color to black
        pdb.gimp_edit_fill(ub_layer, FOREGROUND_FILL) # Fill the new layer
        pdb.gimp_layer_set_lock_alpha(ub_layer, False) # Allow for removal of dark colors

    # Extract colors
    palette_size, palette = pdb.gimp_palette_get_colors(current_palette)
    color_layers = [] # Keep track of which colors get generated
    color_matches = [] # Keep track of PMS color matches

    for i in range(palette_size): # For each color in the palette
        color_rgb = pdb.gimp_palette_entry_get_color(current_palette, i)  # Get the GimpRGB value by index
        color_name = pdb.gimp_palette_entry_get_name(current_palette, i)  # Get the color name by index

        # Select by color        
        pdb.gimp_context_set_antialias(False)
        pdb.gimp_context_set_feather(False)
        pdb.gimp_context_set_sample_transparent(False)
        pdb.gimp_context_set_sample_merged(False)
        pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, original_layer, color_rgb)  # Use specific color from palette

        if pdb.gimp_selection_is_empty(image): # Skip empty colors
            continue        

        # Cut and paste to new layer
        pdb.gimp_edit_cut(original_layer)

        # Create a new layer with the same dimensions as the image
        new_layer = pdb.gimp_layer_new(
            image,                       # The image to which the layer will be added
            image.width,                 # Width of the new layer
            image.height,                # Height of the new layer
            RGBA_IMAGE,                  # Type of the new layer (RGB, RGBA, etc.)
            color_name,                  # Name of the new layer
            100,                         # Opacity (0-100)
            0                            # Layer mode (0 for normal)
        )

        # Add the new layer to the image
        pdb.gimp_image_insert_layer(image, new_layer, None, 0)
        
        # Paste the cut pixels into the new layer
        floating_sel = pdb.gimp_edit_paste(new_layer, False)
        
        # Anchor the floating selection to the new layer
        pdb.gimp_floating_sel_anchor(floating_sel)

        # Lock new layer alpha
        pdb.gimp_layer_set_lock_alpha(new_layer, True)

        # Fill with black
        pdb.gimp_context_set_foreground((0, 0, 0))  # Set foreground color to black
        pdb.gimp_edit_fill(new_layer, FOREGROUND_FILL)  # Fill with black
        
        # Remove color from underbase if below lightness threshold
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

        # Add color to final color list
        color_layers.append(new_layer)

        # Perform color match
        if pms_color_match:
            match_color_name, match_color_rgb, distance = find_closest_color_in_palette(color_rgb, best_fit_palette)
            color_matches.append(new_layer.name + " ({})\n".format(match_color_name))
            new_layer.name = match_color_name

    # Hide Original Layer
    pdb.gimp_layer_set_visible(original_layer, False)

    # Clear Selection
    pdb.gimp_selection_none(image)

    # Resize canvas
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

    # Add registration mark
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

    # Add text labels
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

    # Export to PostScript
    if export:
        # Start by hiding all layers
        for layer in color_layers:
            pdb.gimp_layer_set_visible(reg_layer, False)

        # Re-enable Registration
        pdb.gimp_layer_set_visible(reg_layer, True)

        # Re-enable layers one at a time
        for layer in color_layers:
            pdb.gimp_layer_set_visible(layer, True)
            temp_layer = pdb.gimp_image_merge_visible_layers(image, EXPAND_AS_NECESSARY)
            print(layer.name)
            export_path = "{}_{}.ps".format(original_file_name, layer.name)
            
            pdb.file_ps_save(image, temp_layer, export_path, export_path, 0)

            pdb.gimp_layer_set_visible(layer, False)
        
    # Output color matches
    if pms_color_match:
        pdb.gimp_message(''.join(color_matches))

    if auto_color_match: # Remove temporary color palette if needed
        pdb.gimp_palette_delete(current_palette)
        
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
        (PF_TOGGLE, "auto_color_match", "Auto Color Match?", False),
        (PF_SLIDER, "colors_in_image", "Colors in Image (Auto Color Match Only):", 1, (1, 20, 1)),
        (PF_PALETTE, "palette", "Color Palette:", ""),
        (PF_FLOAT, "canvas_width", "Canvas Width (in):", 23),
        (PF_FLOAT, "canvas_height", "Canvas Height (in):", 31),
        (PF_FLOAT, "canvas_margin", "Canvas Margin (in):", 1.25),
        (PF_INT, "resolution", "DPI:", 300),
        (PF_TOGGLE, "dithering", "Dithering?", True),
        (PF_TOGGLE, "alpha_dithering", "Alpha Dithering?", False),
        (PF_TOGGLE, "autocrop", "Autocrop?", True),
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
        (PF_TOGGLE, "pms_color_match", "PMS Color Match?", False),
        (PF_PALETTE, "best_fit_palette", "Best Fit Palette: ", "Pantone colors")
    ],
    [],
    inksplit,
    menu="<Image>/Filters"
)

main()
