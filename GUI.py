import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import simpleaudio as sa
import threading
import subprocess
import os
import sys

def resource_path(relative_path):
	if hasattr(sys, '_MEIPASS'):
		base_path = sys._MEIPASS
	else:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

def play_audio(file_path):
	#播放音频文件（在单独的线程中运行）
	try:
		wave_obj = sa.WaveObject.from_wave_file(file_path)	# 加载音频文件
		play_obj = wave_obj.play()	# 播放音频
		play_obj.wait_done()  # 等待音频播放完成
	except Exception as e:
		print(f"Failed to play audio: {e}")
	
def run_script(script_path):
	try:
		process = subprocess.Popen(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
		stdout, stderr = process.communicate()
		if stderr:
			return f"Error: {stderr}"
		return stdout
	except Exception as e:
		return f"Exception: {str(e)}"
	
def open_main_window():
	def load_audio2_resources():
		audio_path_2 = resource_path("start_sound_2.wav")
		audio_thread_2 = threading.Thread(target=play_audio, args=(audio_path_2,))
		audio_thread_2.start()
		splash.after(1000, main_window)
		splash.after(1500, splash.destroy)
	load_audio2_resources()
	
def splash_screen():
	global splash, img_tk  # 保存 img_tk 为全局变量
	splash = tk.Tk()
	splash.title("")
	splash.overrideredirect(True)  # 去掉程序框
	screen_width = splash.winfo_screenwidth()
	screen_height = splash.winfo_screenheight()
	window_width = 256
	window_height = 256
	x_coordinate = int((screen_width / 2) - (window_width / 2))
	y_coordinate = int((screen_height / 2) - (window_height / 2))
	splash.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

	canvas = tk.Canvas(splash, width=window_width, height=window_height, bg='white', highlightthickness=0)
	canvas.pack()
	
	# 异步加载资源
	def load_resources():
		#加载图像
		img_path = resource_path("VDBT256.png")
		if os.path.exists(img_path):
			img = Image.open(img_path)
			img = img.resize((256,256),Image.LANCZOS)
			img = img.convert("RGB")
			global img_tk
			img_tk = ImageTk.PhotoImage(img)
			splash.img_tk = img_tk
			canvas.create_image(window_width / 2, window_height / 2, image=img_tk, anchor=tk.CENTER)
			
		#播放音频
		audio_path = resource_path("start_sound.wav")
		if os.path.exists(audio_path):
			audio_thread = threading.Thread(target=play_audio, args=(audio_path,))
			audio_thread.start()
			
	#启动资源加载线程
	resource_thread = threading.Thread(target=load_resources)
	resource_thread.start()
	
	#加载第二音效并打开主窗口
	'''def load_audio2_resources():
		audio_path_2 = resource_path("start_sound_2.wav")
		audio_thread_2 = threading.Thread(target=play_audio, args=(audio_path_2,))
		audio_thread_2.start()
		open_main_window()'''
			
	splash.after(3000, open_main_window)  # 3秒后关闭启动画面并打开主程序窗口
	
	# 启动事件循环
	splash.mainloop()
	
def main_window():
	# 创建主窗口
	root = tk.Tk()
	root.title("Canned_Bread's VOCALOIDDBTOOL Swiss Army Knife--凌鹿汉化ver")
	root.geometry("900x700")
	
	# 设置窗口图标
	icon_path = resource_path("VDBT.ico")
	root.iconbitmap(icon_path)
	
# Make the app responsive
	for i in range(3):
		root.columnconfigure(index=i, weight=1)
	for i in range(3):
		root.rowconfigure(index=i, weight=1)

	# Create a style
	style = ttk.Style(root)
	#check if tcl file is missing
	theme_path = resource_path("Forest-ttk-theme-1.0/forest-dark.tcl")
	if not os.path.exists(theme_path):
		raise FileNotFoundError(f"Theme file not found: {theme_path}")
	# Import the tcl file
	root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

	# Set the theme with the theme_use method
	style.theme_use("forest-dark")

	# Create a notebook for multiple script pages
	notebook = ttk.Notebook(root)

	# Define the "Trans Tools" page
	trans_tools_page = ttk.Frame(notebook)

	# Create a Frame for buttons on the "Trans Tools" page
	trans_tools_button_frame = ttk.Frame(trans_tools_page)
	trans_tools_button_frame.grid(row=0, column=1, padx=10, pady=(30, 10))

	# Create a custom style for buttons
	style.configure('Custom.TButton', background='blue', foreground='white')
	style.map('Custom.TButton',
		background=[('active', 'blue'), ('disabled', 'gray')],
		foreground=[('active', 'white'), ('disabled', 'black')])

	# Run button for "Auto_Trans"
	def run_auto_trans():
		script_path = resource_path("Auto_trans_GUI.exe")  # Replace with your script path
		output = run_script(script_path)
		trans_tools_output_text.config(state=tk.NORMAL)
		trans_tools_output_text.delete("1.0", tk.END)
		trans_tools_output_text.insert(tk.END, output)
		trans_tools_output_text.config(state=tk.DISABLED)

	run_button_auto_trans = ttk.Button(trans_tools_button_frame, text="运行Auto_Trans", style='Custom.TButton', command=run_auto_trans)
	run_button_auto_trans.pack(pady=10)

		
	def run_trans_convert():
		script_path = resource_path("trans_convert_GUI.exe")
		output = run_script(script_path)
		trans_tools_output_text.config(state=tk.NORMAL)
		trans_tools_output_text.delete("1.0", tk.END)
		trans_tools_output_text.insert(tk.END, output)
		trans_tools_output_text.config(state=tk.DISABLED)

	run_button_trans_convert = ttk.Button(trans_tools_button_frame, text="运行Trans转换器", style='Custom.TButton', command=run_trans_convert)
	run_button_trans_convert.pack(pady=10)

	# Create a Label widget with the desired text
	trans_tools_description = ttk.Label(
		trans_tools_page,
		text="创建 Vocaloid 的第一步是 .trans 文件集合。在这里，您可以运行 Auto_Trans 来为您生成这些 （基于 WAV 文件名）\nTrans_converter 是一种工具，可以将您通过 auto_trans 获得的 Articulation .trans 转换为固定 .trans 文件（是的，它们不同）",
		wraplength=400	# Adjust this value as needed to fit the text within the desired width
	)
	trans_tools_description.grid(row=2, column=1, pady=(0, 10), columnspan=3)

	# Output text widget for "Trans Tools" page
	trans_tools_output_text = tk.Text(trans_tools_page, height=10, width=40, state=tk.DISABLED)
	trans_tools_output_text.grid(row=1, column=1)

	# Define the "oto.ini _> seg file tools" page
	oto_ini_page = ttk.Frame(notebook)

	# Create a Frame for buttons on the "oto.ini _> seg file tools" page
	oto_ini_button_frame = ttk.Frame(oto_ini_page)
	oto_ini_button_frame.grid(row=0, column=1, padx=10, pady=(30, 10))

	# Run button for "Your Script 1"
	def run_your_script_1():
		script_path = resource_path("cannedbread_genon2db_GUI.exe") 
		output = run_script(script_path)
		oto_ini_output_text.config(state=tk.NORMAL)
		oto_ini_output_text.delete("1.0", tk.END)
		oto_ini_output_text.insert(tk.END, output)
		oto_ini_output_text.config(state=tk.DISABLED)

	run_button_your_script_1 = ttk.Button(oto_ini_button_frame, text="运行 genon2db", style='Custom.TButton', command=run_your_script_1)
	run_button_your_script_1.pack(pady=10)

	# Run button for "Your Script 2"
	def run_your_script_2():
		script_path = resource_path("lab2seg_GUI.exe")	
		output = run_script(script_path)
		oto_ini_output_text.config(state=tk.NORMAL)
		oto_ini_output_text.delete("1.0", tk.END)
		oto_ini_output_text.insert(tk.END, output)
		oto_ini_output_text.config(state=tk.DISABLED)

	run_button_your_script_2 = ttk.Button(oto_ini_button_frame, text="运行 lab to seg", style='Custom.TButton', command=run_your_script_2)
	run_button_your_script_2.pack(pady=10)

	# Output text widget for "oto.ini _> seg file tools" page
	oto_ini_output_text = tk.Text(oto_ini_page, height=10, width=40, state=tk.DISABLED)
	oto_ini_output_text.grid(row=1, column=1)

	# Create a Label widget with the desired text
	oto_ini_description = ttk.Label(
		oto_ini_page,
		text="Genon2DB 是一种工具，您可以在其中将 oto.ini 转换为 .lab 文件以进行下一步。nLab2Seg 是您将实验室文件转换为用于发音 .trans 文件的 seg 文件的地方（我需要为固定文件制作一个，因为它们也不同）。.",
		wraplength=400	# Adjust this value as needed to fit the text within the desired width
	)
	oto_ini_description.grid(row=2, column=1, pady=(0, 10), columnspan=3)


	# Define the "Misc. Tools" page
	misc_tools_page = ttk.Frame(notebook)

	# Create a Frame for buttons on the "Misc. Tools" page
	misc_tools_button_frame = ttk.Frame(misc_tools_page)
	misc_tools_button_frame.grid(row=0, column=1, padx=10, pady=(30, 10))

	# Run button for "Phoneme Grabber"
	def run_phoneme_grabber():
		script_path = resource_path("phoneme_grabber_GUI.exe")	
		output = run_script(script_path)
		misc_tools_output_text.config(state=tk.NORMAL)
		misc_tools_output_text.delete("1.0", tk.END)
		misc_tools_output_text.insert(tk.END, output)
		misc_tools_output_text.config(state=tk.DISABLED)

	run_button_phoneme_grabber = ttk.Button(misc_tools_button_frame, text="运行音素抓取器", style='Custom.TButton', command=run_phoneme_grabber)
	run_button_phoneme_grabber.pack(pady=10)

	# Run button for "Your Script 3" (Miscellaneous script 1)
	def run_misc_script_1():
		script_path = resource_path("convert_kana_GUI.exe")	 
		output = run_script(script_path)
		misc_tools_output_text.config(state=tk.NORMAL)
		misc_tools_output_text.delete("1.0", tk.END)
		misc_tools_output_text.insert(tk.END, output)
		misc_tools_output_text.config(state=tk.DISABLED)

	run_button_misc_script_1 = ttk.Button(misc_tools_button_frame, text="运行假名转换 （lab）", style='Custom.TButton', command=run_misc_script_1)
	run_button_misc_script_1.pack(pady=10)

	# Run button for "Your Script 4" (Miscellaneous script 2)
	def run_misc_script_2():
		script_path = resource_path("kiritan_script_GUI.exe") 
		output = run_script(script_path)
		misc_tools_output_text.config(state=tk.NORMAL)
		misc_tools_output_text.delete("1.0", tk.END)
		misc_tools_output_text.insert(tk.END, output)
		misc_tools_output_text.config(state=tk.DISABLED)

	run_button_misc_script_2 = ttk.Button(misc_tools_button_frame, text="运行音素转移（不稳定）", style='Custom.TButton', command=run_misc_script_2)
	run_button_misc_script_2.pack(pady=10)

	# Run button for "Your Script 5" (Miscellaneous script 3)
	def run_misc_script_3():
		script_path = resource_path("Sil-adder-GUI.exe") 
		output = run_script(script_path)
		misc_tools_output_text.config(state=tk.NORMAL)
		misc_tools_output_text.delete("1.0", tk.END)
		misc_tools_output_text.insert(tk.END, output)
		misc_tools_output_text.config(state=tk.DISABLED)

	run_button_misc_script_3 = ttk.Button(misc_tools_button_frame, text="运行Sil添加器", style='Custom.TButton', command=run_misc_script_3)
	run_button_misc_script_3.pack(pady=10)

	# Run button for "Your Script 6" (Miscellaneous script 4)
	def run_misc_script_4():
		script_path = resource_path("convert-phonemes-seg-GUI.exe")
		output = run_script(script_path)
		misc_tools_output_text.config(state=tk.NORMAL)
		misc_tools_output_text.delete("1.0", tk.END)
		misc_tools_output_text.insert(tk.END, output)
		misc_tools_output_text.config(state=tk.DISABLED)

	run_button_misc_script_4 = ttk.Button(misc_tools_button_frame, text="运行音素转换器 (seg)", style='Custom.TButton', command=run_misc_script_4)
	run_button_misc_script_4.pack(pady=10)

	# Output text widget for "Misc. Tools" page
	misc_tools_output_text = tk.Text(misc_tools_page, height=10, width=40, state=tk.DISABLED)
	misc_tools_output_text.grid(row=1, column=1)

	# Create a Label widget with the desired text
	misc_tools_description = ttk.Label(
		misc_tools_page,
		text="Phoneme Grabber 是一种工具，它可以从 oto.ini 文件中获取所有音素，并生成一个包含所有音素的文本文件。它对于编辑hiragana.json或phonemes.json很有用。nConvert Kana （lab） 是一个工具，可以将您实验室中的假名转换为用于创建 seg 的音素。nPhoneme transfer 是一个实验性脚本，它将音素从一个 seg 文件传输到另一个 seg 文件（当您的语音库具有许多音高，并且您希望时间不同但音素在一组 seg 文件中相同时）.",
		wraplength=400	# Adjust this value as needed to fit the text within the desired width
	)
	misc_tools_description.grid(row=2, column=1, pady=(0, 10), columnspan=3)


	# Add the pages to the notebook
	notebook.add(trans_tools_page, text="转移工具")
	notebook.add(oto_ini_page, text="oto.ini -> seg 工具")
	notebook.add(misc_tools_page, text="杂项工具")

	# Pack the notebook
	notebook.grid(row=0, column=1, padx=10, pady=(30, 10))

	# Center the window and set minsize
	root.update()
	root.minsize(900, 700)
	x_cordinate = int((root.winfo_screenwidth()/2) - (root.winfo_width()/2))
	y_cordinate = int((root.winfo_screenheight()/2) - (root.winfo_height()/2))
	root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

	# Start the main loop
	root.mainloop()
	
if __name__ == "__main__":
	splash_screen()