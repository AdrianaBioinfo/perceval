import os
import pandas as pd
from skimage import io
import matplotlib.pyplot as plt

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
    list_mean = []
    # iterate through folder
    for films in os.listdir(folder_dir):
        # check if the image ends with tif
        if (films.endswith(".tif")):  
            stack_raw = io.imread(folder_dir +"/" + films)
            films = os.path.splitext(films)[0]
            # iterate over stack
            for i in range(stack_raw.shape[0]): 
                compt = 0
                for_mean = 0
                for row in stack_raw[i]: 
                    for pixel in row: # if pixel is not black
                        if pixel != 0:
                            compt += 1
                            for_mean += pixel
                if compt != 0:
                    list_mean.append(for_mean/compt) # mean intensity value
                else:
                    list_mean.append(0)
            dict_atpadp[films] = list_mean
            list_mean = []
    corrected_intens_val_df = pd.DataFrame.from_dict(dict_atpadp)
    corrected_intens_val_df = corrected_intens_val_df.T
    print('Finish !')
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
    list_sum = []
    for films in os.listdir(folder_dir): # iterate over folder files
        # check if the image ends with tif
        if (films.endswith(".tif")):  
            stack_raw = io.imread(folder_dir +"/" + films)
            films = os.path.splitext(films)[0]
            for i in range(stack_raw.shape[0]): # iterate over stack
                compt = 0
                for_mean = 0
                for row in stack_raw[i]: # iterate over row
                    for pixel in row:
                       if pixel != 0: # if pixel is not black
                           compt += pixel
                list_sum.append(compt)
            dict_marker[films] = list_sum
            list_sum = []
    corrected_intens_val_df = pd.DataFrame.from_dict(dict_marker)
    corrected_intens_val_df_t = corrected_intens_val_df.T
    # Get T0 F480/CD86 mean intensity value
    time_0 = corrected_intens_val_df_t[0]
    time_0_df = time_0.to_frame()
    time_0_df = time_0_df.rename(columns={0: f'T0 of {name} sum intensity value'})
    print('Finish !')
    return(time_0_df)

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
    preprocessed_df.to_csv(f'{csv_output_directory}/atpadp_preprocessed.csv')
    print('--- Preprocessing Finish ! ---')
    return(preprocessed_df)

def pie_chart(dataframe,fig_output_directory, sample_name):
    """ Plot pie chart
    Input
        dataframe : pandas df
            df of interest
        title : string
            Title of the plot
    Return
        preprocessed_df : pandas df
            Preprocessed ATP/ADP df
    """
    print('--- Pie chart ---')
    print('Baking the pie...')
    count_cluster = pd.DataFrame(dataframe['cluster'].value_counts())
    count_cluster = count_cluster.rename(columns={'count': 'cluster'})
    count_cluster = count_cluster.sort_index()
    cluster = count_cluster.index.to_list()
    counts = list(count_cluster['cluster'])
    colors_pie = {1:'darkturquoise',
               2:'lightgreen',
               3:'yellow',
               4:'orange'}
    plt.figure(figsize=(6,6))
    plt.pie(counts, labels=cluster, colors = [colors_pie[key] for key in cluster], autopct='%1.1f%%')
    plt.title(sample_name)
    plt.savefig(f'{fig_output_directory}/{sample_name}_piechart.png')
    print('Finish !')

