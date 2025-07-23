from matplotlib.widgets import PolygonSelector
from matplotlib.path import Path
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog

class ScatterPopup:
    def __init__(self, root, ax, canvas, df, markers):
        self.root = root
        self.ax = ax
        self.canvas = canvas
        self.df = df
        self.markers = markers

        self.selected_points = []       # List of selected DataFrames
        self.population_names = []      # Names of the selected populations
        self.select_labels = []         # Displayed tkinter labels

        self.popup = tk.Toplevel(root)
        self.popup.title("Polygon Selection Tool")
        self.popup.transient(root)      # Always stay on top of the main window
        self.popup.lift()               # Raise the window
        self.popup.attributes('-topmost', True)  # Keep it visually on top

        tk.Label(self.popup, text="Use the button below to draw a polygon.").pack(pady=5)

        tk.Button(self.popup, text="Draw a polygon", command=self.start_polygon_selection).pack(pady=5)
        tk.Button(self.popup, text="Remove last selection", command=self.remove_last_selection).pack(pady=5)

        self.name_list_frame = tk.Frame(self.popup)
        self.name_list_frame.pack(pady=5)

        tk.Button(self.popup, text="OK (Finish)", command=self.ok).pack(pady=5)
        tk.Button(self.popup, text="Cancel", command=self.cancel).pack(pady=5)

        self.selector = None
        self.poly_count = 0

        # Handle closing either window
        self.popup.protocol("WM_DELETE_WINDOW", self.ok)
        self.root.protocol("WM_DELETE_WINDOW", self.ok)

    def start_polygon_selection(self):
        self.selector = PolygonSelector(self.ax, self.onselect, useblit=True)
        self.canvas.draw_idle()

    def onselect(self, verts):
        path = Path(verts)
        xdata = self.df[self.df.columns[-2]].values
        ydata = self.df[self.df.columns[-1]].values
        points = np.column_stack((xdata, ydata))

        mask = path.contains_points(points)
        selected = self.df[mask]
        self.selected_points.append(selected)

        self.poly_count += 1
        default_name = f"population {self.poly_count}"
        name = simpledialog.askstring(
            "Population name",
            "Enter a name for the selected population:",
            initialvalue=default_name,
            parent=self.popup
        )
        if not name:
            name = default_name
        self.population_names.append(name)

        print(f"{len(selected)} points selected for '{name}'.")

        # Show in UI
        label = tk.Label(self.name_list_frame, text=f"{name}: {len(selected)} points")
        label.pack(anchor="w")
        self.select_labels.append(label)

        messagebox.showinfo("Selection complete", f"{len(selected)} points added under the name: {name}")

    def remove_last_selection(self):
        if self.selected_points:
            removed_name = self.population_names.pop()
            self.selected_points.pop()
            self.poly_count -= 1

            label = self.select_labels.pop()
            label.destroy()

            print(f"Selection '{removed_name}' removed.")
        else:
            messagebox.showinfo("Nothing to remove", "There is no selection to remove.")

    def ok(self):
        try:
            self.popup.destroy()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass

    def cancel(self):
        self.selected_points = []
        self.population_names = []
        self.ok()
