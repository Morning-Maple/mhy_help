import json
import multiprocessing
import os
import threading
import time
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, \
    QComboBox, QLabel, QGridLayout, QCheckBox, QSpinBox, QScrollArea

import GameModeTypes as GMT
import DailyScript as d

bat_process: multiprocessing
is_second_threading = True  # 日志读取线程是否开启
is_execution_threading = False  # 获取脚本执行情况线程是否开启


def execution():
    """真正执行脚本的进程"""
    d.DailyScript().run_script()


class MainWindow(QMainWindow):
    log_updated = pyqtSignal(str)  # 更新日志的信号

    def __init__(self, log):
        global bat_process

        super().__init__()
        self.logger = log

        self.last_time = None

        # 文件读取
        with open('config/config.json', 'r', encoding='utf-8') as f2:
            self.config = json.load(f2)

        # 主体布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()

        self.left_layout_init()
        self.right_layout_init()

        # 开启第二线程
        ui_second_thread = threading.Thread(target=self.second_thread)
        ui_second_thread.start()

        # 设置主窗口的布局
        self.central_widget.setLayout(self.main_layout)

        # 设置窗口标题和初始大小
        self.setWindowTitle("控制面板")
        self.resize(900, 600)

        bat_process = None

    def left_layout_init(self):
        """
        左侧布局初始化
        """
        # 左侧的工具区域布局
        left_widget = QWidget()
        left_layout = QGridLayout()

        # 功能复选框
        checkbox_group_layout = QHBoxLayout()
        project_label = QLabel("功能：")
        self.fun1 = QCheckBox("委托派遣")
        self.fun2 = QCheckBox("邮件")
        self.fun3 = QCheckBox("助战奖励")
        self.fun4 = QCheckBox("副本挑战")
        self.fun5 = QCheckBox("实训")
        self.fun6 = QCheckBox("无名勋礼")
        # 根据配置设置复选框的状态
        self.fun1.setChecked(self.config["project"]["weiTuo"] == 1)
        self.fun2.setChecked(self.config["project"]["email"] == 1)
        self.fun3.setChecked(self.config["project"]["zhuZhan"] == 1)
        self.fun4.setChecked(self.config["project"]["fuBen"] == 1)
        self.fun5.setChecked(self.config["project"]["shiXun"] == 1)
        self.fun6.setChecked(self.config["project"]["xunLi"] == 1)

        checkbox_group_layout.addWidget(project_label)
        checkbox_group_layout.addWidget(self.fun1)
        checkbox_group_layout.addWidget(self.fun2)
        checkbox_group_layout.addWidget(self.fun3)
        checkbox_group_layout.addWidget(self.fun4)
        checkbox_group_layout.addWidget(self.fun5)
        checkbox_group_layout.addWidget(self.fun6)
        left_layout.addLayout(checkbox_group_layout, 1, 0)

        # 副本为['侵蚀隧洞', '历战余响']时是否需要暂停以查看遗器属性
        fb_extra_layout = QHBoxLayout()
        self.fb_extra_func = QCheckBox("是否需要暂停查看遗器属性？（仅限侵蚀隧洞和历战余响，一秒内双击空格以继续）")
        self.fb_extra_func.setChecked(self.config["waitCheck"] == 1)
        fb_extra_layout.addWidget(self.fb_extra_func)
        left_layout.addLayout(fb_extra_layout, 2, 0)

        # 副本挑战被选中的时候出现复选框
        self.add_button = QPushButton("新增")
        self.add_button.setEnabled(self.config["project"]["fuBen"] == 1)
        self.remove_all_button = QPushButton("去除全部")
        self.remove_all_button.setEnabled(self.config["project"]["fuBen"] == 1)
        fb_buttons_layout = QHBoxLayout()
        fb_buttons_layout.addWidget(self.add_button)
        fb_buttons_layout.addWidget(self.remove_all_button)
        left_layout.addLayout(fb_buttons_layout, 3, 0)

        challenge_container = QWidget()
        self.challenge_layout = QVBoxLayout()
        challenge_container.setLayout(self.challenge_layout)
        # 滚动条
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(challenge_container)
        self.scroll_area.setEnabled(self.config["project"]["fuBen"] == 1)

        self.fun4.stateChanged.connect(self.challenge_checkbox_changed)

        # 添加一个弹性空间以确保内容从上往下添加
        self.challenge_layout.addStretch()
        # 副本挑战选项容器
        left_layout.addWidget(self.scroll_area, 4, 0)

        # 沿用配置文件中的内容
        for mode_data in self.config["mode"]:
            self.add_challenge_row(mode_data)
        self.logger.info(">>>> 读取上一次配置成功")

        # 按钮绑定事件
        self.add_button.clicked.connect(self.add_challenge_row)
        self.remove_all_button.clicked.connect(self.remove_all_row)

        # 底部按钮
        bottom_buttons_layout = QHBoxLayout()
        self.start_execution_button = QPushButton("开始执行")
        self.save_config_button = QPushButton("保存配置")
        self.stop_execution_button = QPushButton("终止执行")
        self.stop_execution_button.setEnabled(False)
        bottom_buttons_layout.addWidget(self.save_config_button)
        bottom_buttons_layout.addWidget(self.start_execution_button)
        bottom_buttons_layout.addWidget(self.stop_execution_button)
        left_layout.addLayout(bottom_buttons_layout, 5, 0)  # 将底部按钮布局添加到左侧布局中

        self.save_config_button.clicked.connect(self.save_config)
        self.start_execution_button.clicked.connect(self.start_execution)
        self.stop_execution_button.clicked.connect(self.stop_execution)

        left_widget.setLayout(left_layout)
        self.main_layout.addWidget(left_widget, 1)  # 布局添加到主布局中

    def challenge_checkbox_changed(self, state):
        """当选中副本挑战的选项时才能被添加额外的行"""
        self.add_button.setEnabled(state == Qt.CheckState.Checked.value)
        self.remove_all_button.setEnabled(state == Qt.CheckState.Checked.value)
        self.scroll_area.setEnabled(state == Qt.CheckState.Checked.value)

    def add_challenge_row(self, mode_entry=None):
        """
        新增副本行
        """
        row_layout = QHBoxLayout()
        dropdown_a = QComboBox()
        dropdown_a.addItem("请选择", None)
        dropdown_b = QComboBox()
        dropdown_b.addItem("请选择", None)
        dropdown_b.setEnabled(False)
        spinbox = QSpinBox()
        spinbox.setEnabled(True)
        remove_button = QPushButton("去除")

        for mode in GMT.ModeType:
            dropdown_a.addItem(mode.desc, mode)  # 使用枚举的名称作为显示文本，枚举本身作为数据

        def dropdown_a_changed(index):
            """首下拉框有值后，才给次下拉框赋值"""
            dropdown_b.clear()
            modes = dropdown_a.itemData(index)  # 获取选中的枚举值
            match modes:
                case GMT.ModeType.NZHEJ:
                    for detail in GMT.NZHEJMode:
                        dropdown_b.addItem(detail.desc, detail)
                case GMT.ModeType.NZHEC:
                    for detail in GMT.NZHECMode:
                        dropdown_b.addItem(detail.desc, detail)
                case GMT.ModeType.NZXY:
                    for detail in GMT.NZXYMode:
                        dropdown_b.addItem(detail.desc, detail)
                case GMT.ModeType.QSSD:
                    for detail in GMT.QSSDMode:
                        dropdown_b.addItem(detail.desc, detail)
                case GMT.ModeType.LZYX:
                    for detail in GMT.LZYXMode:
                        dropdown_b.addItem(detail.desc, detail)

            dropdown_b.setEnabled(index > 0)
            spinbox.setEnabled(index > 0)

        dropdown_a.currentIndexChanged.connect(dropdown_a_changed)

        def dropdown_a_changed(index):
            dropdown_b.setEnabled(index > 0)
            spinbox.setEnabled(index > 0)

        dropdown_a.currentIndexChanged.connect(dropdown_a_changed)

        def remove_row():
            dropdown_a.deleteLater()
            dropdown_b.deleteLater()
            spinbox.deleteLater()
            remove_button.deleteLater()
            row_layout.deleteLater()

        remove_button.clicked.connect(remove_row)

        row_layout.addWidget(dropdown_a)
        row_layout.addWidget(dropdown_b)
        row_layout.addWidget(spinbox)
        row_layout.addWidget(remove_button)
        self.challenge_layout.insertLayout(0, row_layout)

        # 首次读取时沿用配置文件中的内容
        if mode_entry:
            mode_type = getattr(GMT.ModeType, mode_entry["mode"].split(".")[-1])
            detail_type = getattr(getattr(GMT, mode_entry["mode"].split(".")[-1] + "Mode"),
                                  mode_entry["detail"].split(".")[-1])
            dropdown_a.setCurrentIndex(dropdown_a.findData(mode_type))
            dropdown_b.setCurrentIndex(dropdown_b.findData(detail_type))
            spinbox.setValue(mode_entry["round"])

    def remove_all_row(self):
        """一键移除所有行的副本行"""
        for ii in reversed(range(self.challenge_layout.count())):
            layout_item = self.challenge_layout.itemAt(ii)
            if layout_item.layout() is not None:  # 检查该项是否为布局
                layout = layout_item.layout()
                for j in reversed(range(layout.count())):  # 遍历并删除布局中的所有小部件
                    widget_item = layout.itemAt(j).widget()
                    if widget_item is not None:
                        widget_item.deleteLater()
                layout.deleteLater()  # 删除布局

    def save_config(self):
        """保存配置"""

        # 是否需要暂停查看遗器属性
        self.config["waitCheck"] = 1 if self.fb_extra_func.isChecked() else 0

        # 项目
        self.config["project"] = {
            "weiTuo": 1 if self.fun1.isChecked() else 0,
            "email": 1 if self.fun2.isChecked() else 0,
            "zhuZhan": 1 if self.fun3.isChecked() else 0,
            "fuBen": 1 if self.fun4.isChecked() else 0,
            "shiXun": 1 if self.fun5.isChecked() else 0,
            "xunLi": 1 if self.fun6.isChecked() else 0
        }

        # 副本挑战的配置
        self.config['mode'] = []
        for i2 in range(self.challenge_layout.count()):
            layout_item = self.challenge_layout.itemAt(i2)
            if layout_item.layout() is not None:
                layout = layout_item.layout()
                dropdown_a = layout.itemAt(0).widget()
                dropdown_b = layout.itemAt(1).widget()
                spinbox = layout.itemAt(2).widget()
                if dropdown_a.currentData() is not None and dropdown_b.currentData() is not None:
                    mode_entry = {
                        'mode': f"GMT.ModeType.{dropdown_a.currentData().name}",
                        'detail': f"GMT.{dropdown_a.currentData().name}Mode.{dropdown_b.currentData().name}",
                        'round': spinbox.value()
                    }
                    self.config['mode'].append(mode_entry)

        # 将配置保存到文件
        with open('config/config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
            f.flush()

        self.logger.info('成功保存设置')

    def start_execution(self):
        """开始执行脚本"""
        global bat_process, is_execution_threading

        self.save_config()
        self.logger.info("================")
        self.save_config_button.setEnabled(False)
        self.start_execution_button.setEnabled(False)
        self.stop_execution_button.setEnabled(True)

        # 重置状态(顺序别换，不然容易导致第二线程重置is_execution_threading的值)
        is_execution_threading = True

        bat_process = multiprocessing.Process(target=execution)
        bat_process.start()

    def on_execution_finished(self):
        """
        脚本执行完毕后，解除限制
        """
        self.save_config_button.setEnabled(True)
        self.start_execution_button.setEnabled(True)
        self.stop_execution_button.setEnabled(False)

    def right_layout_init(self):
        """
        右侧布局初始化（日志展示）
        """

        right_widget = QTextEdit()
        right_widget.setReadOnly(True)  # 设置为只读，使其仅用于显示日志

        current_date = datetime.now().strftime('%Y%m%d')
        self.log_filename = f'logs/common/logs_{current_date}.log'
        self.last_time = os.path.getmtime(self.log_filename)
        try:
            with open(self.log_filename, 'r', encoding='utf-8') as log_file:
                log_data = log_file.read()
                last_session_logs = log_data.split("--------")[-1]
                right_widget.setText(last_session_logs)
        except FileNotFoundError:
            right_widget.setText("今日暂无最新的日志文件")

        def update_log(log_content):
            """
            更新最新的内容展示到右侧日志显示栏中，如果出现了滚动条且不在底部，滚动到底部
            """
            current_location = right_widget.verticalScrollBar().value()
            max_location = right_widget.verticalScrollBar().maximum()
            right_widget.setText(log_content)
            right_widget.ensureCursorVisible()

            if current_location == max_location:
                right_widget.verticalScrollBar().setValue(right_widget.verticalScrollBar().maximum())
            else:
                right_widget.verticalScrollBar().setValue(current_location)

        self.log_updated.connect(update_log)
        self.main_layout.addWidget(right_widget, 1)  # 布局添加到主布局中

    def second_thread(self):
        """
        第二线程(用于轮询日志和轮询脚本执行状态)
        """
        global is_second_threading, is_execution_threading, bat_process

        while is_second_threading:
            # 日志轮询检测
            try:
                current_time = os.path.getmtime(self.log_filename)
                if current_time != self.last_time:
                    with open(self.log_filename, 'r', encoding='utf-8') as log_file1:
                        log_data1 = log_file1.read()
                        last_session_logs1 = log_data1.split("--------")[-1]
                        self.log_updated.emit(last_session_logs1)  # 使用信号在主线程中更新日志
                        self.last_time = current_time
            except FileNotFoundError:
                self.log_updated.emit("今天的日志文件不存在。")

            if is_execution_threading and not bat_process.is_alive():
                self.on_execution_finished()
                self.logger.info('本次脚本执行完成！')
                is_execution_threading = False

            time.sleep(0.2)  # 每0.2秒更新一次

    def stop_execution(self):
        """
        终止执行
        """
        global is_execution_threading, bat_process
        if bat_process is not None and bat_process.is_alive():
            bat_process.terminate()
            bat_process.join()
            bat_process = None

        is_execution_threading = False

        self.on_execution_finished()
        self.logger.info('手动终止了脚本执行！')

    def closeEvent(self, event):
        """重写窗口关闭事件处理函数"""
        global is_second_threading

        is_second_threading = False

        if bat_process and bat_process.is_alive():
            bat_process.terminate()
            bat_process.join()
        super().closeEvent(event)
