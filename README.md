# InkSplit Color Separations
![Inksplit Promo](https://github.com/user-attachments/assets/85098dbb-b7e2-4600-968b-3c8fee73b066)

https://github.com/user-attachments/assets/f7d3cd21-4ab6-4918-b0a0-cdcfce39445f

A GIMP plug-in designed for screen printing color separations. This script takes a raster image and a color palette as input, reduces the image to the palette colors, and separates the colors into individual layers. 

## Features

- Reduces raster images to a defined color palette.
- Full set of offset settings made to work with any printer.
- Automatically separates each color into its own layer.
- Leverages the `colormath` library for accurate color conversions and matching.
- Streamlines the screen printing preparation process.

## Known Issues

- Color matching is very slow and sometimes fails to find a match - Matches are occasionally inaccurate
- Exporting currently does not work
- Center alignment math seems to be off - needs more testing!

## Installation

1. **Dependencies**:  
   Ensure you have Python 2.x installed as this script relies on Python 2 and GIMP's `gimpfu` module. Additionally, install the `colormath` library:
   ```bash
   pip install colormath
   ```
   Also download and install the Pantone color palletteto GIMP. Found here: https://github.com/denilsonsa/gimp-palettes/
2. **Download the script**:
   Clone or download this repository, and copy the inksplit folder to your GIMP plug-ins directory. You can find this by going to `Edit > Preferences > Folders > Plug-Ins` and clicking the filing cabinet icon.
   
4. Make the Script Executable (Linux/Mac Only):
   Run the following command in the inksplit to ensure the script is executable:
   ```
   chmod +x inksplit.py
   ```
5. Restart GIMP:
   After installation, restart GIMP. The plug-in will appear under the Filters menu.

## Usage

1. Open your image in GIMP and make sure what you are printing is on a transparent background.
2. Select your desired color pallete in the Palettes panel.
3. Navigate to Filters > InkSplit Color Separations.
   - Here you will be presented ith the options window. Options function as follows:
      ![Screenshot 2025-01-15 at 10 36 45](https://github.com/user-attachments/assets/d21c38e5-494b-4184-b078-261626470b63)
      - Canvas Width/Height/Margin: These are settings for the overall artboard/printer output size (Margin currently only affects vertical offset)
      - DPI: This is the output resolution of the screen printer
      - Print Location: This determines which direction the center offset goes
      - Center Offset (in): This will offset the image from the center of the canvas for left/right-chest prints
      - Vertical Offset (in): This will offset the image from the top of the canvas (+ Canvas Margin)
      - Max Width/Height (in): These two work together to choose the lower of the two sizes
         - If size is left at zero on both, no scaling is done
         - If size is only set on one, the other is ignored
         - If size is set on both, whichever scales smaller is used (to respect "max" values)
      - Generate Underbase?: This will create an additional layer for a white underbase
      - Underbase Lightness Threshold: This setting skips generating underbase for dark colors. The lower the value is, the more dark colors are exluded from the underbase. Useful for printing dark colors on dark shirts.
      - Font/Font Size/Label Spacing: These determine the properties of the registration labels that are generated
      - Export: *--CURRENTLY BROKEN--* This allows for automatic exporting of all layers at once
      - Perform Color Match? (SLOW!): This will take advantage of the colormath library to do a simple color match against the Pantone color set. It will also automatically re-label layers to match their Pantone values and use these values in the registration.

4. The script will process the image, reduce it to the chosen palette, and separate the colors into individual layers.

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
