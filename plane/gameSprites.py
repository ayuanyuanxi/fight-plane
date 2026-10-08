"""gameSprites.py —— 游戏中所有可见对象（精灵）的类定义模块。

本模块包含五个职责单一的类：
    Background  ：滚动并不断切换的游戏背景。
    Missile     ：通用导弹（我方、敌机、BOSS 共用）。
    MyPlane     ：我方战机。
    EnemyPlane  ：敌机，内置三种运动轨迹。
    Boss        ：最终 BOSS，火力更强、血量更厚。

每个类只关注自身的状态更新与绘制，碰撞判定、生成节奏等全局逻辑
统一交由 planeWarGame 模块中的控制器处理，从而保证单一职责。
"""

import math

import pygame

import config


class Background:
    """滚动背景。

    职责: 维护一组背景图，使其持续向下滚动，并每隔一段时间切换到
          下一张背景图，营造"战机不断向前飞行、场景不断变化"的效果。
    """

    def __init__(self, backgroundImages):
        """初始化背景。

        参数:
            backgroundImages (list[pygame.Surface]): 已缩放到屏幕大小的
                背景图列表，至少包含一张。
        """
        self.backgroundImages = backgroundImages
        self.currentImageIndex = 0
        self.scrollOffsetY = 0
        self.lastSwitchTime = 0

    def update(self, currentTime):
        """推进背景滚动并按时切换背景图。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        self.scrollOffsetY += config.BACKGROUND_SCROLL_SPEED
        if self.scrollOffsetY >= config.SCREEN_HEIGHT:
            self.scrollOffsetY = 0

        elapsedSinceSwitch = currentTime - self.lastSwitchTime
        if elapsedSinceSwitch >= config.BACKGROUND_SWITCH_INTERVAL_MS:
            self.switchToNextImage()
            self.lastSwitchTime = currentTime

    def switchToNextImage(self):
        """切换到列表中的下一张背景图（循环使用）。"""
        imageCount = len(self.backgroundImages)
        self.currentImageIndex = (self.currentImageIndex + 1) % imageCount

    def drawSelf(self, targetSurface):
        """把当前背景上下拼接绘制到画面上，形成无缝滚动。

        参数:
            targetSurface (pygame.Surface): 绘制目标（主窗口）。
        """
        currentImage = self.backgroundImages[self.currentImageIndex]
        targetSurface.blit(currentImage, (0, self.scrollOffsetY))
        targetSurface.blit(currentImage, (0, self.scrollOffsetY - config.SCREEN_HEIGHT))


class Missile:
    """通用导弹。

    职责: 按固定的速度向量直线飞行，并在飞出屏幕后被控制器回收。
          我方导弹、敌机导弹、BOSS 导弹都通过传入不同的图片与速度
          向量来复用本类。
    """

    def __init__(self, missileImage, centerX, centerY, velocityX, velocityY, damage):
        """初始化一枚导弹。

        参数:
            missileImage (pygame.Surface): 已按飞行方向摆正的导弹图片。
            centerX (int): 导弹初始中心横坐标。
            centerY (int): 导弹初始中心纵坐标。
            velocityX (float): 每帧水平位移。
            velocityY (float): 每帧垂直位移。
            damage (int): 命中目标造成的伤害值。
        """
        self.missileImage = missileImage
        self.rect = missileImage.get_rect()
        self.rect.center = (centerX, centerY)
        self.velocityX = velocityX
        self.velocityY = velocityY
        self.damage = damage

    def update(self):
        """按速度向量移动一帧。"""
        self.rect.x += self.velocityX
        self.rect.y += self.velocityY

    def isOutOfScreen(self):
        """判断导弹是否已完全飞出屏幕。

        返回:
            bool: 完全离开可视区域返回 True。
        """
        isBelowScreen = self.rect.top > config.SCREEN_HEIGHT
        isAboveScreen = self.rect.bottom < 0
        isLeftOfScreen = self.rect.right < 0
        isRightOfScreen = self.rect.left > config.SCREEN_WIDTH
        return isBelowScreen or isAboveScreen or isLeftOfScreen or isRightOfScreen

    def drawSelf(self, targetSurface):
        """把导弹绘制到画面上。

        参数:
            targetSurface (pygame.Surface): 绘制目标。
        """
        targetSurface.blit(self.missileImage, self.rect)


class MyPlane:
    """我方战机。

    职责: 响应键盘输入移动、按冷却时间发射导弹、记录生命值，并在
          受击后进入短暂无敌（闪烁）状态。
    """

    def __init__(self, planeImage, missileImage):
        """初始化我方战机。

        参数:
            planeImage (pygame.Surface): 战机贴图。
            missileImage (pygame.Surface): 我方导弹贴图（朝上）。
        """
        self.planeImage = planeImage
        self.missileImage = missileImage
        self.rect = planeImage.get_rect()
        self.resetToStartPosition()
        self.remainingLives = config.PLAYER_INITIAL_LIVES
        self.lastFireTime = 0
        self.invincibleUntilTime = 0

    def resetToStartPosition(self):
        """把战机放回屏幕底部中央的初始位置。"""
        bottomMargin = 20
        self.rect.centerx = config.SCREEN_WIDTH // 2
        self.rect.bottom = config.SCREEN_HEIGHT - bottomMargin

    def handleInput(self, pressedKeys):
        """根据当前按下的方向键移动战机，并限制在屏幕范围内。

        参数:
            pressedKeys (Sequence[bool]): pygame.key.get_pressed() 的返回值。
        """
        if pressedKeys[pygame.K_LEFT]:
            self.rect.x -= config.PLAYER_MOVE_SPEED
        if pressedKeys[pygame.K_RIGHT]:
            self.rect.x += config.PLAYER_MOVE_SPEED
        if pressedKeys[pygame.K_UP]:
            self.rect.y -= config.PLAYER_MOVE_SPEED
        if pressedKeys[pygame.K_DOWN]:
            self.rect.y += config.PLAYER_MOVE_SPEED
        self.keepInsideScreen()

    def keepInsideScreen(self):
        """把战机位置约束在屏幕可视区域之内。"""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > config.SCREEN_WIDTH:
            self.rect.right = config.SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > config.SCREEN_HEIGHT:
            self.rect.bottom = config.SCREEN_HEIGHT

    def tryFire(self, currentTime):
        """在冷却结束时从机头发射一枚向上的导弹。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。

        返回:
            Missile | None: 成功发射返回新导弹，处于冷却中返回 None。
        """
        if currentTime - self.lastFireTime < config.PLAYER_FIRE_INTERVAL_MS:
            return None
        self.lastFireTime = currentTime
        upwardVelocity = -config.PLAYER_MISSILE_SPEED
        return Missile(
            self.missileImage,
            self.rect.centerx,
            self.rect.top,
            0,
            upwardVelocity,
            config.PLAYER_MISSILE_DAMAGE,
        )

    def isInvincible(self, currentTime):
        """判断战机当前是否处于无敌状态。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。

        返回:
            bool: 仍在无敌时间内返回 True。
        """
        return currentTime < self.invincibleUntilTime

    def takeHit(self, currentTime):
        """处理战机被击中：扣减生命并进入短暂无敌。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。

        返回:
            bool: 本次确实造成扣血返回 True；无敌期间被忽略返回 False。
        """
        if self.isInvincible(currentTime):
            return False
        self.remainingLives -= 1
        self.invincibleUntilTime = currentTime + config.PLAYER_INVINCIBLE_DURATION_MS
        return True

    def isDestroyed(self):
        """判断战机生命值是否已耗尽。

        返回:
            bool: 生命值小于等于零返回 True。
        """
        return self.remainingLives <= 0

    def shouldRenderThisFrame(self, currentTime):
        """决定本帧是否绘制战机，用于实现无敌闪烁效果。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。

        返回:
            bool: 应当绘制返回 True。
        """
        if not self.isInvincible(currentTime):
            return True
        blinkPhase = (currentTime // config.PLAYER_BLINK_INTERVAL_MS) % 2
        return blinkPhase == 0

    def drawSelf(self, targetSurface, currentTime):
        """绘制战机（无敌闪烁时可能跳过本帧绘制）。

        参数:
            targetSurface (pygame.Surface): 绘制目标。
            currentTime (int): 当前游戏时间（毫秒）。
        """
        if self.shouldRenderThisFrame(currentTime):
            targetSurface.blit(self.planeImage, self.rect)


class EnemyPlane:
    """敌机。

    职责: 按所属类型预设的运动轨迹自主移动、循环播放螺旋桨动画、
          定时向下发射导弹，并记录血量与击毁得分。三种敌机分别使用
          竖直、正弦、折线三种不同的运动轨迹。
    """

    def __init__(self, enemyType, animationFrames, missileImage, typeSettings, spawnCenterX):
        """初始化一架敌机。

        参数:
            enemyType (int): 敌机类型编号（1、2 或 3）。
            animationFrames (list[pygame.Surface]): 该类型的动画帧序列。
            missileImage (pygame.Surface): 敌机导弹贴图（朝下）。
            typeSettings (dict): 该类型在 config 中的属性字典。
            spawnCenterX (int): 出生时的中心横坐标。
        """
        self.enemyType = enemyType
        self.animationFrames = animationFrames
        self.missileImage = missileImage
        self.currentFrameIndex = 0
        self.lastAnimationTime = 0

        self.rect = animationFrames[0].get_rect()
        self.rect.centerx = spawnCenterX
        self.rect.bottom = 0  # 从屏幕上方外侧进入

        self.remainingHealth = typeSettings["maxHealth"]
        self.downSpeed = typeSettings["downSpeed"]
        self.trajectory = typeSettings["trajectory"]
        self.scoreValue = typeSettings["scoreValue"]
        self.fireIntervalMs = typeSettings["fireIntervalMs"]
        self.lastFireTime = 0

        # 正弦轨迹需要的基准横坐标与相位角
        self.baseCenterX = spawnCenterX
        self.sineAngle = 0.0
        # 折线轨迹的当前水平方向（+1 向右，-1 向左）
        self.horizontalDirection = 1

    def updateAnimation(self, currentTime):
        """按固定间隔循环切换动画帧。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        if currentTime - self.lastAnimationTime < config.ENEMY_ANIMATION_INTERVAL_MS:
            return
        self.lastAnimationTime = currentTime
        frameCount = len(self.animationFrames)
        self.currentFrameIndex = (self.currentFrameIndex + 1) % frameCount

    def updatePosition(self):
        """根据敌机类型调用相应的轨迹算法移动一帧。"""
        if self.trajectory == config.TRAJECTORY_STRAIGHT:
            self.moveStraightDown()
        elif self.trajectory == config.TRAJECTORY_SINE:
            self.moveAlongSineWave()
        else:
            self.moveAlongZigzag()

    def moveStraightDown(self):
        """轨迹一：竖直向下匀速飞行。"""
        self.rect.y += self.downSpeed

    def moveAlongSineWave(self):
        """轨迹二：一边下行一边按正弦曲线左右摆动。"""
        self.rect.y += self.downSpeed
        self.sineAngle += config.SINE_ANGULAR_SPEED
        horizontalOffset = config.SINE_AMPLITUDE * math.sin(self.sineAngle)
        self.rect.centerx = int(self.baseCenterX + horizontalOffset)

    def moveAlongZigzag(self):
        """轨迹三：一边下行一边沿折线水平移动，碰到屏幕边缘即反弹。"""
        self.rect.y += self.downSpeed
        self.rect.x += config.ZIGZAG_HORIZONTAL_SPEED * self.horizontalDirection
        if self.rect.left <= 0:
            self.rect.left = 0
            self.horizontalDirection = 1
        elif self.rect.right >= config.SCREEN_WIDTH:
            self.rect.right = config.SCREEN_WIDTH
            self.horizontalDirection = -1

    def tryFire(self, currentTime):
        """在开火间隔到达且敌机已进入屏幕时，向下发射一枚导弹。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。

        返回:
            Missile | None: 成功发射返回导弹，否则返回 None。
        """
        if self.rect.top < 0:
            return None
        if currentTime - self.lastFireTime < self.fireIntervalMs:
            return None
        self.lastFireTime = currentTime
        return Missile(
            self.missileImage,
            self.rect.centerx,
            self.rect.bottom,
            0,
            config.ENEMY_MISSILE_SPEED,
            config.ENEMY_COLLISION_DAMAGE_TO_PLAYER,
        )

    def takeDamage(self, damageAmount):
        """扣减敌机血量。

        参数:
            damageAmount (int): 被命中造成的伤害值。
        """
        self.remainingHealth -= damageAmount

    def isDead(self):
        """判断敌机是否已被击毁。

        返回:
            bool: 血量小于等于零返回 True。
        """
        return self.remainingHealth <= 0

    def hasFlownOffScreen(self):
        """判断敌机是否已飞出屏幕下方。

        返回:
            bool: 完全离开屏幕底部返回 True。
        """
        return self.rect.top > config.SCREEN_HEIGHT

    def drawSelf(self, targetSurface):
        """绘制敌机当前动画帧。

        参数:
            targetSurface (pygame.Surface): 绘制目标。
        """
        currentFrame = self.animationFrames[self.currentFrameIndex]
        targetSurface.blit(currentFrame, self.rect)


