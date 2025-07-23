import tkinter as tk
from tkinter import messagebox

class ScatterPopup:
    def __init__(self, root, ax, canvas, markers):
        self.root = root
        self.ax = ax
        self.canvas = canvas
        self.markers = markers
        self.hline = None
        self.vline = None
        self.selected_coords = None
        self.selected_conditions = []

        self.popup = tk.Toplevel(root)
        self.popup.title("Select X and Y")

        self.popup.protocol("WM_DELETE_WINDOW", self.cancel)

        tk.Label(self.popup, text="X value:").pack()
        self.x_entry = tk.Entry(self.popup)
        self.x_entry.pack()

        tk.Label(self.popup, text="Y value:").pack()
        self.y_entry = tk.Entry(self.popup)
        self.y_entry.pack()

        button_frame = tk.Frame(self.popup)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Preview", command=self.preview).pack(side="left", padx=5)
        tk.Button(button_frame, text="OK", command=self.ok).pack(side="left", padx=5)
        tk.Button(button_frame, text="Don't add axes", command=self.cancel).pack(side="left", padx=5)

        # Analysis section
        tk.Label(self.popup, text="\nAnalysis:").pack()

        tk.Button(self.popup, text="Continue analysis on one population", command=self.analyse_one_population).pack(pady=3)
        tk.Button(self.popup, text="Continue analysis on X populations", command=self.show_population_options).pack(pady=3)

        self.condition_vars = {
            "low_low": tk.BooleanVar(),
            "high_low": tk.BooleanVar(),
            "low_high": tk.BooleanVar(),
            "high_high": tk.BooleanVar()
        }
        self.check_frame = None

    def show_population_options(self):
        if self.check_frame:
            self.check_frame.destroy()
        
        m1 = self.markers[1]
        m2 = self.markers[2]
        self.check_frame = tk.Frame(self.popup)
        self.check_frame.pack(pady=5)

        tk.Label(self.check_frame, text="Select conditions:").pack()

        tk.Checkbutton(self.check_frame, text=f"{m1} 'low' & {m2} 'low'", variable=self.condition_vars["low_low"]).pack(anchor="w")
        tk.Checkbutton(self.check_frame, text=f"{m1} 'high' & {m2} 'low'", variable=self.condition_vars["high_low"]).pack(anchor="w")
        tk.Checkbutton(self.check_frame, text=f"{m1} 'low' & {m2} 'high'", variable=self.condition_vars["low_high"]).pack(anchor="w")
        tk.Checkbutton(self.check_frame, text=f"{m1} 'high' & {m2} 'high'", variable=self.condition_vars["high_high"]).pack(anchor="w")

        tk.Button(self.check_frame, text="Start analysis", command=self.analyse_x_populations).pack(pady=5)

    def preview(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            self.update_lines(x, y)
        except ValueError:
            print("Invalid input")

    def ok(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            self.selected_coords = (x, y)
            self.update_lines(x, y)
        except ValueError:
            print("Invalid input")
            return

        self.popup.destroy()
        self.root.destroy()

    def cancel(self):
        self.popup.destroy()
        self.root.destroy()

    def update_lines(self, x, y):
        if self.hline:
            self.hline.remove()
        if self.vline:
            self.vline.remove()

        self.hline = self.ax.axhline(y=y, color='red', linestyle='-')
        self.vline = self.ax.axvline(x=x, color='blue', linestyle='-')
        self.canvas.draw()

    def analyse_one_population(self):
        messagebox.showinfo("Analysis", "Analysis on one population triggered.")
        # Call your function here

    def analyse_x_populations(self):
        # Check that X and Y are valid floats
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid numeric values for X and Y.")
            return

        # Make sure at least one condition is selected
        self.selected_conditions = [key for key, var in self.condition_vars.items() if var.get()]
        if not self.selected_conditions:
            tk.messagebox.showerror("Error", "Please select at least one condition for analysis.")
            return

        # Save the coordinates (in case the user didn’t press OK)
        self.selected_coords = (x, y)
        self.update_lines(x, y)

        self.popup.destroy()
        self.root.destroy()
