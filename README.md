# InkSplit Color Separations

![](https://github.com/user-attachments/assets/8662d893-19cb-4474-a813-16ace795a925)

A GIMP plug-in designed for screen printing workflows. This script takes a raster image and a specified color palette, reduces the image to the palette colors, and separates the colors into individual layers. Perfect for preparing artwork for screen printing!

## Features

- Reduces raster images to a defined color palette.
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
2. **Download the script**:
        Clone or download this repository, and copy the auto_color_seps.py script to your GIMP plug-ins directory:
        - On Linux: `~/.config/GIMP/2.10/plug-ins/`
        - On Windows: `C:\Users\<YourUsername>\AppData\Roaming\GIMP\2.10\plug-ins\`
3. Make the Script Executable (Linux/Mac):
   Run the following command to ensure the script is executable:
   ```
   chmod +x auto_color_seps.py
   ```
4. Restart GIMP:
   After installation, restart GIMP. The plug-in will appear under the Filters menu.

## Usage

1. Open your raster image in GIMP.
2. Select your desired color pallete in the Palettes panel.
3. Navigate to Filters > Auto Color Separations.
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
