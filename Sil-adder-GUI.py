import os
import argparse
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def add_sil_phonemes(input_directory, output_directory, add_sil_at_beginning, add_sil_at_end):
    # 如果输出目录不存在，则创建该目录
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 处理 input 目录中的每个 seg 文件
    for seg_file_name in os.listdir(input_directory):
        if seg_file_name.endswith(".seg"):
            input_seg_file = os.path.join(input_directory, seg_file_name)
            output_seg_file = os.path.join(output_directory, seg_file_name)

            # 读取原始 .seg 文件
            with open(input_seg_file, 'r') as infile:
                lines = infile.readlines()

            # 找到出现 “=====” 行的行索引
            separator_line_index = lines.index("=================================================\n")

            # 从第一行非空音素中提取计时信息
            first_non_empty_phoneme_start = None
            first_non_empty_phoneme_end = None

            for line in lines[separator_line_index + 1:]:
                phoneme_values = line.strip().split('\t')
                if len(phoneme_values) >= 3:
                    first_non_empty_phoneme_start = phoneme_values[1]
                    first_non_empty_phoneme_end = phoneme_values[2]
                    break

            if add_sil_at_beginning:
                # 在顶部插入 “Sil” 并计算出结束时间
                new_sil_line = f"Sil\t\t0.000000\t\t{first_non_empty_phoneme_end}\n"
                lines.insert(separator_line_index + 1, new_sil_line)

            if add_sil_at_end:
                # 计算音素的数量
                num_phonemes = len(lines) - separator_line_index

            # 使用计算的计数更新 “nPhonemes” 行
            for i, line in enumerate(lines):
                if line.startswith("nPhonemes"):
                    current_value = int(line.split()[-1])
                    new_value = current_value + 1
                    lines[i] = f"nPhonemes {new_value}\n"
                    break

                # 查找最后一个非空音素的结束时间
                last_non_empty_phoneme_end = first_non_empty_phoneme_end
                for line in reversed(lines[separator_line_index + 1:]):
                    phoneme_values = line.strip().split('\t')
                    if len(phoneme_values) >= 3:
                        last_non_empty_phoneme_end = phoneme_values[2]
                        break

                # 在 .seg 文件中查找最大的结束时间
                largest_end_time = max(float(phoneme_values[2]) for line in lines[separator_line_index + 1:])

                # 格式化largest_end_time以包含所有小数，如果是整数，则为零
                if largest_end_time.is_integer():
                    largest_end_time = f"{largest_end_time:.6f}"
                else:
                    largest_end_time = str(largest_end_time)

                    # 将 “Sil” 设置在结束时间最长的末尾
                    lines[-1] = f"Sil\t\t{last_non_empty_phoneme_end}\t\t{last_non_empty_phoneme_end}\n"


            # 打开输出 .seg 文件进行写入
            with open(output_seg_file, 'w') as outfile:
                # 将整个修改后的列表写回文件
                outfile.writelines(lines)

            print("Sil 音素已添加至", seg_file_name)

    print("所有修改完成。")

def browse_input_directory():
    input_directory = filedialog.askdirectory()
    input_directory_entry.delete(0, tk.END)
    input_directory_entry.insert(0, input_directory)

def browse_output_directory():
    output_directory = filedialog.askdirectory()
    output_directory_entry.delete(0, tk.END)
    output_directory_entry.insert(0, output_directory)

def execute_script():
    input_directory = input_directory_entry.get()
    output_directory = output_directory_entry.get()
    add_sil_at_beginning = add_sil_at_beginning_var.get()
    add_sil_at_end = add_sil_at_end_var.get()
    add_sil_phonemes(input_directory, output_directory, add_sil_at_beginning, add_sil_at_end)
    result_label.config(text="修改完成。")

# 创建主窗口
root = tk.Tk()
root.title("添加 'Sil' 音素")

# 导入tcl文件
root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

# 使用theme_use方法导入皮肤
style = ttk.Style()
style.theme_use("forest-dark")

# 创建和配置控件
input_directory_label = ttk.Label(root, text="输入路径:")
input_directory_entry = ttk.Entry(root)
browse_input_button = ttk.Button(root, text="浏览", command=browse_input_directory)

output_directory_label = ttk.Label(root, text="输出路径:")
output_directory_entry = ttk.Entry(root)
browse_output_button = ttk.Button(root, text="浏览", command=browse_output_directory)

add_sil_at_beginning_var = tk.BooleanVar()
add_sil_at_beginning_checkbox = ttk.Checkbutton(root, text="在开头添加 'Sil' ", variable=add_sil_at_beginning_var)

add_sil_at_end_var = tk.BooleanVar()
add_sil_at_end_checkbox = ttk.Checkbutton(root, text="在末尾添加 'Sil' (实验性/损坏)", variable=add_sil_at_end_var)

execute_button = ttk.Button(root, text="执行", command=execute_script)
result_label = ttk.Label(root, text="")

# 控件布局
input_directory_label.grid(row=0, column=0, padx=10, pady=5)
input_directory_entry.grid(row=0, column=1, padx=10, pady=5)
browse_input_button.grid(row=0, column=2, padx=10, pady=5)

output_directory_label.grid(row=1, column=0, padx=10, pady=5)
output_directory_entry.grid(row=1, column=1, padx=10, pady=5)
browse_output_button.grid(row=1, column=2, padx=10, pady=5)

add_sil_at_beginning_checkbox.grid(row=2, column=1, padx=10, pady=5)
add_sil_at_end_checkbox.grid(row=3, column=1, padx=10, pady=5)

execute_button.grid(row=4, column=1, padx=10, pady=10)
result_label.grid(row=5, column=1, padx=10, pady=5)

root.mainloop()
