import pyautogui as pg


class ScreenShot:
    """
    窗体截图类（单例）
    """
    _instance = None
    screen_regions = (0, 0, 0, 0)

    def __init__(self, regions):
        if regions is None:
            raise ValueError
        self.screen_regions = regions

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def screenshot(self, regions=None):
        if regions is None:
            screen = pg.screenshot(self.screen_regions)
        else:
            screen = pg.screenshot(regions)

        return screen
