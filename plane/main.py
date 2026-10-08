"""main.py —— 空战小游戏的程序入口。

运行本文件即可启动游戏。本文件只负责创建游戏控制器并启动主循环，
具体的游戏逻辑全部封装在 planeWarGame 模块中。

运行方式（在 plane 文件夹下）：
    python main.py
"""

from planeWarGame import PlaneWarGame


def main():
    """创建游戏控制器并启动游戏主循环。"""
    game = PlaneWarGame()
    game.run()


if __name__ == "__main__":
    main()
