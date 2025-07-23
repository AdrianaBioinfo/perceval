import argparse 
import pandas as pd
import os
# tkinter
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter_adjust import ScatterPopup

from processing import *
from figures import * 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Arguments
    parser.add_argument("-path", "--path_working_directory", help = 'Enter path of the working directory')
    parser.add_argument("-markers", "--markers", nargs='+', help="List of markers to process (e.g., ATPADP F480 CD86)")
    parser.add_argument("-output", "--output_path", help = 'Optional. Enter path for the output folder. By default output folder = path')
    parser.add_argument("-preds", "--run_predictions", help = 'Optional. Compute predictions. By default "yes". You can set it to "no"')
    
    # Assign arguments to variables
    args = parser.parse_args()
    markers = args.markers
    path = args.path_working_directory
    output_folder = args.output_path
    prediction = args.run_predictions

    if not path:
        raise Exception("ERROR : You need to enter a path !")
    if not output_folder:
        output_folder = path
    # Output directory
    output_directory = os.path.join(output_folder, r'outputs')
    print(output_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Directory for the figures and df
    fig_output_directory = os.path.join(output_directory, r'figs') 
    if not os.path.exists(fig_output_directory):
        os.makedirs(fig_output_directory)
    csv_output_directory = os.path.join(output_directory, r'dataframe')
    if not os.path.exists(csv_output_directory):
        os.makedirs(csv_output_directory)

    path_split = os.path.normpath(path)
    sample_name = path_split.split(os.sep)[-1]
    # Preprocessing
    list_of_df_atpadp = []
    list_of_other_markers = {marker: [] for marker in markers if marker != 'ATPADP'}

    for folder in os.listdir(path):
        if "ATPADP" in folder:
            df_atpadp = get_ATP_ADP_ratio(f'{path}/{folder}')
            list_of_df_atpadp.append(df_atpadp)
        for marker in markers:
            if marker != 'ATPADP' and marker in folder:
                df_marker = get_mean_ratio(f'{path}/{folder}', marker)
                list_of_other_markers[marker].append(df_marker)
    atpadp_concat = pd.concat(list_of_df_atpadp)
    # preprocess adpatp df and saved all the df in specific folder
    preprocessed_adpatp = preprocess_atpadp_tracks(atpadp_concat, csv_output_directory) 
    preprocessed_adpatp_np = preprocessed_adpatp.to_numpy()
    
    df_combined_all = preprocessed_adpatp.copy()
    # Merge with other marker data
    for marker, dfs in list_of_other_markers.items():
        if dfs:
            marker_concat = pd.concat(dfs)
            df_combined_all = df_combined_all.merge(marker_concat, how='inner', left_index=True, right_index=True)

    df_combined_all.to_csv(f'{csv_output_directory}/perceval_preprocessed.csv')
    
    if len(markers) == 3:
        #Tkinter scatter plot
        root = tk.Tk()
        root.title("Scatter Viewer")
        fig, ax = plot_scatter_markers(df_combined_all, markers, fig_output_directory)
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack()
        # Open pop-up
        popup = ScatterPopup(root, ax, canvas,df_combined_all, markers)
        root.mainloop()

        # heatmap/histogramme on one population
        name = "one_population"
        plot_heatmaps_markers(df_combined_all, markers, name, fig_output_directory)
        plot_histogram(df_combined_all, markers, name, fig_output_directory, color=None)

        # Analysis on subpopulations
        if popup.selected_points:
            fig.savefig(f"{fig_output_directory}/scatter_plot_markers_with_population.png")
            for i, (subset, name) in enumerate(zip(popup.selected_points, popup.population_names)):
                print(f"> Analyse de {name} ({len(subset)} points)")
                fig_condition = os.path.join(fig_output_directory, name) 
                if not os.path.exists(fig_condition):
                    os.makedirs(fig_condition)
                subset.to_csv(f"{fig_condition}/{name}.csv", index=False)
                
                analyse_population(
                    df_subset=subset,
                    name=name,
                    markers=markers,
                    fig_output_directory=fig_condition,
                    prediction=prediction,
                    preprocessed_adpatp=preprocessed_adpatp,
                    preprocessed_adpatp_np=preprocessed_adpatp_np,
                    csv_output_directory=csv_output_directory,
                    sample_name=sample_name
                )
        else:
            print("No condition selected – Analysis on a single population.")

    # model predictions
    if prediction != 'no':
        print('--- Run predictions ---')
        model = joblib.load("model_perceval.joblib")
        predictions = model.predict(preprocessed_adpatp_np)
        print('Finish !')
    
    # pie chart & tracks plot
        preprocessed_adpatp['cluster'] = predictions
        preprocessed_adpatp_cluster = preprocessed_adpatp.sort_values(by=['cluster']) 
        preprocessed_adpatp_cluster.to_csv(f'{csv_output_directory}/cluster_perceval_preprocessed.csv')
        pie_chart(preprocessed_adpatp_cluster, fig_output_directory, sample_name)
        plot_tracks(preprocessed_adpatp_cluster, fig_output_directory)
    
    print("Final finish !")
