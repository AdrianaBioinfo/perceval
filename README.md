# 🌈Perceval 

This project was carried out as part of the "Met-Vision reveals a metabolic mosaic of tissue macrophage 
reconfigured by inflammation" paper. 

These scripts allow you to extract, interpret and classify functional metabolic information from live-cell imaging data with single-cell resolution. 
In the [macro folder](https://github.com/AdrianaBioinfo/perceval/tree/main/macro) you will find the macro for displaying the single-cell view and the individual cell crops.
Individual crops are used as input to the python pipeline.

The outputs of the pipeline are :
- Pie chart representing the distribution of each metabolic class
- Heatmaps of ATP:ADP ratio over time and associated markers (maximum 2)
- Histograms of markers
- Tracks plot colored by cluster

**Quick start** (run the whole Python analysis):
```
python main.py -path path_to_individual_crops_folder -markers ATPADP F480 MHCII
```

## 	:zero: Prerequisites

To use the program you must have python. 
To download python: https://www.python.org/downloads/. The version used for this project is 3.11.9

Clone the repository:

```SHELL
git clone git@github.com:AdrianaLecourieux/perceval.git
```

Move to the new directory:

```SHELL
cd perceval/
```

Install Miniconda :  https://docs.conda.io/en/latest/miniconda.html#windows-installers.
Once Miniconda is installed, install Mamba :

```SHELL
conda install mamba -n base -c conda-forge
```

Create the environment and load it :

```SHELL
mamba env create -f perceval_1.yml
conda activate perceval_1
```
If you want to deactivate the environment, use the command :

```SHELL
conda deactivate
```
-----------------------
## :one: Running Analysis

You must have all the data in one folder. The subfolders need to contain "ATPADP" and the marker(s) name(s). Otherwise they will not be included in the analysis.

Ex: 
```SHELL
Working_directory/
  Sample_X/
    ├──sample_X_ATPADP/
    │       ├──sample_X_crop_1
    |       ├──sample_X_crop_n
    ├──sample_X_Marker1/
    │       ├──sample_X_crop_1
    |       ├──sample_X_crop_n  
    ├──sample_X_Marker2/
            ├──sample_X_crop_1
            ├──sample_X_crop_n
  Sample_Y/
    ├──sample_Y_ATPADP/
    │       ├──...
    ├──sample_Y_Marker1/
    │       ├──... 
    ├──sample_Y_Marker2/
            ├──...

```
If you need help about inputs, you can use the --help command:

```SHELL
cd src/
python main.py --help
```
```
  -h, --help            show this help message and exit
  -path PATH_WORKING_DIRECTORY, --path_working_directory PATH_WORKING_DIRECTORY
                        Enter path of the working directory
  -markers MARKERS [MARKERS ...], --markers MARKERS [MARKERS ...]
                        List of markers to process (e.g., ATPADP F480 MHCII)
  -output OUTPUT_PATH, --output_path OUTPUT_PATH
                        Optional. Enter path for the output folder. By default output folder = path
  -preds RUN_PREDICTIONS, --run_predictions RUN_PREDICTIONS
                        Optional. Compute predictions. By default "yes". You can set it to "no"
```

If you use the pipeline please cite the paper.
