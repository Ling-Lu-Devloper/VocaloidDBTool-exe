import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import sys
import subprocess

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
	
def convert_trans_file(input_file, output_file):
    with open(input_file, "r") as infile:
        lines = infile.readlines()

    output_lines = []
    top_line = lines[0].strip()  # Keep the top line as is
    output_lines.append(top_line + "\n")

    for line in lines[1:-1]:  # Exclude the first and last lines
        if '[' in line:
            tokens = line.strip().split(' ')
            for token in tokens[1:]:
                output_lines.append("[" + token)
                output_lines.append("\n")
        else:
            tokens = line.strip().split('][')
            for token in tokens:
                phonemes = token.split(' ')
                if len(phonemes) > 1:
                    output_lines.append("[" + phonemes[1] + ' ')
            output_lines.append("\n")

    with open(output_file, "w") as outfile:
        outfile.writelines(output_lines)

def convert_trans_files():
    input_dir = input_dir_entry.get()
    output_dir = output_dir_entry.get()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    converted_files = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".trans"):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            convert_trans_file(input_file, output_file)
            converted_files.append(filename)

    terminal_output.config(state=tk.NORMAL)
    if converted_files:
        terminal_output.insert(tk.END, "以下文件转换完成:\n")
        for file in converted_files:
            terminal_output.insert(tk.END, file + "\n")
    else:
        terminal_output.insert(tk.END, "没有找到用于转换的 .trans 文件.\n")
    terminal_output.config(state=tk.DISABLED)

# Create the main application window
root = tk.Tk()
root.title(".trans 文件转换器")

# Import the tcl file
root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

# Set the theme with the theme_use method
style = ttk.Style()
style.theme_use("forest-dark")

# Make the app responsive
for i in range(2):
    root.columnconfigure(index=i, weight=1)
for i in range(4):
    root.rowconfigure(index=i, weight=1)

# Create a Frame for inputs and buttons
input_frame = ttk.Frame(root)
input_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Input for .trans files directory
input_dir_label = ttk.Label(input_frame, text="Articulation .trans 输入目录:")
input_dir_label.grid(row=0, column=0, sticky="w")
input_dir_entry = ttk.Entry(input_frame, width=40)
input_dir_entry.grid(row=0, column=1, padx=(0, 5))
input_dir_browse = ttk.Button(input_frame, text="浏览", command=lambda: browse_directory(input_dir_entry))
input_dir_browse.grid(row=0, column=2)

# Input for output directory
output_dir_label = ttk.Label(input_frame, text="Stationary .trans 输出目录:")
output_dir_label.grid(row=1, column=0, sticky="w")
output_dir_entry = ttk.Entry(input_frame, width=40)
output_dir_entry.grid(row=1, column=1, padx=(0, 5))
output_dir_browse = ttk.Button(input_frame, text="浏览", command=lambda: browse_directory(output_dir_entry))
output_dir_browse.grid(row=1, column=2)

# Convert button
convert_button = ttk.Button(input_frame, text="转换 .trans 文件", command=convert_trans_files)
convert_button.grid(row=2, column=0, columnspan=3, pady=10)

# Create a Frame for the terminal output
output_frame = ttk.Frame(root)
output_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")

# Terminal output
terminal_output = tk.Text(output_frame, height=10, width=60, state=tk.DISABLED)
terminal_output.grid(row=0, column=0, sticky="nsew")

# Function to browse for a directory and update the corresponding entry
def browse_directory(entry_widget):
    directory = filedialog.askdirectory()
    if directory:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, directory)

# Start the main loop
root.mainloop()
