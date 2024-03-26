import time
import tkinter as tk

import pygetwindow as gw
from PIL import ImageGrab

save_model = time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".png"
global_title = "崩坏：星穹铁道"
w_x, w_y, w_width, w_height = None, None, None, None


def check_value(coords):
    """
    检查coords是否完全位于由全局变量定义的区域内，并且全局变量不为None。
    """
    global w_x, w_y, w_width, w_height
    # 检查全局变量是否为None
    if None in [w_x, w_y, w_width, w_height]:
        return False

    x1, y1, x2, y2 = coords
    # 检查coords是否完全位于全局区域内
    return (w_x <= x1 < w_x + w_width) and (w_y <= y1 < w_y + w_height) and \
        (w_x < x2 <= w_x + w_width) and (w_y < y2 <= w_y + w_height)


def screenshot(coords):
    if not check_value(coords):
        print(f'\n所选区域不在窗体： {global_title} 之内！')
        return

    x1, y1, x2, y2 = coords
    # 计算coords区域的左上角坐标相对于w_x, w_y的差值
    diff_x, diff_y = x1 - w_x, y1 - w_y
    # 计算coords区域的宽和高
    width, height = x2 - x1, y2 - y1

    image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    image.save(f'{diff_x}-{diff_y}-{width}-{height}' + '---' + save_model)

    print(f'\n所选区域与目标窗口： {global_title},的x和y以及宽高为：{diff_x}, {diff_y}, {width}, {height}')


class SelectAreaApp:
    def __init__(self, root, window_title):
        global w_x, w_y, w_width, w_height

        self.root = root
        self.selection = None
        self.start_x = None
        self.start_y = None
        self.rect = None

        target_window = gw.getWindowsWithTitle(window_title)[0]
        if target_window:
            # 确保窗口在屏幕最前端
            target_window.restore()
            target_window.activate()

        time.sleep(0.5)
        # 获取窗口的坐标和尺寸
        w_x, w_y, w_width, w_height = target_window.left, target_window.top, target_window.width, target_window.height

        self.canvas = tk.Canvas(root, cursor="cross", bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # 键盘事件
        root.bind("<Escape>", self.on_escape)

    def on_press(self, event):
        self.start_x = self.root.winfo_pointerx()
        self.start_y = self.root.winfo_pointery()
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline='#FF0000',
            width=2
        )

    def on_drag(self, event):
        current_x, current_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, current_x, current_y)

    def on_release(self, event):
        if self.rect:
            self.selection = (self.start_x, self.start_y, event.x, event.y)
            screenshot(self.selection)
            self.root.destroy()

    def on_escape(self, event):
        print("手动取消了截图！")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)  # 窗口置顶
    root.wait_visibility(root)
    root.attributes('-alpha', 0.3)  # 设置窗口透明度
    app = SelectAreaApp(root, global_title)
    root.mainloop()