class Boss:
    """最终 BOSS。

    职责: 在所有普通敌机被消灭后入场，先下行到指定高度，随后在屏幕
          顶部左右巡逻；定时进行扇形齐射，一次发射多枚朝不同方向飞行
          的导弹；血量远高于普通敌机，需要持续攻击才能击败。
    """

    def __init__(self, bossImage, missileBaseImage):
        """初始化 BOSS。

        参数:
            bossImage (pygame.Surface): BOSS 贴图。
            missileBaseImage (pygame.Surface): 用于生成各方向导弹的基准贴图。
        """
        self.bossImage = bossImage
        self.missileBaseImage = missileBaseImage
        self.rect = bossImage.get_rect()
        self.rect.centerx = config.SCREEN_WIDTH // 2
        self.rect.bottom = 0  # 从屏幕上方进入

        self.maxHealth = config.BOSS_MAX_HEALTH
        self.remainingHealth = config.BOSS_MAX_HEALTH
        self.horizontalDirection = 1
        self.lastFireTime = 0

    def updateMovement(self):
        """更新 BOSS 位置：先入场下行，到位后左右巡逻。"""
        if self.isEntering():
            self.rect.y += config.BOSS_ENTER_SPEED
            return
        self.patrolHorizontally()

    def isEntering(self):
        """判断 BOSS 是否仍在入场下行阶段。

        返回:
            bool: 尚未到达停留高度返回 True。
        """
        return self.rect.top < config.BOSS_STOP_Y

    def patrolHorizontally(self):
        """在屏幕顶部左右往返巡逻，碰到边缘即反向。"""
        self.rect.x += config.BOSS_MOVE_SPEED * self.horizontalDirection
        if self.rect.left <= 0:
            self.rect.left = 0
            self.horizontalDirection = 1
        elif self.rect.right >= config.SCREEN_WIDTH:
            self.rect.right = config.SCREEN_WIDTH
            self.horizontalDirection = -1

    def tryFireVolley(self, currentTime):
        """在入场完成且开火间隔到达时，进行一次扇形齐射。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。

        返回:
            list[Missile]: 本次齐射产生的导弹列表；条件不满足时为空列表。
        """
        if self.isEntering():
            return []
        if currentTime - self.lastFireTime < config.BOSS_FIRE_INTERVAL_MS:
            return []
        self.lastFireTime = currentTime
        return self.buildSpreadMissiles()

    def buildSpreadMissiles(self):
        """构造一组朝不同方向飞行的导弹，形成扇形弹幕。

        返回:
            list[Missile]: 覆盖设定扇形角度的多枚导弹。
        """
        missileList = []
        missileCount = config.BOSS_MISSILE_COUNT_PER_VOLLEY
        totalSpread = config.BOSS_SPREAD_ANGLE_DEGREES
        startAngle = -totalSpread / 2
        angleStep = totalSpread / (missileCount - 1)

        for missileIndex in range(missileCount):
            offsetDegrees = startAngle + angleStep * missileIndex
            offsetRadians = math.radians(offsetDegrees)
            velocityX = config.BOSS_MISSILE_SPEED * math.sin(offsetRadians)
            velocityY = config.BOSS_MISSILE_SPEED * math.cos(offsetRadians)
            orientedImage = pygame.transform.rotate(self.missileBaseImage, -offsetDegrees)
            singleMissile = Missile(
                orientedImage,
                self.rect.centerx,
                self.rect.bottom,
                velocityX,
                velocityY,
                config.ENEMY_COLLISION_DAMAGE_TO_PLAYER,
            )
            missileList.append(singleMissile)
        return missileList

    def takeDamage(self, damageAmount):
        """扣减 BOSS 血量。

        参数:
            damageAmount (int): 被命中造成的伤害值。
        """
        self.remainingHealth -= damageAmount

    def isDead(self):
        """判断 BOSS 是否已被击败。

        返回:
            bool: 血量小于等于零返回 True。
        """
        return self.remainingHealth <= 0

    def getHealthRatio(self):
        """计算 BOSS 当前血量占总血量的比例，用于绘制血条。

        返回:
            float: 介于 0.0 与 1.0 之间的血量比例。
        """
        healthRatio = self.remainingHealth / self.maxHealth
        if healthRatio < 0:
            return 0.0
        return healthRatio

    def drawSelf(self, targetSurface):
        """绘制 BOSS 贴图。

        参数:
            targetSurface (pygame.Surface): 绘制目标。
        """
        targetSurface.blit(self.bossImage, self.rect)
