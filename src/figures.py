import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
import joblib

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plot_heatmaps_markers(dataframe, markers, name, fig_output_directory):
    """
    Build heatmaps for up to three markers in the given order.
    
    Parameters:
    - dataframe: pandas DataFrame containing the data to plot.
    - markers: list of strings, the names of the markers to plot (ATP/ADP, F480, CD86 or others).
               Max length is 3, first one is assumed to be ATP/ADP which spans multiple columns.
    - fig_output_directory: string, the path where the figure will be saved.
    
    The function will plot up to three heatmaps (for ATP/ADP, F480, and CD86 or other specified markers).
    """
    print("Plotting heatmaps...")
    plt.close()
    # Define color palettes 
    atpadp_cmap = sns.color_palette(
        palette=["midnightblue", "navy", "blue", "darkturquoise", "green", "lightgreen", "yellow", "orange", "red", "fuchsia", "mediumorchid", "pink", "whitesmoke"],
        desat=None, as_cmap=False
    )
    plasma_cmap = cm.get_cmap('plasma')
    # Number of heatmaps (max 3)
    num_heatmaps = min(3, len(markers))
    if 'MHCII' in markers:
          dataframe = dataframe.sort_values(by=['MHCII'])
    # Create subplots with ncols equal to the number of heatmaps
    fig, axes = plt.subplots(figsize=(20, 20), ncols=num_heatmaps, width_ratios=[10] + [1] * (num_heatmaps - 1))
    fig.subplots_adjust(wspace=0.05)
    # Ensure axes is iterable even if there's only one marker
    if num_heatmaps == 1:
        axes = [axes]
        atpadp_df = dataframe.iloc[:, :]
    else:
        atpadp_df = dataframe.iloc[:, :-num_heatmaps + 1]
    # Process ATP/ADP separately since it spans multiple columns
    sns.heatmap(
        atpadp_df,  # All columns except the last two for other markers
        cmap=atpadp_cmap,  # First color palette
        ax=axes[0], 
        cbar=False, 
        yticklabels=False, 
        linewidth=0, 
        vmin=0, vmax=255
    )
    fig.colorbar(axes[0].collections[0], ax=axes[0], location="bottom", use_gridspec=False, pad=0.05, fraction=0.046, shrink=0.2)
    axes[0].set_ylabel("ATP/ADP clusters")
    axes[0].tick_params(rotation=90)
    # Process the remaining markers (F480, CD86, or others) in order
    for i in range(1, num_heatmaps):
        marker = markers[i]
        # Select the appropriate color palette for the marker based on its order
        #palette = color_palettes[i] 
        # Select the appropriate column for this marker:
        if i == num_heatmaps - 1:
            marker_data = dataframe.iloc[:, -1:]  # Last column
        else:
            marker_data = dataframe.iloc[:, -2:-1]  # Second-to-last column
        sns.heatmap(
            marker_data, 
            cmap=plasma_cmap, 
            ax=axes[i], 
            cbar=False, 
            yticklabels=False, 
            xticklabels=False, 
            vmin=None, vmax=None
        )
        fig.colorbar(axes[i].collections[0], ax=axes[i], location="bottom", use_gridspec=False, pad=0.05, fraction=0.046, shrink=1.0)
        axes[i].set_ylabel(marker)
        axes[i].tick_params(rotation=90)
    # Save the figure
    plt.savefig(f'{fig_output_directory}/{name}_heatmap_{len(markers)}markers.pdf')
    #show_heatmap_in_tkinter_with_sorting(dataframe,markers) #show the heatmaps
    print('Finish!')


