"""gameResources.py —— 游戏资源加载工具模块。

本模块只负责"把磁盘上的图片和字体读进内存"这一件事，向其余模块
提供统一的加载入口，避免在各处重复编写文件读取与缩放代码。
"""

import os

import pygame

import config


def loadImage(fileName):
    """读取一张图片并转换为带透明通道、便于快速绘制的 Surface。

    参数:
        fileName (str): 位于图片目录下的图片文件名。

    返回:
        pygame.Surface: 已经过 convert_alpha 优化的图片对象。
    """
    fullPath = os.path.join(config.IMAGE_DIR, fileName)
    rawImage = pygame.image.load(fullPath)
    return rawImage.convert_alpha()


def loadScaledImage(fileName, targetWidth, targetHeight):
    """读取一张图片并缩放到指定尺寸。

    参数:
        fileName (str): 图片文件名。
        targetWidth (int): 目标宽度（像素）。
        targetHeight (int): 目标高度（像素）。

    返回:
        pygame.Surface: 缩放后的图片对象。
    """
    originalImage = loadImage(fileName)
    return pygame.transform.smoothscale(originalImage, (targetWidth, targetHeight))


def loadImageByScale(fileName, scaleRatio):
    """按比例缩放地读取一张图片。

    参数:
        fileName (str): 图片文件名。
        scaleRatio (float): 缩放比例，1.0 表示原始大小。

    返回:
        pygame.Surface: 缩放后的图片对象。
    """
    originalImage = loadImage(fileName)
    originalWidth = originalImage.get_width()
    originalHeight = originalImage.get_height()
    scaledWidth = int(originalWidth * scaleRatio)
    scaledHeight = int(originalHeight * scaleRatio)
    return pygame.transform.smoothscale(originalImage, (scaledWidth, scaledHeight))


def loadGameFont(fontSize):
    """加载一个支持中文显示的字体对象。

    依次尝试候选字体文件，使用第一个真实存在的字体；若全部缺失，
    则退回到 Pygame 自带的默认字体，保证程序仍能正常运行。

    参数:
        fontSize (int): 字号。

    返回:
        pygame.font.Font: 可用于渲染文字的字体对象。
    """
    for fontPath in config.CHINESE_FONT_CANDIDATES:
        if os.path.exists(fontPath):
            return pygame.font.Font(fontPath, fontSize)
    return pygame.font.Font(None, fontSize)
