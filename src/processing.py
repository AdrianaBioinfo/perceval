import os
import pandas as pd
from skimage import io
import matplotlib.pyplot as plt
import numpy as np

def get_ATP_ADP_ratio(folder_dir):
    """
    Iterate through folder, open image and 
    get a df of ATP:ADP mean intensity value
    Input
        folder_dir : str
            path where images are saved
    Return
        one_fcorrected_intens_val_df : pandas dataframe (df)
    """
    print('--- Get ATP/ADP ratio ---')
    print('Creation of the dataframe containing ATP/ADP tracks...')
    dict_atpadp = {}
    # Iterate through folder and process images
    for file_name in filter(lambda f: f.endswith(".tif"), os.listdir(folder_dir)):
        file_path = os.path.join(folder_dir, file_name)
        stack_raw = io.imread(file_path)
        film_name = os.path.splitext(file_name)[0]
        # Calculate mean intensity for each slice in the stack
        mean_intensity_per_slice = [
            np.mean(slice[slice > 0]) if np.any(slice > 0) else 0
            for slice in stack_raw
        ]
        
        dict_atpadp[film_name] = mean_intensity_per_slice
    # Convert the dictionary to a DataFrame
    corrected_intens_val_df = pd.DataFrame.from_dict(dict_atpadp, orient='index')
    print('Finished!')
    return(corrected_intens_val_df)

def get_intensity_sum(folder_dir, name):
    """
    Iterate through folder, open image and 
    get a df of F480/CD86 sum intensity value
    Input
        folder_dir : str
            path where images are saved
    Return
        corrected_intens_val_df_t : pandas df
        time_0_df : pandas df
    """
    print(f'--- Get {name} sum values ---')
    print(f'Creation of the dataframe containing {name} tracks...')
    dict_marker = {}
    for films in os.listdir(folder_dir):  # Iterate over files in the folder
        if films.endswith(".tif"):  
            stack_raw = io.imread(os.path.join(folder_dir, films))
            films_name = os.path.splitext(films)[0]
            
            # Sum pixel values for non-black pixels across the stack
            list_sum = [stack_raw[i][stack_raw[i] != 0].sum() for i in range(stack_raw.shape[0])]
            
            dict_marker[films_name] = list_sum
    # Create dataframe and transpose it
    corrected_intens_val_df_t = pd.DataFrame.from_dict(dict_marker, orient='index')
    # Get T0 F480/CD86 mean intensity value
    time_0_df = corrected_intens_val_df_t.iloc[:, 0].to_frame(name=name)
    print('Finished!')
    
    return(time_0_df)

def get_mean_ratio(folder_dir,name):
    """
    Iterate through folder, open image and 
    get a df of ATP:ADP mean intensity value
    Input
        folder_dir : str
            path where images are saved
    Return
        corrected_intens_val_df : pandas dataframe (df)
    """
    dict_atpadp = {}
    # Iterate through folder and process images
    for file_name in filter(lambda f: f.endswith(".tif"), os.listdir(folder_dir)):
        file_path = os.path.join(folder_dir, file_name)
        stack_raw = io.imread(file_path)
        film_name = os.path.splitext(file_name)[0]
        # Calculate mean intensity for each slice in the stack
        mean_intensity_per_slice = [
            np.mean(slice[slice > 0]) if np.any(slice > 0) else 0
            for slice in stack_raw
        ]
        dict_atpadp[film_name] = mean_intensity_per_slice
    # Convert the dictionary to a DataFrame
    mean_intensity_df = pd.DataFrame.from_dict(dict_atpadp, orient='index')
    if name != "ATPADP":
        mean_intensity_df = mean_intensity_df.iloc[:, 0].to_frame(name=name)
    print(f'{folder_dir} done ! ')
    return mean_intensity_df

def preprocess_atpadp_tracks(dataframe, csv_output_directory):
    """ Preprocess ATP/ADP tracks
    Iterate through tracks df. Normalize,
    remove noise and smooth the tracks.
    Input
        dataframe : pandas df
            ATP/ADP df
    Return
        preprocessed_df : pandas df
            Preprocessed ATP/ADP df
    """
    print('--- Preprocess ATP/ADP tracks df ---')
    # re-normalize data
    norm_value = 155
    list_of_list = []
    count = 0
    for index, row in dataframe.iterrows(): 
        factor = 155/row[0]
        list_val = []
        for val in row:
            new_val = factor*val
            list_val.append(new_val)         
        dataframe.iloc[count, :] = list_val
        list_of_list.append(list_val)
        count+=1
    # if length of the track <30, fill it with the last value
    dataframe_no_na = dataframe.ffill(axis=1)
    # smooth the track
    dataframe_no_na_RM = dataframe_no_na.T.rolling(3).mean()
    dataframe_no_na_RM = dataframe_no_na_RM.iloc[2:]
    # remove tracks with value = 0
    dataframe_no_na_RM_wo0 = dataframe_no_na_RM.copy()
    columns = [c for c in dataframe_no_na_RM_wo0.columns if (dataframe_no_na_RM_wo0[c] == 0).any()]
    dataframe_no_na_RM_wo0 = dataframe_no_na_RM_wo0.drop(columns, axis=1)
    # remove tracks contraining value(s) <50 before injection
    bef_injection = dataframe_no_na_RM_wo0.T.iloc[:,:8]
    columns_50 = [c for c in bef_injection.T.columns if (bef_injection.T[c] <= 50).any()]
    nb_removed = len(columns)+len(columns_50)
    print(f'Number of tracks containing intensity value = 0 : {len(columns)}')
    print(f'Number of tracks containing intensity value < 50 before injection :{len(columns_50)}')
    print(f'Total Number of removed tracks : {nb_removed}')
    dataframe_no_na_RM_wo0 = dataframe_no_na_RM_wo0.drop(columns_50, axis=1)
    preprocessed_df = dataframe_no_na_RM_wo0.T
    # save the dataframe
    #preprocessed_df.to_csv(f'{csv_output_directory}/atpadp_preprocessed.csv')
    print('--- Preprocessing Finish ! ---')
    return(preprocessed_df)


