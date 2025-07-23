import argparse 
import pandas as pd
import os
import joblib
import sktime

from processing import *
from figures import * 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Arguments
    parser.add_argument("-path", "--path_working_directory", help = 'Enter path of the working directory')
    parser.add_argument("-output", "--output_path", help = 'Enter path for the output folder')
    parser.add_argument("-atp_df", "--atpadp_f480_cd86_df", help = 'Optional. Path of the atpadp/f480/cd86 dataframe')
    parser.add_argument("-preds", "--run_predictions", help = 'Optional. Compute predictions. By default "yes". You can set it to "no"')
    
    # Assign arguments to variables
    args = parser.parse_args()
    path = args.path_working_directory
    combined_df_path = args.atpadp_f480_cd86_df
    output_folder = args.output_path
    prediction = args.run_predictions

    if not path and not combined_df_path:
        raise Exception("ERROR : You need to enter a path !")
    if not output_folder:
        output_folder = path

    # Output directory
    current_directory = os.getcwd()
    output_directory = os.path.join(output_folder, r'outputs')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Directory for the figures
    fig_output_directory = os.path.join(output_directory, r'figs') 
    if not os.path.exists(fig_output_directory):
        os.makedirs(fig_output_directory)
    if not combined_df_path:
            # Directory for the dataframes
        csv_output_directory = os.path.join(output_directory, r'dataframe')
        if not os.path.exists(csv_output_directory):
            os.makedirs(csv_output_directory)

        path_split = os.path.normpath(path)
        sample_name = path_split.split(os.sep)[-1]
    # Preprocessing
        list_of_df_atpadp = []
        list_of_df_f480 = []
        list_of_df_CD86 = []
        for folder in os.listdir(path):
            if "ATPADP" in folder:
                df_atpadp = get_ATP_ADP_ratio(f'{path}/{folder}')
                list_of_df_atpadp.append(df_atpadp)
            if "F480" in folder:
                df_f480 = get_intensity_sum(f'{path}/{folder}', "F480")
                list_of_df_f480.append(df_f480)
            if "CD86" in folder:
                df_CD86 = get_intensity_sum(f'{path}/{folder}', "CD86")
                list_of_df_CD86.append(df_CD86)

        atpadp_concat = pd.concat(list_of_df_atpadp)
        # preprocess adpatp df and saved all the df in specific folder
        df_combined_all = preprocess_atpadp_tracks(atpadp_concat, csv_output_directory) 
        preprocessed_adpatp_np = df_combined_all.to_numpy()
        if len(list_of_df_f480) !=0:
            f480_concat = pd.concat(list_of_df_f480)
            # create one merged df
            df_combined_all = df_combined_all.merge(f480_concat, how= 'inner', left_index=True,right_index=True)
        if len(list_of_df_CD86) !=0:    
            cd86_concat = pd.concat(list_of_df_CD86)
            df_combined_all = df_combined_all.merge(cd86_concat, how= 'inner', left_index=True,right_index=True)
        df_combined_all.to_csv(f'{csv_output_directory}/perceval_preprocessed.csv')
        
        # compute figures with ATP/ADP, F480 and CD86 data
        if len(list_of_df_f480) !=0 and len(list_of_df_CD86) !=0:
            plot_3_heatmaps(df_combined_all, fig_output_directory)
            plot_histogram(df_combined_all.iloc[:,-1:], "CD86", fig_output_directory, color="c")
            plot_histogram(df_combined_all.iloc[:,-2:-1], "F480", fig_output_directory, color="m")
        # if F480 and CD86 data are missing
        elif len(list_of_df_f480) ==0 and len(list_of_df_CD86) ==0:
            plot_atpadp_heatmaps(df_combined_all, fig_output_directory)
        # if F480 or CD86 data is missing
        elif len(list_of_df_f480) ==0 or len(list_of_df_CD86) ==0:
            if len(list_of_df_f480) < len(list_of_df_CD86):
                plot_two_heatmaps(df_combined_all, "CD86", fig_output_directory, color="c")
                plot_histogram(df_combined_all.iloc[:,-1:], "CD86", fig_output_directory, color="c")
            else:
                plot_two_heatmaps(df_combined_all, "F480", fig_output_directory, color="m")
                plot_histogram(df_combined_all.iloc[:,-2:-1], "F480", fig_output_directory, color="m")

    else:
        sample_name = combined_df_path.split(os.sep)[-1]
        sample_name = sample_name.split(".")[0]
        df_combined_all = pd.read_csv(combined_df_path, index_col = 0)
        # check if CD86 and F480 data are present
        if "CD86" and "F480" in df_combined_all.columns:
            print("ATP:ADP, F480 and CD86 data are presente in the dataset")
            preprocessed_adpatp_np = df_combined_all.iloc[:,:-2].to_numpy()
            plot_3_heatmaps(df_combined_all, fig_output_directory)
            plot_histogram(df_combined_all.iloc[:,-1:], "CD86", fig_output_directory, color="c")
            plot_histogram(df_combined_all.iloc[:,-2:-1], "F480", fig_output_directory, color="m")
        # check if CD86 and F480 data are not present
        elif "CD86" not in df_combined_all.columns and "F480" not in df_combined_all.columns:
            print("Only ATP:ADP data are presente in the dataset")
            preprocessed_adpatp_np = df_combined_all.to_numpy()
            plot_atpadp_heatmaps(df_combined_all, fig_output_directory)
        # check if CD86 or F480 data not present
        else: 
            marker = list(df_combined_all.columns)[-1]
            print(f" ATP:ADP and {marker} data are presente in the dataset")
            preprocessed_adpatp_np = df_combined_all.iloc[:,:-1].to_numpy()
            if "CD86" in df_combined_all.columns:
                plot_two_heatmaps(df_combined_all, "CD86", fig_output_directory, color="c")
                plot_histogram(df_combined_all.iloc[:,-1:], "CD86", fig_output_directory, color="c")
            elif "F480" in df_combined_all.columns:
                plot_two_heatmaps(df_combined_all, "F480", fig_output_directory, color="m")
                plot_histogram(df_combined_all.iloc[:,-2:-1], "F480", fig_output_directory, color="m")
            

    # model predictions
    if prediction != 'no':
        print('--- Run predictions ---')
        model = joblib.load("model_perceval.joblib")
        predictions = model.predict(preprocessed_adpatp_np)
        print('Finish !')
    
    # pie chart & tracks plot
        df_combined_all['cluster'] = predictions
        df_combined_all = df_combined_all.sort_values(by=['cluster']) 
        pie_chart(df_combined_all, fig_output_directory, sample_name)
        plot_tracks(df_combined_all, fig_output_directory)
    
    print("Final finish !")

