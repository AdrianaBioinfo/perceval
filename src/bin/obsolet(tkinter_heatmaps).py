import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from figures import plot_heatmaps_markers2
"""
class HeatmapApp(tk.Tk):
    def __init__(self, dataframe, markers):
        super().__init__()
        self.title("Heatmap Viewer")
        self.geometry("1200x700")
        self.df = dataframe
        self.original_df = dataframe.copy()
        self.markers = markers

        self.sort_order = True

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(self.button_frame, text="Trier croissant", command=self.sort_ascending).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Trier décroissant", command=self.sort_descending).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Réinitialiser", command=self.reset).pack(side=tk.LEFT, padx=5)

        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.plot()

    def sort_ascending(self):
        self.df = self.df.sort_values(by=self.df.columns[-1], ascending=True)
        self.plot()

    def sort_descending(self):
        self.df = self.df.sort_values(by=self.df.columns[-1], ascending=False)
        self.plot()

    def reset(self):
        self.df = self.original_df.copy()
        self.plot()

    def plot(self):
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        num_heatmaps = min(3, len(self.markers))
        fig, axes = plt.subplots(figsize=(15, 6), ncols=num_heatmaps)
        if num_heatmaps == 1:
            axes = [axes]

        # Appelle ta fonction depuis figures.py
        plot_heatmaps_markers2(self.df, self.markers, fig=fig, axes=axes)

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

"""   