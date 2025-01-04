import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import argparse
import re
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def convert_lab_to_seg(input_directory, output_directory):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Process each lab file
    for lab_file_name in os.listdir(input_directory):
        if lab_file_name.endswith(".lab"):
            input_lab_file = os.path.join(input_directory, lab_file_name)
            output_seg_file = os.path.join(output_directory, lab_file_name.replace(".lab", ".seg"))

            # Initialize variables
            phoneme_list = []

            # Open the input lab for reading
            with open(input_lab_file, 'r') as infile:
                lines = infile.readlines()

            for line in lines:
                line = line.strip()
                # Use regular expressions to extract phonemes, start times, and end times
                match = re.match(r'(\d+)\s+(\d+)\s+(.+)', line)
                if match:
                    start_time = float(match.group(1)) / 1e7  # Convert time to seconds
                    end_time = float(match.group(2)) / 1e7
                    phoneme = match.group(3)

                    # Remove trailing numbers from phonemes (you might remove this)
                    phoneme = ''.join([c for c in phoneme if not c.isdigit()])

                    # Replace "R" and "pau" with "Sil" (mostly for arpabet)
                    if phoneme == "R" or phoneme == "pau":
                        phoneme = "Sil"

                    phoneme_list.append((phoneme, start_time, end_time))

            if phoneme_list:
                # .seg writing
                with open(output_seg_file, 'w') as outfile:
                    outfile.write("nPhonemes {}\n".format(len(phoneme_list)))
                    outfile.write("articulationsAreStationaries 0\n")
                    outfile.write("phoneme\t\tBeginTime\t\tEndTime\n")
                    outfile.write("=" * 49 + "\n")
                    for phoneme, start_time, end_time in phoneme_list:
                        outfile.write("{}\t\t{:.6f}\t\t{:.6f}\n".format(phoneme, start_time, end_time))

                print("转换完成", lab_file_name)
            else:
                print("跳过空文件:", lab_file_name)

    print("所有转换完成")

def browse_input_directory():
    directory = filedialog.askdirectory()
    if directory:
        input_directory_entry.delete(0, tk.END)
        input_directory_entry.insert(0, directory)

def browse_output_directory():
    directory = filedialog.askdirectory()
    if directory:
        output_directory_entry.delete(0, tk.END)
        output_directory_entry.insert(0, directory)

def convert_lab_files():
    input_directory = input_directory_entry.get()
    output_directory = output_directory_entry.get()

    if not os.path.exists(input_directory):
        messagebox.showerror("错误", "输入目录不存在")
        return

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    convert_lab_to_seg(input_directory, output_directory)
    messagebox.showinfo("成功", "转换完成")

# Create the main application window
root = tk.Tk()
root.title("Lab -> Seg转换器")

# Import the tcl file
root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

# Set the theme with the theme_use method
style = ttk.Style()
style.theme_use("forest-dark")

# Create a frame for the input fields
input_frame = ttk.Frame(root, padding=10)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Input directory
input_directory_label = ttk.Label(input_frame, text='输入目录:')
input_directory_label.grid(row=0, column=0, sticky='w')

input_directory_entry = ttk.Entry(input_frame, width=40)
input_directory_entry.grid(row=0, column=1, padx=(5, 0), sticky='w')

input_directory_button = ttk.Button(input_frame, text='浏览', command=browse_input_directory)
input_directory_button.grid(row=0, column=2, padx=(5, 0), sticky='w')

# Output directory
output_directory_label = ttk.Label(input_frame, text='输出目录:')
output_directory_label.grid(row=1, column=0, sticky='w')

output_directory_entry = ttk.Entry(input_frame, width=40)
output_directory_entry.grid(row=1, column=1, padx=(5, 0), sticky='w')

output_directory_button = ttk.Button(input_frame, text='浏览', command=browse_output_directory)
output_directory_button.grid(row=1, column=2, padx=(5, 0), sticky='w')

# Convert button
convert_button = ttk.Button(root, text='转换', command=convert_lab_files)
convert_button.grid(row=1, column=0, padx=10, pady=10)

# Start the GUI application
root.mainloop()
