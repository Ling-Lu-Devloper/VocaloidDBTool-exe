import os
import sys
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
	
# Load the phoneme JSON data
script_directory = os.path.dirname(os.path.abspath(__file__))
phonemes_json_path = os.path.join(script_directory, 'phonemes.json')

with open(phonemes_json_path, 'r') as file:
    phonemes_data = json.load(file)

# Create a dictionary for easy lookup
phonemes_dict = {entry['kana']: entry['phoneme'] for entry in phonemes_data}

# Function to convert kana sequence to phonemes
def convert_kana_sequence_to_phonemes(kana_sequence):
    words = kana_sequence.split()
    phonemes = []
    for word in words:
        phoneme = phonemes_dict.get(word, word)
        phonemes.append(phoneme)
    return ' '.join(phonemes)

# Function to process a single .seg file
def process_seg_file(input_path):
    with open(input_path, 'r', encoding='utf-8') as seg_file:
        seg_lines = seg_file.read().split('\n')

    converted_lines = []
    convert_lines = False
    header_lines = []

    for line in seg_lines:
        if line.startswith('='):
            convert_lines = True
            header_lines.append(line)
        elif convert_lines:
            parts = line.split()
            if len(parts) == 3:
                kana_sequence, start_time, end_time = parts
                phoneme_sequence = convert_kana_sequence_to_phonemes(kana_sequence)
                converted_lines.append(f"{phoneme_sequence}\t\t{start_time}\t\t{end_time}")
            else:
                converted_lines.append(line)

    n_phonemes = len(converted_lines)  # Subtract 1 to exclude the "=====" line
    header_lines.insert(0, f'nPhonemes {n_phonemes}')
    header_lines.insert(1, 'articulationsAreStationaries 0')
    header_lines.insert(2, 'phoneme   BeginTime   EndTime')

    converted_content = '\n'.join(header_lines + converted_lines)

    with open(input_path, 'w', encoding='utf-8') as seg_file:
        seg_file.write(converted_content)

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)

def convert_files():
    directory = directory_entry.get()

    if not directory:
        messagebox.showerror("错误", "请选择一个目录.")
        return

    for filename in os.listdir(directory):
        if filename.endswith(".seg"):
            input_path = os.path.join(directory, filename)
            process_seg_file(input_path)

    messagebox.showinfo("成功", "转换完成.")

# Create the main application window
root = tk.Tk()
root.title("SEG File Conversion")

# Create a style
style = ttk.Style(root)

# Import the tcl file
root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

# Set the theme with the theme_use method
style.theme_use("forest-dark")

# Create a frame for the input fields
input_frame = ttk.Frame(root, padding=10)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Directory selection
directory_label = ttk.Label(input_frame, text='选择目录:')
directory_label.grid(row=0, column=0, sticky='w')

directory_entry = ttk.Entry(input_frame, width=40)
directory_entry.grid(row=0, column=1, padx=(5, 0), sticky='w')

directory_button = ttk.Button(input_frame, text='浏览', command=browse_directory)
directory_button.grid(row=0, column=2, padx=(5, 0), sticky='w')

# Convert button
convert_button = ttk.Button(root, text='转换 SEG 文件', command=convert_files)
convert_button.grid(row=1, column=0, padx=10, pady=10)

# Start the GUI application
root.mainloop()
