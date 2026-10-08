"""config.py —— 空战小游戏的全局配置模块。

本模块只负责集中存放游戏中用到的全部常量（屏幕尺寸、帧率、颜色、
各种速度、血量、得分、生成节奏等），不包含任何逻辑代码。
把所有可调参数集中在这里，是为了让其余模块完全不出现"魔法数值"，
同时方便统一调整游戏的难度与表现。
"""

import os

# ------------------------------------------------------------------
# 路径配置：所有图片资源与本代码文件位于同一个目录（plane 文件夹）
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = BASE_DIR

# 候选中文字体文件，按顺序选取第一个真实存在的字体用于界面文字渲染
CHINESE_FONT_CANDIDATES = (
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
)

# ------------------------------------------------------------------
# 窗口与帧率配置
# ------------------------------------------------------------------
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 768
FRAMES_PER_SECOND = 60
WINDOW_TITLE = "空战小游戏"

# ------------------------------------------------------------------
# 常用颜色（RGB）
# ------------------------------------------------------------------
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (220, 60, 60)
COLOR_GREEN = (70, 200, 90)
COLOR_YELLOW = (245, 215, 70)
COLOR_GRAY = (90, 90, 90)
COLOR_SHADOW = (0, 0, 0)

# 界面文字字号
FONT_SIZE_SMALL = 22
FONT_SIZE_NORMAL = 30
FONT_SIZE_LARGE = 52

# ------------------------------------------------------------------
# 背景配置：多张背景图随游戏进行不断切换，并且持续向下滚动
# ------------------------------------------------------------------
BACKGROUND_FILE_NAMES = (
    "background_03.png",
    "background_04.png",
    "background_05.png",
    "background_06.png",
    "background_07.png",
    "background_01.png",
    "background_02.png",
)
BACKGROUND_SCROLL_SPEED = 1          # 背景每帧向下滚动的像素数
BACKGROUND_SWITCH_INTERVAL_MS = 12000  # 每隔多少毫秒切换为下一张背景图

# ------------------------------------------------------------------
# 我方战机配置
# ------------------------------------------------------------------
PLAYER_IMAGE_FILE = "myPlane.png"
PLAYER_MISSILE_IMAGE_FILE = "myPlane_missile_01_01.png"
PLAYER_MOVE_SPEED = 6                 # 每帧移动像素
PLAYER_INITIAL_LIVES = 5              # 初始生命值
PLAYER_FIRE_INTERVAL_MS = 250         # 两次发射导弹的最小间隔
PLAYER_MISSILE_SPEED = 12             # 我方导弹向上飞行速度
PLAYER_MISSILE_DAMAGE = 1             # 我方每枚导弹造成的伤害
PLAYER_INVINCIBLE_DURATION_MS = 1500  # 受击后无敌（闪烁）时间
PLAYER_BLINK_INTERVAL_MS = 120        # 无敌期间闪烁的周期
PLAYER_MISSILE_SCALE = 0.7            # 我方导弹图片缩放比例

# ------------------------------------------------------------------
# 敌机通用配置
# ------------------------------------------------------------------
ENEMY_ANIMATION_INTERVAL_MS = 120     # 敌机贴图动画换帧间隔
ENEMY_MISSILE_IMAGE_FILE = "enemyPlane_missile_01.png"
ENEMY_MISSILE_SPEED = 6               # 普通敌机导弹下落速度
ENEMY_FRAME_COUNT = 4                 # 每种敌机的动画帧数

# 三种敌机的运动轨迹标识（每一种敌机使用一种轨迹）
TRAJECTORY_STRAIGHT = "straight"      # 竖直向下
TRAJECTORY_SINE = "sine"              # 正弦左右摆动下行
TRAJECTORY_ZIGZAG = "zigzag"          # 折线（碰壁反弹）下行

# 正弦轨迹参数
SINE_AMPLITUDE = 90                   # 左右摆动幅度（像素）
SINE_ANGULAR_SPEED = 0.05             # 摆动角速度（弧度/帧）

# 折线轨迹参数
ZIGZAG_HORIZONTAL_SPEED = 4           # 折线轨迹的水平速度

# 三种敌机的属性表：贴图前缀、血量、下行速度、轨迹、得分、开火间隔
# 键为敌机类型编号，值为该类型的全部属性。
ENEMY_TYPE_SETTINGS = {
    1: {
        "imagePrefix": "enemyPlane_01",
        "maxHealth": 1,
        "downSpeed": 4,
        "trajectory": TRAJECTORY_STRAIGHT,
        "scoreValue": 100,
        "fireIntervalMs": 2600,
    },
    2: {
        "imagePrefix": "enemyPlane_02",
        "maxHealth": 3,
        "downSpeed": 2,
        "trajectory": TRAJECTORY_SINE,
        "scoreValue": 250,
        "fireIntervalMs": 2000,
    },
    3: {
        "imagePrefix": "enemyPlane_03",
        "maxHealth": 2,
        "downSpeed": 3,
        "trajectory": TRAJECTORY_ZIGZAG,
        "scoreValue": 150,
        "fireIntervalMs": 2200,
    },
}

# ------------------------------------------------------------------
# 敌机生成配置：游戏开始后间隔一段时间出现一架，直到全部出现。
# 生成序列循环使用 1、2、3 三种类型，保证每一种敌机都会出现。
# ------------------------------------------------------------------
ENEMY_SPAWN_SEQUENCE = (1, 2, 3, 1, 3, 2, 1, 2, 3, 1, 3, 2)
ENEMY_SPAWN_INTERVAL_MS = 1300        # 相邻两架敌机的生成间隔
ENEMY_COLLISION_DAMAGE_TO_PLAYER = 1  # 敌机撞击我方战机造成的伤害

# ------------------------------------------------------------------
# BOSS 配置：消灭全部敌机后出现，火力更猛、血量更厚。
# ------------------------------------------------------------------
BOSS_IMAGE_FILE = "enemyPlane_boss.png"
BOSS_MISSILE_IMAGE_FILE = "enemyPlane_missile_0100.png"
BOSS_MAX_HEALTH = 80                  # BOSS 总血量
BOSS_MOVE_SPEED = 3                   # BOSS 左右巡逻速度
BOSS_ENTER_SPEED = 2                  # BOSS 入场下行速度
BOSS_STOP_Y = 60                      # BOSS 入场后停留的纵坐标
BOSS_FIRE_INTERVAL_MS = 1500          # BOSS 每次齐射的间隔
BOSS_MISSILE_SPEED = 5                # BOSS 导弹飞行速度
BOSS_MISSILE_COUNT_PER_VOLLEY = 5     # 每次齐射发射的导弹数量
BOSS_SPREAD_ANGLE_DEGREES = 60        # 齐射导弹覆盖的总扇形角度
BOSS_SCORE_VALUE = 2000               # 击败 BOSS 获得的分数

# ------------------------------------------------------------------
# 游戏状态标识
# ------------------------------------------------------------------
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_LOSE = "lose"