def plot_histogram(dataframe, markers, name, fig_output_directory, color='blue'):
    """
    Plot KDE histograms for given markers from a DataFrame.
    
    Parameters:
        dataframe (pd.DataFrame): DataFrame containing marker columns.
        markers (list): List of marker names (column names in the DataFrame).
        name (str): Base name for the output files.
        fig_output_directory (str): Directory path to save the figures.
        color (str): Color used for all histograms.
    """
    for marker in markers:
        if marker not in dataframe.columns:
            print(f"Warning: Marker '{marker}' not found in DataFrame columns.")
            continue

        print(f"Plot {marker} histogram...")
        plt.figure()
        sns.kdeplot(data=dataframe[marker], color=color, fill=True, log_scale=True, label=marker)
        plt.xlabel(f"{marker} Sum Intensity Value (Log)")
        plt.legend()
        
        output_path = os.path.join(fig_output_directory, f"{name}_{marker}_hist.png")
        plt.savefig(output_path)
        plt.close()
        print(f"Saved: {output_path}")

def pie_chart(dataframe,fig_output_directory, sample_name):
    """ Plot pie chart
    Input
        dataframe : pandas df
            df of interest
        fig_output_directory : string
            output directory path
        sample_name : string
            sample name
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
               4:'#ff6400'}
    plt.figure(figsize=(6,6))
    plt.pie(counts, labels=cluster, colors = [colors_pie[key] for key in cluster], autopct='%1.1f%%')
    plt.title(sample_name)
    plt.savefig(f'{fig_output_directory}/{sample_name}_piechart.pdf')
    print('Finish !')

def plot_tracks(dataframe, fig_output_directory):
    """ Plot tracks colored by cluster
    Input
        dataframe : pandas df
            df of interest
        fig_output_directory : string
            output directory path
    """
    colors = {1:'darkturquoise',
            2:'lightgreen',
            3:'yellow',
            4:'orange'}
    dataframe.iloc[:,:-1].T.plot.line(color=dataframe['cluster'].map(colors),figsize=(15,9),lw=0.6)
    handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=v, label=k, markersize=8) for k, v in colors.items()]
    plt.axvline(x = 9, color = 'black', label = 'axvline - full height', ls=":", lw = 2)
    plt.legend(handles=handles)
    plt.xlabel("Frame number")
    plt.ylabel("ATP/ADP")
    plt.ylim(-5, 250)
    plt.xlim(0, dataframe.shape[1]-2)
    plt.savefig(f'{fig_output_directory}/tracks_by_cluster.png')

def plot_scatter_markers(dataframe,markers, fig_output_directory):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(dataframe.iloc[:,-2:-1], dataframe.iloc[:,-1:], c='black', s=6)
    ax.set_yscale('log')
    ax.set_xscale('log')
    plt.xlabel(dataframe.columns[-2])
    plt.ylabel(dataframe.columns[-1])
    plt.savefig(f'{fig_output_directory}/scatter_plot_markers.png')
    return(fig, ax)

def analyse_population(
    df_subset, 
    name, 
    markers, 
    fig_output_directory, 
    prediction, 
    preprocessed_adpatp, 
    preprocessed_adpatp_np, 
    csv_output_directory, 
    sample_name
):
    # Tracés classiques
    plot_heatmaps_markers(df_subset, markers, name, fig_output_directory)
    plot_histogram(df_subset, markers, name, fig_output_directory, color=None)

    # Prédiction si activée
    if prediction != 'no':
        print(f'--- Run predictions for {name} ---')
        model = joblib.load("model_perceval.joblib")

        mask = preprocessed_adpatp.index.isin(df_subset.index)
        sub_preprocessed_np = preprocessed_adpatp_np[mask]
        sub_preprocessed = preprocessed_adpatp.loc[mask].copy()

        predictions = model.predict(sub_preprocessed_np)
        sub_preprocessed['cluster'] = predictions

        sub_preprocessed_cluster = sub_preprocessed.sort_values(by='cluster')
        sub_preprocessed_cluster.to_csv(f'{csv_output_directory}/cluster_perceval_preprocessed_{name}.csv')

        pie_chart(sub_preprocessed_cluster, fig_output_directory, f"{sample_name}_{name}")
        plot_tracks(sub_preprocessed_cluster, fig_output_directory)