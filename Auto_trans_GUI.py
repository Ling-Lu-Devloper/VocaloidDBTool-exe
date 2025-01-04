import tkinter as tk
from tkinter import ttk
import sys
import os
import subprocess
import glob
import json
from tkinter import filedialog  # Import filedialog
from os import path

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Create a tkinter window
root = tk.Tk()
root.title("Auto-trans")

# Import the tcl file for the Forest theme
root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

# Set the theme with the theme_use method
style = ttk.Style(root)
style.theme_use("forest-dark")

# Create a BooleanVar with global scope
trans_check_var = tk.BooleanVar()

# Function to run the Auto-trans script
def run_auto_trans():
    # Your Auto-trans script code here
    jsonfile = open("hiragana.json", encoding='UTF-8', errors='ignore')
    pDict = json.load(jsonfile)
    jsonfile.close()
    
    wav_path = wav_entry.get()
    wav_path = wav_path + "\\"
    wav_files = glob.glob(f'{wav_path}*.wav')
    
    creating_ask = trans_check_var.get()  
    auto_creating = False
    if creating_ask:
        auto_creating = True

    for filepath in wav_files:
        name = path.basename(filepath)
        name = path.splitext(name)[0]

        filepath = filepath.replace(".wav", ".trans")
        trans_file = open(filepath, "w+")
        if auto_creating:
            nameLen = len(name)
            phoneme = "Sil "
            findCheck = False
            for i in range(0, nameLen):
                findCheck = False
                if i + 1 < nameLen:
                    for obj in pDict:
                        if obj['kana'] == (name[i] + name[i + 1]):
                            phoneme += obj['phoneme'] + " "
                            findCheck = True
                            break
                    if not findCheck:
                        for obj in pDict:
                            if obj['kana'] == (name[i]):
                                phoneme += obj['phoneme'] + " "
                                break
                else:
                    for obj in pDict:
                        if obj['kana'] == (name[i]):
                            phoneme += obj['phoneme'] + " "
                            break

            phoneme += "Sil"

            trans_file.write(phoneme)
            phonlist = phoneme.split()
            phonLen = len(phonlist)
            for i in range(0, phonLen):
                if i < phonLen - 1:
                    trans_file.write("\n[" + phonlist[i] + " " + phonlist[i + 1] + "]")
                else:
                    break

        trans_file.close()

    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "进程已完成!")
    result_text.config(state=tk.DISABLED)
        
def browse_wav_directory():
    wav_directory = filedialog.askdirectory()  # Open directory dialog
    wav_entry.delete(0, tk.END)  # Clear any previous input
    wav_entry.insert(0, wav_directory)  # Insert selected directory path

# Create a frame for the Auto-trans page
auto_trans_page = tk.Frame(root)
auto_trans_page.pack(padx=20, pady=20)

# Create a label and entry for the wav directory
wav_label = tk.Label(auto_trans_page, text="输入 wav 目录:")
wav_label.pack()
wav_entry = tk.Entry(auto_trans_page)
wav_entry.pack()
browse_button = ttk.Button(auto_trans_page, text="浏览", command=browse_wav_directory)
browse_button.pack()

# Create a checkbox for transcription writing
trans_check = ttk.Checkbutton(auto_trans_page, text="自动编写转录", variable=trans_check_var)
trans_check.pack()

# Create a "Run" button
run_button = ttk.Button(auto_trans_page, text="运行 Auto-trans 脚本", command=run_auto_trans)
run_button.pack()

# Create a text widget for the script output
result_text = tk.Text(auto_trans_page, height=5, width=40, state=tk.DISABLED)
result_text.pack()

# Start the tkinter main loop
root.mainloop()
