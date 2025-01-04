import os
import sys
import json
import re
import argparse
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
	
# Load the hiragana JSON data from the same directory as the script
script_directory = os.path.dirname(os.path.abspath(__file__))
hiragana_json_path = os.path.join(script_directory, 'hiragana.json')

with open(hiragana_json_path, 'r', encoding='utf-8') as file:
    hiragana_data = json.load(file)

# Create a dictionary for easy lookup
hiragana_dict = {entry['kana']: entry['phoneme'] for entry in hiragana_data}

# Create a set to store unknown kana characters
unknown_kana = set()

# Function to convert kana sequence to phonemes
def convert_kana_sequence_to_phonemes(kana_sequence):
    words = kana_sequence.split()
    phonemes = []
    for word in words:
        phoneme = hiragana_dict.get(word, word)
        if phoneme == word:
            unknown_kana.add(word)  # Add unknown kana characters to the set
        phonemes.append(phoneme)
    return ' '.join(phonemes)

# Function to process a single .lab file
def process_lab_file(input_path, split_phonemes):
    with open(input_path, 'r', encoding='utf-8') as lab_file:
        lab_content = lab_file.read()

    lines = lab_content.split('\n')
    converted_lines = []

    for line in lines:
        if not line:
            continue
        parts = line.split()
        if len(parts) == 3:
            start_time, end_time, kana_sequence = parts
            phoneme_sequence = convert_kana_sequence_to_phonemes(kana_sequence)
            phoneme_list = phoneme_sequence.split()
            
            if split_phonemes:
                for phoneme in phoneme_list:
                    converted_lines.append(f"{start_time} {end_time} {phoneme}")
            else:
                converted_lines.append(f"{start_time} {end_time} {phoneme_sequence}")

    converted_lab_content = '\n'.join(converted_lines)

    with open(input_path, 'w', encoding='utf-8') as lab_file:
        lab_file.write(converted_lab_content)

def browse_labs_directory():
    directory = filedialog.askdirectory()
    if directory:
        labs_directory_entry.delete(0, tk.END)
        labs_directory_entry.insert(0, directory)

def convert_labs():
    labs_directory = labs_directory_entry.get()

    if not os.path.exists(labs_directory):
        messagebox.showerror("错误", "LABs 目录不存在.")
        return

    split_phonemes = split_phonemes_var.get()

    for filename in os.listdir(labs_directory):
        if filename.endswith(".lab"):
            input_path = os.path.join(labs_directory, filename)
            process_lab_file(input_path, split_phonemes)

    # Create a text file to store unknown kana characters
    unknown_kana_file_path = os.path.join(script_directory, 'unknown_kana.txt')
    with open(unknown_kana_file_path, 'w', encoding='utf-8') as unknown_kana_file:
        for kana in unknown_kana:
            unknown_kana_file.write(kana + '\n')

    messagebox.showinfo("成功", "转换完成。未知假名字符保存到 'unknown_kana.txt' 未知假名字符.")

def toggle_split_phonemes():
    if split_phonemes_var.get():
        messagebox.showinfo("选项已启用", "音素将被分成单独的行.")
    else:
        messagebox.showinfo("选项已禁用", "音素将保持在同一行上.")

# Create the main application window
root = tk.Tk()
root.title("假名到音素转换器 （lab）")

# Import the tcl file
root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

# Set the theme with the theme_use method
style = ttk.Style()
style.theme_use("forest-dark")

# Create a frame for the input fields
input_frame = ttk.Frame(root, padding=10)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# LABs directory
labs_directory_label = ttk.Label(input_frame, text='LABs 目录:')
labs_directory_label.grid(row=0, column=0, sticky='w')

labs_directory_entry = ttk.Entry(input_frame, width=40)
labs_directory_entry.grid(row=0, column=1, padx=(5, 0), sticky='w')

labs_directory_button = ttk.Button(input_frame, text='浏览', command=browse_labs_directory)
labs_directory_button.grid(row=0, column=2, padx=(5, 0), sticky='w')

# Create a BooleanVar to store the checkbox state
split_phonemes_var = tk.BooleanVar()

# Add a checkbox to toggle splitting phonemes
split_phonemes_checkbox = ttk.Checkbutton(input_frame, text='拆分音素（实验性）', variable=split_phonemes_var, command=toggle_split_phonemes)
split_phonemes_checkbox.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='w')

# Convert button
convert_button = ttk.Button(root, text='转换 LABs', command=convert_labs)
convert_button.grid(row=1, column=0, padx=10, pady=10)

# Start the GUI application
root.mainloop()
