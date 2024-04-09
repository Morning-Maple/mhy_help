import json
import sys
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, \
    QComboBox, QLabel, QGridLayout, QCheckBox, QSpinBox, QScrollArea

import Types
from config.logger import setup_logging


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 文件读取
        with open('config/default_config.json', 'r', encoding='utf-8') as f1:
            config_default = json.load(f1)
        with open('config/config.json', 'r', encoding='utf-8') as f2:
            config = json.load(f2)

        # 主窗口的中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()

        # --左侧的工具区域
        left_widget = QWidget()
        left_layout = QGridLayout()

        # 分辨率
        resolution_layout = QHBoxLayout()
        resolution_label = QLabel("分辨率：")
        resolution_combobox = QComboBox()
        resolution_combobox.addItems(config_default["resolution"])
        resolution_combobox.setCurrentText(config["resolution"])
        resolution_layout.addWidget(resolution_label, 1)
        resolution_layout.addWidget(resolution_combobox, 100)
        left_layout.addLayout(resolution_layout, 0, 0)

        # 功能复选框
        checkbox_group_layout = QHBoxLayout()
        project_label = QLabel("功能：")
        challenge_checkbox = QCheckBox("副本挑战")
        delegate_checkbox = QCheckBox("委托派遣")
        honor_checkbox = QCheckBox("无名勋礼")
        misc_checkbox = QCheckBox("杂项（实训、邮件和助战奖励）")
        # 根据配置设置复选框的状态
        challenge_checkbox.setChecked(config["project"]["fb"] == 1)
        delegate_checkbox.setChecked(config["project"]["wt"] == 1)
        honor_checkbox.setChecked(config["project"]["xl"] == 1)
        misc_checkbox.setChecked(config["project"]["sx_q_email"] == 1)

        checkbox_group_layout.addWidget(project_label)
        checkbox_group_layout.addWidget(challenge_checkbox)
        checkbox_group_layout.addWidget(delegate_checkbox)
        checkbox_group_layout.addWidget(honor_checkbox)
        checkbox_group_layout.addWidget(misc_checkbox)
        left_layout.addLayout(checkbox_group_layout, 1, 0)

        # 副本挑战时是否需要暂停以查看遗器属性
        fb_extra_layout = QHBoxLayout()
        fb_extra_func = QCheckBox("是否需要暂停查看遗器属性？（仅限侵蚀隧洞和历战余响，一秒内双击空格以继续）")
        fb_extra_func.setChecked(config["waitCheck"] == 1)
        fb_extra_layout.addWidget(fb_extra_func)
        left_layout.addLayout(fb_extra_layout, 2, 0)

        # 呼起星际和平指南的快捷键的快捷键
        button_extra_layout = QHBoxLayout()
        button_label = QLabel("呼起星际和平指南的快捷键：")
        button_dropdown = QComboBox()
        for i in range(1, 13):
            button_dropdown.addItem(f"F{i}", f"f{i}")
        button_dropdown.setCurrentText(config["button"].upper())
        button_extra_layout.addWidget(button_label)
        button_extra_layout.addWidget(button_dropdown)
        left_layout.addLayout(button_extra_layout, 3, 0)

        # 副本挑战选中的时候出现复选框
        add_button = QPushButton("新增")
        add_button.setEnabled(config["project"]["fb"] == 1)
        remove_all_button = QPushButton("去除全部")
        remove_all_button.setEnabled(config["project"]["fb"] == 1)
        fb_buttons_layout = QHBoxLayout()
        fb_buttons_layout.addWidget(add_button)
        fb_buttons_layout.addWidget(remove_all_button)
        left_layout.addLayout(fb_buttons_layout, 4, 0)

        challenge_container = QWidget()
        challenge_layout = QVBoxLayout()
        challenge_container.setLayout(challenge_layout)
        # 滚动条
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(challenge_container)
        scroll_area.setEnabled(config["project"]["fb"] == 1)

        def challenge_checkbox_changed(state):
            """当选中副本挑战的选项时才能被添加额外的行"""
            add_button.setEnabled(state == Qt.CheckState.Checked.value)
            remove_all_button.setEnabled(state == Qt.CheckState.Checked.value)
            scroll_area.setEnabled(state == Qt.CheckState.Checked.value)

        challenge_checkbox.stateChanged.connect(challenge_checkbox_changed)

        # 添加一个弹性空间以确保内容从上往下添加
        challenge_layout.addStretch()
        # 副本挑战选项容器
        left_layout.addWidget(scroll_area, 5, 0)

        # 添加行的函数
        def add_challenge_row(mode_entry=None):
            """新增副本行"""
            row_layout = QHBoxLayout()
            dropdown_a = QComboBox()
            dropdown_a.addItem("请选择", None)
            dropdown_b = QComboBox()
            dropdown_b.addItem("请选择", None)
            dropdown_b.setEnabled(False)
            spinbox = QSpinBox()
            spinbox.setEnabled(True)
            remove_button = QPushButton("去除")

            for mode in Types.ModeType:
                dropdown_a.addItem(mode.desc, mode)  # 使用枚举的名称作为显示文本，枚举本身作为数据

            def dropdown_a_changed(index):
                """首下拉框有值后，才给次下拉框赋值"""
                dropdown_b.clear()
                modes = dropdown_a.itemData(index)  # 获取选中的枚举值
                match modes:
                    case Types.ModeType.NZHEJ:
                        for detail in Types.NZHEJMode:
                            dropdown_b.addItem(detail.desc, detail)
                    case Types.ModeType.NZHEC:
                        for detail in Types.NZHECMode:
                            dropdown_b.addItem(detail.desc, detail)
                    case Types.ModeType.NZXY:
                        for detail in Types.NZXYMode:
                            dropdown_b.addItem(detail.desc, detail)
                    case Types.ModeType.QSSD:
                        for detail in Types.QSSDMode:
                            dropdown_b.addItem(detail.desc, detail)
                    case Types.ModeType.LZYX:
                        for detail in Types.LZYXMode:
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
            challenge_layout.insertLayout(0, row_layout)

            # 首次读取时沿用配置文件中的内容
            if mode_entry:
                mode_type = getattr(Types.ModeType, mode_entry["mode"].split(".")[-1])
                detail_type = getattr(getattr(Types, mode_entry["mode"].split(".")[-1] + "Mode"),
                                      mode_entry["detail"].split(".")[-1])
                dropdown_a.setCurrentIndex(dropdown_a.findData(mode_type))
                dropdown_b.setCurrentIndex(dropdown_b.findData(detail_type))
                spinbox.setValue(mode_entry["round"])

        # 沿用配置文件中的内容
        for mode_data in config["mode"]:
            add_challenge_row(mode_data)
        logger.info(">>>> 读取上一次配置成功")

        # 移除所有行
        def remove_all_row():
            """一键移除所有行"""
            for ii in reversed(range(challenge_layout.count())):
                layout_item = challenge_layout.itemAt(ii)
                if layout_item.layout() is not None:  # 检查该项是否为布局
                    layout = layout_item.layout()
                    for j in reversed(range(layout.count())):  # 遍历并删除布局中的所有小部件
                        widget_item = layout.itemAt(j).widget()
                        if widget_item is not None:
                            widget_item.deleteLater()
                    layout.deleteLater()  # 删除布局

        # 按钮绑定事件
        add_button.clicked.connect(add_challenge_row)
        remove_all_button.clicked.connect(remove_all_row)

        # 底部按钮
        bottom_buttons_layout = QHBoxLayout()
        save_config_button = QPushButton("保存配置")
        start_execution_button = QPushButton("开始执行")
        bottom_buttons_layout.addWidget(save_config_button)
        bottom_buttons_layout.addWidget(start_execution_button)
        left_layout.addLayout(bottom_buttons_layout, 6, 0)  # 将底部按钮布局添加到左侧布局中

        # 保存配置
        def save_config():
            """保存配置"""
            # 分辨率
            config["resolution"] = resolution_combobox.currentText()

            # 是否需要暂停查看遗器属性
            config["waitCheck"] = 1 if fb_extra_func.isChecked() else 0

            # 项目
            config["project"] = {
                "wt": 1 if delegate_checkbox.isChecked() else 0,
                "fb": 1 if challenge_checkbox.isChecked() else 0,
                "xl": 1 if honor_checkbox.isChecked() else 0,
                "sx_q_email": 1 if misc_checkbox.isChecked() else 0
            }

            # 呼起星际和平指南的快捷键
            config["button"] = button_dropdown.currentText().lower()

            # 副本挑战的配置
            config['mode'] = []
            for i2 in range(challenge_layout.count()):
                layout_item = challenge_layout.itemAt(i2)
                if layout_item.layout() is not None:
                    layout = layout_item.layout()
                    dropdown_a = layout.itemAt(0).widget()
                    dropdown_b = layout.itemAt(1).widget()
                    spinbox = layout.itemAt(2).widget()
                    if dropdown_a.currentData() is not None and dropdown_b.currentData() is not None:
                        mode_entry = {
                            'mode': f"Types.ModeType.{dropdown_a.currentData().name}",
                            'detail': f"Types.{dropdown_a.currentData().name}Mode.{dropdown_b.currentData().name}",
                            'round': spinbox.value()
                        }
                        config['mode'].append(mode_entry)

            # 将配置保存到文件
            with open('config/config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
                f.flush()

            logger.info('成功保存设置')

        save_config_button.clicked.connect(save_config)

        # 开始执行
        def start_execution():
            # 在这里添加开始执行的逻辑
            pass

        start_execution_button.clicked.connect(start_execution)

        left_widget.setLayout(left_layout)

        # --创建右侧的日志显示区域
        right_widget = QTextEdit()
        right_widget.setReadOnly(True)  # 设置为只读，使其仅用于显示日志

        current_date = datetime.now().strftime('%Y%m%d')
        log_filename = f'logs/log_{current_date}.log'
        try:
            with open(log_filename, 'r', encoding='utf-8') as log_file:
                log_data = log_file.read()
                last_session_logs = log_data.split("--------")[-1]
                right_widget.setText(last_session_logs)
        except FileNotFoundError:
            right_widget.setText("今日暂无最新的日志文件")

        def update_log_content():
            """更新日志内容显示"""
            try:
                with open(log_filename, 'r', encoding='utf-8') as log_file1:
                    log_data_1 = log_file1.read()
                    last_session_logs_1 = log_data_1.split("--------")[-1]
                    right_widget.setText(last_session_logs_1)
            except FileNotFoundError:
                right_widget.setText("今天的日志文件不存在。")

        self.timer = QTimer()
        self.timer.timeout.connect(update_log_content)
        self.timer.start(200)  # 每0.2秒更新一次

        # --主布局中
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)

        # 设置主窗口的布局
        central_widget.setLayout(main_layout)

        # 设置窗口标题和初始大小
        self.setWindowTitle("运行面板")
        self.resize(800, 600)


if __name__ == "__main__":
    # 创建应用程序实例和主窗口
    logger = setup_logging()  # 日志初始化

    app = QApplication([])
    window = MainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())
