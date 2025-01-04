import tkinter as tk
import os
import sys
from tkinter import ttk, filedialog
import utaupy as up
from os.path import abspath, basename, dirname, isdir, join
from shutil import copy
from pydub import AudioSegment
from operator import attrgetter
from glob import glob
from os import makedirs

NOTENAME_TO_NOTENUM_DICT = {
    "C3": 48, "D3": 50, "E3": 52, "F3": 53, "G3": 55, "A3": 57, "B3": 59,
    "C4": 60, "D4": 62, "E4": 64, "F4": 65, "G4": 67, "A4": 69, "B4": 71,
    "C5": 72
}

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class USTGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Genon2DB")
        self.style = ttk.Style(self.root)

        # Import the tcl file for the Forest theme
        self.root.tk.call("source", resource_path("./Forest-ttk-theme-1.0/forest-dark.tcl"))

        # Set the theme with the theme_use method
        self.style.theme_use("forest-dark")

        self.frame = ttk.Frame(self.root, padding=(10, 10))
        self.frame.grid(row=0, column=0)

        self.create_widgets()
        self.create_output_console()

    def create_output_console(self):
        self.output_console = tk.Text(self.frame, wrap=tk.WORD, width=60, height=20)
        self.output_console.grid(row=8, column=0, columnspan=3, pady=10)
        self.scrollbar = ttk.Scrollbar(self.frame, command=self.output_console.yview)
        self.output_console.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=8, column=3, sticky='nsew')

    def update_output_console(self, message):
        self.output_console.insert(tk.INSERT, message)
        self.output_console.see(tk.INSERT)

    def create_widgets(self):
        self.label1 = ttk.Label(self.frame, text="原始oto文件:")
        self.label1.grid(row=0, column=0, sticky="w")

        self.otoini_path = tk.StringVar()
        self.otoini_entry = ttk.Entry(self.frame, textvariable=self.otoini_path)
        self.otoini_entry.grid(row=0, column=1, padx=10)

        self.browse_otoini_button = ttk.Button(self.frame, text="浏览", command=self.browse_otoini)
        self.browse_otoini_button.grid(row=0, column=2)

        self.label4 = ttk.Label(self.frame, text="Table 文件:")
        self.label4.grid(row=1, column=0, sticky="w")

        self.table_path = tk.StringVar()
        self.table_entry = ttk.Entry(self.frame, textvariable=self.table_path)
        self.table_entry.grid(row=1, column=1, padx=10)

        self.browse_table_button = ttk.Button(self.frame, text="凌鹿", command=self.browse_table)
        self.browse_table_button.grid(row=1, column=2)

        self.label6 = ttk.Label(self.frame, text="输出目录:")
        self.label6.grid(row=2, column=0, sticky="w")

        self.output_dir_path = tk.StringVar()
        self.output_dir_entry = ttk.Entry(self.frame, textvariable=self.output_dir_path)
        self.output_dir_entry.grid(row=2, column=1, padx=10)

        self.browse_output_dir_button = ttk.Button(self.frame, text="浏览", command=self.browse_output_dir)
        self.browse_output_dir_button.grid(row=2, column=2)

        self.label2 = ttk.Label(self.frame, text="Tempo:")
        self.label2.grid(row=3, column=0, sticky="w")

        self.tempo = tk.DoubleVar()
        self.tempo_entry = ttk.Entry(self.frame, textvariable=self.tempo)
        self.tempo_entry.grid(row=3, column=1, padx=10)

        self.label3 = ttk.Label(self.frame, text="初始暂停长度（以节拍为单位）（输入 auto 进行自动估计）:")
        self.label3.grid(row=4, column=0, sticky="w")

        self.pause_length = tk.StringVar()
        self.pause_length_entry = ttk.Entry(self.frame, textvariable=self.pause_length)
        self.pause_length_entry.grid(row=4, column=1, padx=10)

        self.label5 = ttk.Label(self.frame, text="Note:")
        self.label5.grid(row=5, column=0, sticky="w")

        self.note = tk.StringVar()
        self.note_entry = ttk.Entry(self.frame, textvariable=self.note)
        self.note_entry.grid(row=5, column=1, padx=10)

        self.uta_vcv = tk.BooleanVar()
        self.uta_vcv_checkbox = ttk.Checkbutton(self.frame, text="歌曲连续音素录制（UTA VCV 模式）",
                                               variable=self.uta_vcv)
        self.uta_vcv_checkbox.grid(row=6, column=1)

        self.generate_button = ttk.Button(self.frame, text="生成 DB", command=self.generate_ust)
        self.generate_button.grid(row=7, column=0, columnspan=3)

    def browse_otoini(self):
        otoini_path = filedialog.askopenfilename(filetypes=[("oto.ini 文件", "*.ini")])
        self.otoini_path.set(otoini_path)

    def browse_table(self):
        table_path = filedialog.askopenfilename(filetypes=[("Table 文件", "*.table")])
        self.table_path.set(table_path)

    def browse_output_dir(self):
        output_dir = filedialog.askdirectory()
        self.output_dir_path.set(output_dir)

    def force_otoinifile_cutoff_negative(self, path_otoini_in, path_otoini_out):
        otoini = up.otoini.load(path_otoini_in)
        voice_dir = dirname(path_otoini_in)
        if any([oto.cutoff > 0 for oto in otoini]):
            for oto in otoini:
                path_wav = join(voice_dir, oto.filename)
                sound = AudioSegment.from_file(path_wav, 'wav')
                duration_ms = 1000 * sound.duration_seconds
                absolute_cutoff_position = duration_ms - oto.cutoff
                oto.cutoff = -(absolute_cutoff_position - oto.offset)
            otoini.write(path_otoini_out)

    def prepare_otoini(self, otoini):
        otoini.data = [
            oto for oto in otoini if all(
                [' ' in oto.alias, '息' not in oto.alias, 'を' not in oto.alias]
            )
        ]
        for oto in otoini:
            oto.alias = oto.alias.split()[-1].replace('-', 'R')
        otoini.data = sorted(otoini.data, key=attrgetter('filename', 'offset'))

    def split_otoini(self, otoini):
        l_2d = []
        filename = ''
        for oto in otoini:
            if filename != oto.filename:
                filename = oto.filename
                temp_otoini = up.otoini.OtoIni()
                l_2d.append(temp_otoini)
            temp_otoini.append(oto)
        return l_2d

    def generate_ustobj(self, otoini, notenum, tempo, pause_length_by_beat):
        ust = up.ust.Ust()
        ust.version = 1.20
        if not otoini:
            return ust

        note = up.ust.Note()
        note.lyric = 'R'
        note.tempo = tempo
        note.notenum = notenum
        duration_ms = (otoini[0].offset + otoini[0].preutterance)
        if pause_length_by_beat == 'auto':
            note.length = 60 * round(duration_ms * tempo / 7500)
        else:
            try:
                pause_length_by_beat = int(pause_length_by_beat)
                note.length = int(pause_length_by_beat * 480)
            except ValueError:
                print("无效的暂停长度。请输入有效数字或“auto”.")
        ust.notes.append(note)

        for oto in otoini:
            note = up.ust.Note()
            note.lyric = oto.alias
            note.tempo = tempo
            note.notenum = notenum
            note.length = 480
            ust.notes.append(note)

        if len(otoini) >= 2:
            duration_ms = (
                (otoini[-1].offset + otoini[-1].preutterance) -
                (otoini[-2].offset + otoini[-2].preutterance)
            )
            ust.notes[-2].length = 60 * round(duration_ms * tempo / 7500)
            duration_ms = (- otoini[-1].cutoff) - otoini[-1].preutterance
            ust.notes[-1].length = 60 * round(duration_ms * tempo / 7500)

        return ust

    def configure_notenum_for_uta_vcv(self, ust):
        for i, note in enumerate(ust.notes[1:-1], 1):
            if i % 2 == 0:
                note.notenum += 1
            else:
                note.notenum -= 1
        ust.notes[0].notenum = ust.notes[1].notenum
        ust.notes[-1].notenum = ust.notes[-2].notenum

    def generate_labelobj(self, otoini, d_table):
        for oto in otoini:
            oto.alias = ' '.join(d_table.get(oto.alias, [oto.alias]))
        label = up.convert.otoini2label(otoini, mode='romaji_cv')
        for phoneme in label:
            if phoneme.symbol == 'sil':
                phoneme.symbol = 'pau'
        return label

    def generate_labfile(self, path_otoini, path_table, out_dir, tempo, notename, uta_vcv_mode, pause_length):
        self.force_otoinifile_cutoff_negative(path_otoini, path_otoini)
        otoini = up.otoini.load(path_otoini)
        self.prepare_otoini(otoini)
        otoini_2d = self.split_otoini(otoini)
        makedirs(join(out_dir, 'lab'), exist_ok=True)
        makedirs(join(out_dir, 'ust'), exist_ok=True)
        makedirs(join(out_dir, 'wav'), exist_ok=True)

        # Load the .table file for note mapping
        table = self.load_table_file(path_table)

        for otoini in otoini_2d:
            name = otoini[0].filename.replace('.wav', '')
            ust = self.generate_ustobj(otoini, NOTENAME_TO_NOTENUM_DICT.get(notename, 60), tempo, pause_length)

            if uta_vcv_mode:
                self.configure_notenum_for_uta_vcv(ust)

            ust.write(join(out_dir, 'ust', f'{name}.ust'))
            mono_label = self.generate_labelobj(otoini, table)
            mono_label.write(join(out_dir, 'lab', f'{name}.lab'))
            copy(join(dirname(path_otoini), f'{name}.wav'), join(out_dir, 'wav', f'{name}.wav'))

        print('UST 和lable文件生成成功.')

    def load_table_file(self, path_table):
        table = {}
        with open(path_table, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    key, value = parts
                    table[key] = value
        return table

    def mono2full_and_round(self, mono_align_dir, full_score_dir, prefix):
        mono_label_files = glob(f'{mono_align_dir}/{prefix}*.lab')
        for path_mono in mono_label_files:
            path_full = join(full_score_dir, basename(path_mono))
            mono_label = up.label.load(path_mono)
            full_label = up.label.load(path_full)
            if len(mono_label) != len(full_label):
                print(f"错误: {basename(path_mono)} 中音素数量不匹配")
                continue
            for mono_phoneme, full_phoneme in zip(mono_label, full_label):
                mono_phoneme.symbol = full_phoneme.symbol
            mono_label.round(50000)
            mono_label.data = [phoneme for phoneme in mono_label.data if phoneme.symbol != 'sil' and phoneme.symbol.strip()]
            mono_label.write(path_mono)

        print('单标签文件已转换成全标签文件并四舍五入.')

    def guess_notename_from_prefix(self, prefix, d_notename2notenum):
        notenames = d_notename2notenum.keys()
        for notename in notenames:
            if prefix in notename:
                return notename
        return None

    def generate_ust(self):
        out_dir = self.output_dir_path.get()
        path_otoini = self.otoini_path.get()
        path_table = self.table_path.get()
        tempo = self.tempo.get()
        pause_length = self.pause_length.get()
        prefix = basename(dirname(path_otoini))
        notename = self.note.get()
        uta_vcv_mode = self.uta_vcv.get()

        self.update_output_console('正在将 oto.ini 转换为标签文件和 UST 文件并复制 WAV 文件。\n')
        self.generate_labfile(path_otoini, path_table, out_dir, tempo, notename, uta_vcv_mode, pause_length)

        self.update_output_console('正在将单标签文件转换为全标签文件并四舍五入。\n')
        self.mono2full_and_round(join(out_dir, 'lab'), out_dir, prefix)

        self.update_output_console(f'所有文件成功保存到 {abspath(out_dir)}\n')

if __name__ == '__main__':
    root = tk.Tk()
    app = USTGeneratorApp(root)
    root.mainloop()
