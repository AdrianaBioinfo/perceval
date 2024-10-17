import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np # for f480 hist

def plot_heatmap(dataframe, fig_output_directory, sample_name, choose_color_palette):
    """ Build heatmaps
    From dataframe, plot the heatmaps
    Input
        dataframe : pandas df
            ATP/ADP or F480 or CD86 df
        fig_output_directory : string
            path to save the fig
        sample_name : string
            sample name 
        choose_color_palette : string
            "atpadp" or "f480" or "cd86"
    """
    print(f'--- Create {choose_color_palette} heatmap ---')
    # Choose color palette
    if choose_color_palette == "atpadp":
        color_palette = sns.color_palette(palette=["midnightblue","navy","blue", "darkturquoise", "green","lightgreen", "yellow", "orange", "red","fuchsia","mediumorchid","pink","whitesmoke"], desat=None, as_cmap=False)
    elif choose_color_palette == "f480":
        color_palette = matplotlib.colors.LinearSegmentedColormap.from_list("color_palette", ["plum","purple","indigo","blue"])
    elif choose_color_palette == "cd86":
        color_palette = matplotlib.colors.LinearSegmentedColormap.from_list("color_palette", ["gainsboro","grey","dimgray","black"])
    # Plot the figure
    fig, (ax) = plt.subplots(figsize = (15,15), ncols=1)
    sns_plot = sns.heatmap(dataframe, cmap=color_palette, ax=ax, cbar=False, yticklabels=False, linewidth=.7, vmax=255)
    fig.suptitle(f'{choose_color_palette} heatmap')
    fig.colorbar(ax.collections[0], ax=ax,location="left", use_gridspec=False, pad=0.05,fraction=0.026)
    ax.tick_params(rotation=90)
    plt.savefig(f'{fig_output_directory}/{sample_name}_heatmap.png')
    print('Finish !')

def plot_3_heatmaps(dataframe, fig_output_directory):
    """ Build heatmaps
    From dataframe, plot the ATP/ADP,
    F480 and CD86 heatmaps
    Input
        dataframe : pandas df
            ATP/ADP, F480, CD86 df
        fig_output_directory : string
            path to save the fig
    """
    print("Plot heatmaps...")
    plt.close()
    color_palette_atpadp = sns.color_palette(palette=["midnightblue","navy","blue", "darkturquoise", "green","lightgreen", "yellow", "orange", "red","fuchsia","mediumorchid","pink","whitesmoke"], desat=None, as_cmap=False)
    color_palette_f480 = matplotlib.colors.LinearSegmentedColormap.from_list("color_palette", ["plum","purple","indigo","blue"])
    color_palette_cd86 = matplotlib.colors.LinearSegmentedColormap.from_list("color_palette", ["gainsboro","grey","dimgray","black"])

    fig, (ax,ax2,ax3) = plt.subplots(figsize = (20,20), ncols=3, width_ratios=[10, 1,1])
    fig.subplots_adjust(wspace=0.05)

    sns_plot = sns.heatmap(dataframe.iloc[:,:-2], cmap=color_palette_atpadp, ax=ax, cbar=False, yticklabels=False, linewidth=.5, vmin=0, vmax=255)
    fig.colorbar(ax.collections[0], ax=ax,location="bottom", use_gridspec=False, pad = 0.05, fraction=0.046, shrink=0.2)
    ax.set_ylabel('ATP/ADP clusters')
    ax.tick_params(rotation=90)

    sns_plot = sns.heatmap(dataframe.iloc[:,-1:], cmap=color_palette_cd86, ax=ax2, cbar=False, yticklabels=False, xticklabels=False, vmin=None, vmax = None)
    fig.colorbar(ax2.collections[0], ax=ax2,location="bottom", use_gridspec=False, pad = 0.05,fraction=0.046, shrink=1.1)
    ax2.set_ylabel('CD86')

    sns_plot = sns.heatmap(dataframe.iloc[:,-2:-1], cmap=color_palette_f480, ax=ax3, cbar=False, yticklabels=False,xticklabels=False, vmin=None, vmax = None)
    fig.colorbar(ax3.collections[0], ax=ax3,location="bottom", use_gridspec=False, pad = 0.05,fraction=0.046, shrink=0.9)
    ax3.set_ylabel('F480')
    plt.savefig(f'{fig_output_directory}/heatmap3.png')
    print('Finish !')

def plot_histogram(dataframe, label, fig_output_directory, color = None):
    """ Plot distribution
    Of F480, CD86 or other values
    Input
        dataframe : pandas df
            F480, CD86 or other df
        label : strings
            Name of the variable
        fig_output_directory : string
            path to save the fig
        color : string
            color for the graph
    """
    print(f"Plot {label} histogram...")
    plt.close()
    sns.kdeplot(data=dataframe.squeeze(), color=color, fill=True, log_scale = True, label=label)
    plt.xlabel(f"{label} Sum Intensity Value (Log)")
    plt.legend()
    plt.savefig(f'{fig_output_directory}/{label}_hist.png')
    print('Finish !')
    