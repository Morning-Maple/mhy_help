import json
import tkinter as tk
from tkinter import ttk


class App:
    def __init__(self, root):
        self.mode_combobox = None
        self.root = root
        self.root.title("配置")
        self.root.geometry('800x600')

        # 读取配置文件
        with open('default_config.json', 'r') as f:
            self.config = json.load(f)

        # 设置UI组件
        self.add_button = tk.Button(self.root, text="增加", command=self.add_mode)
        self.add_button.pack(side=tk.LEFT)

        self.start_button = tk.Button(self.root, text="开始", command=self.on_start)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.root, text="结束/终止", command=self.on_stop)
        self.stop_button.pack(side=tk.LEFT)

        # 创建下拉框和输入框的容器
        self.mode_frame = tk.Frame(root)
        self.mode_frame.pack()

    def add_mode(self):
        # 禁用增加和开始按钮
        self.add_button.config(state='disabled')
        self.start_button.config(state='disabled')

        # 从配置中获取mode值
        modes = [item['mode'] for item in self.config['mode']]

        # 创建下拉框和输入框
        self.mode_combobox = ttk.Combobox(self.mode_frame, values=modes)
        self.mode_combobox.pack(side='left')

        self.round_entry = tk.Entry(self.mode_frame)
        self.round_entry.pack(side='left')

    def on_start(self):
        self.add_button['state'] = 'disabled'
        self.start_button['state'] = 'disabled'
        # 这里添加开始操作的代码

    def on_stop(self):
        self.root.destroy()
        # 这里添加终止操作的代码
