# Perceval

- Get individual crops from ATP:ADP, F480 and CD86 data -> Fiji macro
- Get heatmaps of these data
- Predict metabolic profil

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

You must have all the data in one folder. The subfolders need to contain "ATPADP" or "F480" or "CD86" in their name. Otherwise they will not be included in the analysis.

Ex: 
```SHELL
Sample_X/
  ├──sample_X_ATPADP/
  │       ├──sample_X_crop_1
  |       ├──sample_X_crop_n
  ├──sample_X_F480/
  │       ├──sample_X_crop_1
  |       ├──sample_X_crop_n  
  ├──sample_X_CD86/
          ├──sample_X_crop_1
          ├──sample_X_crop_n  

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
  -output OUTPUT_PATH, --output_path OUTPUT_PATH
                        Enter path for the output folder
  -skp SKP_PREPROC, --skp_preproc SKP_PREPROC
                        If 'yes' the preprocessing of the films is skip. Else set 'no'
  -atp_df ATPADP_F480_CD86_DF, --atpadp_f480_cd86_df ATPADP_F480_CD86_DF
                        If skp is 'yes', enter the path of the atpadp/f480/cd86 dataframe
  -preds RUN_PREDICTIONS, --run_predictions RUN_PREDICTIONS
                        Optional. Compute predictions. By default 'yes'. You can set it to 'no'
```


