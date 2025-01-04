import os
import sys
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

def load_segments(seg_file):
    segments = []
    in_segment_section = False

    with open(seg_file, 'r') as file:
        for line in file:
            if line.strip() == '===' or line.strip() == '=================================================':
                in_segment_section = True
                continue

            if in_segment_section:
                parts = line.strip().split()
                if len(parts) >= 3:
                    phoneme, begin_time, end_time = parts[0], float(parts[1]), float(parts[2])
                    segments.append((phoneme, begin_time, end_time))

    return segments

def transfer_phonemes(seg_folder1, seg_folder2, out_folder):
    os.makedirs(out_folder, exist_ok=True)

    seg_files1 = {}
    seg_files2 = {}

    for seg_filename1 in os.listdir(seg_folder1):
        if seg_filename1.endswith('.seg'):
            base_name = os.path.splitext(seg_filename1)[0]
            seg_files1[base_name] = os.path.join(seg_folder1, seg_filename1)

    for seg_filename2 in os.listdir(seg_folder2):
        if seg_filename2.endswith('.seg'):
            base_name = os.path.splitext(seg_filename2)[0]
            seg_files2[base_name] = os.path.join(seg_folder2, seg_filename2)

    common_base_names = set(seg_files1.keys()).intersection(seg_files2.keys())

    for base_name in common_base_names:
        seg_file1 = seg_files1[base_name]
        seg_file2 = seg_files2[base_name]
        out_file = os.path.join(out_folder, base_name + '.seg')

        segments1 = load_segments(seg_file1)
        segments2 = load_segments(seg_file2)

        with open(out_file, 'w') as outfile:
            outfile.write("nPhonemes {}\n".format(len(segments2)))
            outfile.write("articulationsAreStationaries 0\n")
            outfile.write("phoneme\tBeginTime\tEndTime\n")
            outfile.write("=================================================\n")

            for i, segment2 in enumerate(segments2):
                if i < len(segments1):
                    phoneme1, begin_time1, end_time1 = segments1[i]
                    phoneme2, begin_time2, end_time2 = segment2
                    if phoneme1.strip():
                        outfile.write(f"{phoneme1}\t{begin_time2:.6f}\t{end_time2:.6f}\n")
                else:
                    phoneme2, begin_time2, end_time2 = segment2
                    outfile.write(f"{phoneme2}\t{begin_time2:.6f}\t{end_time2:.6f}\n")

        print(f"已将音素 从{seg_file1} 转移到 {seg_file2} 并保存在 {out_file}")

def browse_folder1():
    directory = filedialog.askdirectory()
    if directory:
        folder1_entry.delete(0, tk.END)
        folder1_entry.insert(0, directory)

def browse_folder2():
    directory = filedialog.askdirectory()
    if directory:
        folder2_entry.delete(0, tk.END)
        folder2_entry.insert(0, directory)

def browse_output_folder():
    directory = filedialog.askdirectory()
    if directory:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, directory)

def convert_phonemes():
    folder1 = folder1_entry.get()
    folder2 = folder2_entry.get()
    output_folder = output_folder_entry.get()

    if not os.path.exists(folder1) or not os.path.exists(folder2):
        messagebox.showerror("错误", "输入的文件夹不存在.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    transfer_phonemes(folder1, folder2, output_folder)
    messagebox.showinfo("成功", "转换完成.")

# Create the main application window
root = tk.Tk()
root.title("音素转移器")

# Import the tcl file
root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

# Set the theme with the theme_use method
style = ttk.Style()
style.theme_use("forest-dark")

# Create a frame for the input fields
input_frame = ttk.Frame(root, padding=10)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Folder 1
folder1_label = ttk.Label(input_frame, text='文件夹一 (Donor):')
folder1_label.grid(row=0, column=0, sticky='w')

folder1_entry = ttk.Entry(input_frame, width=40)
folder1_entry.grid(row=0, column=1, padx=(5, 0), sticky='w')

folder1_button = ttk.Button(input_frame, text='浏览', command=browse_folder1)
folder1_button.grid(row=0, column=2, padx=(5, 0), sticky='w')

# Folder 2
folder2_label = ttk.Label(input_frame, text='文件夹2 (Receiver):')
folder2_label.grid(row=1, column=0, sticky='w')

folder2_entry = ttk.Entry(input_frame, width=40)
folder2_entry.grid(row=1, column=1, padx=(5, 0), sticky='w')

folder2_button = ttk.Button(input_frame, text='浏览', command=browse_folder2)
folder2_button.grid(row=1, column=2, padx=(5, 0), sticky='w')

# Output folder
output_folder_label = ttk.Label(input_frame, text='输出文件夹:')
output_folder_label.grid(row=2, column=0, sticky='w')

output_folder_entry = ttk.Entry(input_frame, width=40)
output_folder_entry.grid(row=2, column=1, padx=(5, 0), sticky='w')

output_folder_button = ttk.Button(input_frame, text='浏览', command=browse_output_folder)
output_folder_button.grid(row=2, column=2, padx=(5, 0), sticky='w')

# Convert button
convert_button = ttk.Button(root, text='转移音素', command=convert_phonemes)
convert_button.grid(row=1, column=0, padx=10, pady=10)

# Start the GUI application
root.mainloop()
