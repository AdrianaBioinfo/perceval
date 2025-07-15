# Perceval macro

## :zero: Requirements
The macro was developed and tested with the following versions:
- ImageJ : 2.16.0/1.54p
- Java : 1.8.0_322

## :one: Running the Perceval macro

To run the Perceval macro, make sure you have a *.tiff* file with 2 to 4 channels.

Once the macro starts, a pop-up window will appear asking for input. Please fill out the following fields accordingly:
- **Markers** : Enter the name to assign to each channel, in order, separated by commas without spaces (ex : ADP,F480,ATP,CD86)
- **Save crops** :  Check *yes* to save the individual cropped images of the detected cells. This is required if you plan to run the Perceval script afterward
- **Normalize all data** : Check *yes* to normalize the data
- **Change normalization mean intensity value** : The value will correspond to the mean intensity of the ROIs at frame 1
- **Border around cells**: Check *yes* to display a white border around each cell in the output array
