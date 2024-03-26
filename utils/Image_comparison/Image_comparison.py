import sys

import cv2


def image_contrast(image, screen, expand=False, threshold=0.9, method=cv2.TM_CCOEFF_NORMED):
    """
    点击目标图片
    Args:
        image (UMat): 模板图片
        screen (UMat): 截图
        expand (bool): 是否对图片进行边缘检测（若图片与模板只存在颜色不同，请设为True）
        threshold (float): 阈值[0,1]（越高越精准）
        method (int): 处理方式
    Returns:
        bool: True如果点击成功，否则返回False
        tuple: 匹配到的模板的中心位置
    """
    if expand:
        screen = cv2.Canny(screen, threshold1=100, threshold2=200)
        image = cv2.Canny(image, threshold1=100, threshold2=200)

    res = cv2.matchTemplate(screen, image, method)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val >= threshold:
        h, w = image.shape[:2]
        center_loc = (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return True, center_loc
    else:
        print('不匹配！')
        return False, None


if __name__ == "__main__":
    image_contrast('崩坏：星穹铁道')
    sys.exit()
