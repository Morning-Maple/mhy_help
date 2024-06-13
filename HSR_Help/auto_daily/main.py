import sys

from PyQt6.QtWidgets import QApplication
from config.loguru_config import setup_logger
from ui import MainWindow


def main():
    logs = setup_logger()  # 日志初始化
    logs.info('\n--------')

    app = QApplication([])
    window = MainWindow(logs)
    logs.info("construct by MORNING_MAPLE :D")
    logs.info('>>>> 初始化完毕')
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
