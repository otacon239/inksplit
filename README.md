# InkSplit Color Separations
![Inksplit Promo](https://github.com/user-attachments/assets/85098dbb-b7e2-4600-968b-3c8fee73b066)

https://github.com/user-attachments/assets/8662d893-19cb-4474-a813-16ace795a925

A GIMP plug-in designed for screen printing color separations. This script takes a raster image and a color palette as input, reduces the image to the palette colors, and separates the colors into individual layers. 

## Features
- Reduces raster images to a defined color palette.
- Full set of offset settings made to work with any printer.
- Automatically separates each color into its own layer.
- Leverages the `colormath` library for accurate color conversions and matching.
- Streamlines the screen printing preparation process.

## Known Issues
- Exporting currently does not work

## Installation
1. **Dependencies**:  
   ## colormath
   - You will need to install the `colormath` library via GIMP's Python by performing the following steps:
        1. Find the Python path by going to `Filters > Python-fu > Console` and run the following:
           ```python
           import sys
           print(sys.executable)
           ```
        2. In your terminal, cd to this directory and run:
           ```
           python -m pip install colormath
           ```
   ## Pantone color palette
   - To install the Pantone color palette, first download the palette here: https://github.com/denilsonsa/gimp-palettes/blob/master/palettes/Pantone.gpl
      - This file will need to be placed in the App Data/Config directory. You can find this by going to `Preferences > Folders > Palettes`. You may need to create this folder if it does not already exist.
2. **Download the script**:
   Clone or download this repository, and copy the inksplit folder to your GIMP plug-ins directory. You can find this by going to `Edit > Preferences > Folders > Plug-Ins` and clicking the filing cabinet icon.
   
3. Make the Script Executable (Linux/Mac Only):
   Run the following command in the inksplit to ensure the script is executable:
   ```
   chmod +x inksplit.py
   ```
4. Restart GIMP:
   After installation, restart GIMP. The plug-in will appear under the Filters menu.

## Usage

1. Open your image in GIMP and make sure what you are printing is on a transparent background.
2. Navigate to Filters > InkSplit Color Separations.
   - Here you will be presented with the options window. Options function as follows:
      ![InkSplit Options](https://github.com/user-attachments/assets/f5502f76-b34f-4e2c-9d36-30cabae742b3)
      - Auto Color Match: Automatically flatten the image to the amount of colors specified
      - Colors in Image: The amount of colors in the image to reduce to (not including underbase)
      - Color Palette: If Auto Color Match is disabled, you can specify a custom color palette
      - Canvas Width/Height/Margin: These are settings for the overall artboard/printer output size (Margin currently only affects vertical offset)
      - DPI: This is the output resolution of the screen printer
      - Dithering: Enables gradient dithering using Floyd-Steinberg distribution
      - Alpha Dithering: Similar to dithering, but applies to transparency gradients
      - Autocrop?: Automatically crop empty space around the image before resizing
      - Print Location: This determines which direction the center offset goes - Useful for left/right chest decorations
      - Center Offset (in): This determines the amount of offset applied to print location
      - Vertical Offset (in): This will offset the image from the top of the canvas (+ Canvas Margin) - Currently only accepts a positive value to lower your design
      - Max Width/Height (in): These two work together to choose the lower of the two sizes
         - If size is left at zero on both, no scaling is done
         - If size is only set on one, the other is ignored
         - If size is set on both, whichever scales smaller is used (to respect "max" values)
      - Generate Underbase?: This will create an additional layer for a white underbase
      - Underbase Lightness Threshold: This setting skips generating underbase for dark colors. The lower the value is, the more dark colors are exlcuded from the underbase. Useful for printing dark colors on dark shirts.
      - Font/Font Size/Label Spacing: These determine the properties of the registration labels that are generated
      - Export: *--CURRENTLY BROKEN--* This allows for automatic exporting of all layers at once
      - Best Fit Color Match?: This will take advantage of the colormath library to do a basic color match against the selected Best Fit Palette. It will also automatically re-label layers to match the color labels found in the Best Fit Palette and use these values in the registration.
      - Best Fit Palette: This determines what color set is used to match color names against

4. The script will perform the following steps, in order:
   1. Adjust image scaling
   2. Reduce to color palette
   3. Create underbase
   4. Extract colors & color match
   5. Remove dark colors from underbase
   6. Resize canvas
   7. Add registration marks
  
## Planned Changes and Additions Before Intial Release

- [ ] Separate system settings into a separate window
- [ ] Allow for persistent settings
- [ ] Break settings into Basic, Intermediate, Advanced
- [ ] Add custom registration mark option
- [ ] Error checking
- [ ] Break code into more organized and modular functions

## Contributing

We welcome contributions to this project! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear and concise commit messages.
4. Submit a pull request with a detailed explanation of your changes.

## License
This project is licensed under the GNU General Public License v3.0. You are free to use, modify, and distribute the script, provided that any modifications or derived works are also distributed under the GPL v3 license.

## Acknowledgments
- The colormath library for its excellent color conversion functionality.
- The GIMP development team for creating such a versatile and open-source image editing platform.

## Contact
For questions, suggestions, or feedback, please open an issue or reach out to me via direct message.

---

Happy screen printing!
