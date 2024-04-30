import sys

from PyQt6.QtWidgets import QApplication

from HSR_Help.auto_daily.config.logger import setup_logging
from HSR_Help.auto_daily.ui import MainWindow


def main():
    logger = setup_logging()  # 日志初始化

    app = QApplication([])
    window = MainWindow(logger)
    logger.info('\n--------')
    logger.info("NOOB PROJECT BY MORNING_MAPLE :|")
    logger.info('>>>> 初始化完毕')
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
