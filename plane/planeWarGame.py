"""planeWarGame.py —— 空战小游戏的主控制器模块。

本模块只包含一个 PlaneWarGame 类，负责把背景、我方战机、敌机、BOSS
与各类导弹组织起来：维护游戏主循环与状态机，控制敌机的生成节奏与
BOSS 的登场时机，统一处理碰撞判定、计分以及界面（HUD、开始画面、
胜负画面）的绘制。各对象自身的行为则由 gameSprites 模块负责。
"""

import random

import pygame

import config
import gameResources
from gameSprites import Background, Boss, EnemyPlane, MyPlane


class PlaneWarGame:
    """空战小游戏控制器。

    职责: 初始化窗口与资源，运行主循环，根据当前游戏状态更新逻辑、
          检测碰撞与胜负、并把画面绘制出来。
    """

    def __init__(self):
        """初始化 Pygame、窗口、字体并加载全部图片资源。"""
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.smallFont = gameResources.loadGameFont(config.FONT_SIZE_SMALL)
        self.normalFont = gameResources.loadGameFont(config.FONT_SIZE_NORMAL)
        self.largeFont = gameResources.loadGameFont(config.FONT_SIZE_LARGE)

        self.loadAllResources()
        self.gameState = config.STATE_START
        self.resetGame()

    # ----------------------------------------------------------------
    # 资源加载
    # ----------------------------------------------------------------
    def loadAllResources(self):
        """加载并预处理游戏所需的全部图片资源。"""
        self.backgroundImages = self.buildBackgroundImages()
        self.playerImage = gameResources.loadImage(config.PLAYER_IMAGE_FILE)
        self.playerMissileImage = gameResources.loadImageByScale(
            config.PLAYER_MISSILE_IMAGE_FILE, config.PLAYER_MISSILE_SCALE
        )
        self.enemyFramesByType = self.buildEnemyFramesByType()
        self.enemyMissileImage = self.buildDownwardEnemyMissileImage()
        self.bossImage = gameResources.loadImageByScale(config.BOSS_IMAGE_FILE, 0.6)
        self.bossMissileImage = gameResources.loadImage(config.BOSS_MISSILE_IMAGE_FILE)

    def buildBackgroundImages(self):
        """把全部背景图缩放到屏幕大小，返回背景图列表。

        返回:
            list[pygame.Surface]: 已缩放的背景图列表。
        """
        scaledBackgrounds = []
        for fileName in config.BACKGROUND_FILE_NAMES:
            scaledImage = gameResources.loadScaledImage(
                fileName, config.SCREEN_WIDTH, config.SCREEN_HEIGHT
            )
            scaledBackgrounds.append(scaledImage)
        return scaledBackgrounds

    def buildEnemyFramesByType(self):
        """加载三种敌机的动画帧，并统一同一类型内各帧的尺寸。

        返回:
            dict[int, list[pygame.Surface]]: 类型编号到动画帧列表的映射。
        """
        framesByType = {}
        for enemyType, typeSettings in config.ENEMY_TYPE_SETTINGS.items():
            framesByType[enemyType] = self.buildFramesForType(typeSettings["imagePrefix"])
        return framesByType

    def buildFramesForType(self, imagePrefix):
        """加载某一类型敌机的全部动画帧并对齐到首帧尺寸。

        参数:
            imagePrefix (str): 该类型贴图的文件名前缀，如 "enemyPlane_01"。

        返回:
            list[pygame.Surface]: 尺寸一致的动画帧列表。
        """
        frameList = []
        for frameNumber in range(1, config.ENEMY_FRAME_COUNT + 1):
            fileName = "%s_%02d.png" % (imagePrefix, frameNumber)
            frameList.append(gameResources.loadImage(fileName))

        targetWidth = frameList[0].get_width()
        targetHeight = frameList[0].get_height()
        alignedFrames = []
        for frameImage in frameList:
            alignedFrames.append(pygame.transform.smoothscale(frameImage, (targetWidth, targetHeight)))
        return alignedFrames

    def buildDownwardEnemyMissileImage(self):
        """把敌机导弹贴图旋转为朝下方向，便于向我方战机射击。

        返回:
            pygame.Surface: 朝下的敌机导弹贴图。
        """
        horizontalMissile = gameResources.loadImage(config.ENEMY_MISSILE_IMAGE_FILE)
        rotateToDownDegrees = -90
        return pygame.transform.rotate(horizontalMissile, rotateToDownDegrees)

    # ----------------------------------------------------------------
    # 关卡状态重置
    # ----------------------------------------------------------------
    def resetGame(self):
        """重置一局游戏所需的全部状态，回到可重新开始的初始局面。"""
        self.background = Background(self.backgroundImages)
        self.playerPlane = MyPlane(self.playerImage, self.playerMissileImage)
        self.enemyList = []
        self.playerMissiles = []
        self.enemyMissiles = []
        self.boss = None
        self.playerScore = 0

        self.spawnQueue = list(config.ENEMY_SPAWN_SEQUENCE)
        self.lastSpawnTime = 0

    # ----------------------------------------------------------------
    # 主循环
    # ----------------------------------------------------------------
    def run(self):
        """启动并维持游戏主循环，直到玩家关闭窗口。"""
        isRunning = True
        while isRunning:
            currentTime = pygame.time.get_ticks()
            isRunning = self.handleEvents()
            self.updateCurrentState(currentTime)
            self.drawCurrentState(currentTime)
            pygame.display.flip()
            self.clock.tick(config.FRAMES_PER_SECOND)
        pygame.quit()

    def handleEvents(self):
        """处理窗口与键盘事件，并据此切换游戏状态。

        返回:
            bool: 游戏应继续运行返回 True，收到退出请求返回 False。
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.handleKeyDown(event.key)
        return True

    def handleKeyDown(self, pressedKey):
        """根据当前状态响应一次按键，用于开始与重新开始游戏。

        参数:
            pressedKey (int): 被按下的按键常量。
        """
        if self.gameState == config.STATE_START:
            self.startNewRound()
        elif self.gameState in (config.STATE_WIN, config.STATE_LOSE):
            if pressedKey == pygame.K_r:
                self.startNewRound()

    def startNewRound(self):
        """重置状态并进入正式游戏。"""
        self.resetGame()
        self.gameState = config.STATE_PLAYING

    def updateCurrentState(self, currentTime):
        """仅在游戏进行状态下推进游戏逻辑。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        if self.gameState == config.STATE_PLAYING:
            self.updatePlaying(currentTime)

    # ----------------------------------------------------------------
    # 进行中状态的逻辑更新
    # ----------------------------------------------------------------
    def updatePlaying(self, currentTime):
        """推进一帧的全部游戏逻辑。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        self.background.update(currentTime)
        self.updatePlayer(currentTime)
        self.spawnDueEnemy(currentTime)
        self.updateEnemies(currentTime)
        self.trySpawnBoss()
        self.updateBoss(currentTime)
        self.updateMissiles()
        self.handlePlayerMissileHits()
        self.handleHostileMissileHits(currentTime)
        self.handleBodyCollisions(currentTime)
        self.checkEndConditions()

    def updatePlayer(self, currentTime):
        """根据键盘状态移动我方战机并按住空格连续射击。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        pressedKeys = pygame.key.get_pressed()
        self.playerPlane.handleInput(pressedKeys)
        if pressedKeys[pygame.K_SPACE]:
            newMissile = self.playerPlane.tryFire(currentTime)
            if newMissile is not None:
                self.playerMissiles.append(newMissile)

    def spawnDueEnemy(self, currentTime):
        """当生成间隔到达且仍有待出现的敌机时，生成下一架敌机。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        if not self.spawnQueue:
            return
        if currentTime - self.lastSpawnTime < config.ENEMY_SPAWN_INTERVAL_MS:
            return
        self.lastSpawnTime = currentTime
        nextEnemyType = self.spawnQueue.pop(0)
        self.enemyList.append(self.createEnemy(nextEnemyType))

    def createEnemy(self, enemyType):
        """按类型创建一架敌机，并为其选择合适的出生横坐标。

        参数:
            enemyType (int): 敌机类型编号。

        返回:
            EnemyPlane: 新建的敌机对象。
        """
        animationFrames = self.enemyFramesByType[enemyType]
        typeSettings = config.ENEMY_TYPE_SETTINGS[enemyType]
        enemyWidth = animationFrames[0].get_width()
        spawnCenterX = self.pickSpawnCenterX(enemyWidth, typeSettings["trajectory"])
        return EnemyPlane(enemyType, animationFrames, self.enemyMissileImage, typeSettings, spawnCenterX)

    def pickSpawnCenterX(self, enemyWidth, trajectory):
        """为敌机随机选择一个能保证其留在屏幕内的出生横坐标。

        参数:
            enemyWidth (int): 敌机宽度（像素）。
            trajectory (str): 敌机的运动轨迹标识。

        返回:
            int: 出生时的中心横坐标。
        """
        halfWidth = enemyWidth // 2
        leftLimit = halfWidth
        rightLimit = config.SCREEN_WIDTH - halfWidth
        if trajectory == config.TRAJECTORY_SINE:
            leftLimit += config.SINE_AMPLITUDE
            rightLimit -= config.SINE_AMPLITUDE
        if leftLimit >= rightLimit:
            return config.SCREEN_WIDTH // 2
        return random.randint(leftLimit, rightLimit)

    def updateEnemies(self, currentTime):
        """更新全部敌机的动画、位置与开火，并清除已飞出屏幕的敌机。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        survivingEnemies = []
        for enemy in self.enemyList:
            enemy.updateAnimation(currentTime)
            enemy.updatePosition()
            newMissile = enemy.tryFire(currentTime)
            if newMissile is not None:
                self.enemyMissiles.append(newMissile)
            if not enemy.hasFlownOffScreen():
                survivingEnemies.append(enemy)
        self.enemyList = survivingEnemies

    def trySpawnBoss(self):
        """在所有敌机都已出现并被消灭后，让 BOSS 登场（仅一次）。"""
        if self.boss is not None:
            return
        allEnemiesSpawned = len(self.spawnQueue) == 0
        battlefieldCleared = len(self.enemyList) == 0
        if allEnemiesSpawned and battlefieldCleared:
            self.boss = Boss(self.bossImage, self.bossMissileImage)

    def updateBoss(self, currentTime):
        """更新 BOSS 的移动与扇形齐射。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        if self.boss is None:
            return
        self.boss.updateMovement()
        volleyMissiles = self.boss.tryFireVolley(currentTime)
        self.enemyMissiles.extend(volleyMissiles)

    def updateMissiles(self):
        """移动所有导弹并清除已飞出屏幕的导弹。"""
        self.playerMissiles = self.advanceMissiles(self.playerMissiles)
        self.enemyMissiles = self.advanceMissiles(self.enemyMissiles)

    def advanceMissiles(self, missileList):
        """让一组导弹各自前进一帧，并返回仍在屏幕内的导弹。

        参数:
            missileList (list[Missile]): 待更新的导弹列表。

        返回:
            list[Missile]: 仍处于屏幕内的导弹列表。
        """
        survivingMissiles = []
        for missile in missileList:
            missile.update()
            if not missile.isOutOfScreen():
                survivingMissiles.append(missile)
        return survivingMissiles

    # ----------------------------------------------------------------
    # 碰撞处理
    # ----------------------------------------------------------------
    def handlePlayerMissileHits(self):
        """处理我方导弹命中敌机与 BOSS：扣血、计分并回收导弹。"""
        remainingMissiles = []
        for missile in self.playerMissiles:
            if self.tryHitEnemyWithMissile(missile):
                continue
            if self.tryHitBossWithMissile(missile):
                continue
            remainingMissiles.append(missile)
        self.playerMissiles = remainingMissiles

    def tryHitEnemyWithMissile(self, missile):
        """检测一枚我方导弹是否命中某架敌机并结算。

        参数:
            missile (Missile): 待检测的我方导弹。

        返回:
            bool: 命中并消耗了该导弹返回 True。
        """
        for enemy in self.enemyList:
            if missile.rect.colliderect(enemy.rect):
                enemy.takeDamage(missile.damage)
                if enemy.isDead():
                    self.playerScore += enemy.scoreValue
                    self.enemyList.remove(enemy)
                return True
        return False

    def tryHitBossWithMissile(self, missile):
        """检测一枚我方导弹是否命中 BOSS 并结算。

        参数:
            missile (Missile): 待检测的我方导弹。

        返回:
            bool: 命中并消耗了该导弹返回 True。
        """
        if self.boss is None:
            return False
        if missile.rect.colliderect(self.boss.rect):
            self.boss.takeDamage(missile.damage)
            return True
        return False

    def handleHostileMissileHits(self, currentTime):
        """处理敌方导弹命中我方战机：扣减生命并回收导弹。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        playerHitBox = self.buildPlayerHitBox()
        remainingMissiles = []
        for missile in self.enemyMissiles:
            if missile.rect.colliderect(playerHitBox):
                self.playerPlane.takeHit(currentTime)
            else:
                remainingMissiles.append(missile)
        self.enemyMissiles = remainingMissiles

    def handleBodyCollisions(self, currentTime):
        """处理敌机机体撞击我方战机：我方扣血，敌机同时被撞毁。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        playerHitBox = self.buildPlayerHitBox()
        survivingEnemies = []
        for enemy in self.enemyList:
            if enemy.rect.colliderect(playerHitBox):
                self.playerPlane.takeHit(currentTime)
            else:
                survivingEnemies.append(enemy)
        self.enemyList = survivingEnemies

    def buildPlayerHitBox(self):
        """构造略小于贴图的我方战机判定框，使闪避手感更宽容。

        返回:
            pygame.Rect: 收缩后的碰撞判定矩形。
        """
        shrinkMargin = -16
        return self.playerPlane.rect.inflate(shrinkMargin, shrinkMargin)

    # ----------------------------------------------------------------
    # 胜负判定
    # ----------------------------------------------------------------
    def checkEndConditions(self):
        """检测本局是否结束：我方阵亡为失败，击败 BOSS 为胜利。"""
        if self.playerPlane.isDestroyed():
            self.gameState = config.STATE_LOSE
            return
        if self.boss is not None and self.boss.isDead():
            self.playerScore += config.BOSS_SCORE_VALUE
            self.gameState = config.STATE_WIN

    # ----------------------------------------------------------------
    # 画面绘制
    # ----------------------------------------------------------------
    def drawCurrentState(self, currentTime):
        """根据当前游戏状态绘制对应画面。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        if self.gameState == config.STATE_START:
            self.drawStartScreen()
        elif self.gameState == config.STATE_PLAYING:
            self.drawPlayingScene(currentTime)
        else:
            self.drawPlayingScene(currentTime)
            self.drawEndOverlay()

    def drawPlayingScene(self, currentTime):
        """绘制游戏进行中的完整场景与状态栏。

        参数:
            currentTime (int): 当前游戏时间（毫秒）。
        """
        self.background.drawSelf(self.screen)
        for missile in self.playerMissiles:
            missile.drawSelf(self.screen)
        for enemy in self.enemyList:
            enemy.drawSelf(self.screen)
        if self.boss is not None:
            self.boss.drawSelf(self.screen)
        for missile in self.enemyMissiles:
            missile.drawSelf(self.screen)
        self.playerPlane.drawSelf(self.screen, currentTime)
        self.drawHud()

    def drawHud(self):
        """绘制顶部状态栏：得分、剩余生命与 BOSS 血条。"""
        scoreText = "得分: %d" % self.playerScore
        livesText = "生命: %d" % max(self.playerPlane.remainingLives, 0)
        self.drawTextWithShadow(scoreText, self.smallFont, config.COLOR_WHITE, (10, 8))
        livesSurface = self.smallFont.render(livesText, True, config.COLOR_WHITE)
        livesX = config.SCREEN_WIDTH - livesSurface.get_width() - 10
        self.drawTextWithShadow(livesText, self.smallFont, config.COLOR_WHITE, (livesX, 8))
        if self.boss is not None:
            self.drawBossHealthBar()

    def drawBossHealthBar(self):
        """在屏幕顶部绘制 BOSS 的血量条。"""
        barLeft = 60
        barTop = 38
        barWidth = config.SCREEN_WIDTH - barLeft * 2
        barHeight = 12
        backgroundRect = pygame.Rect(barLeft, barTop, barWidth, barHeight)
        pygame.draw.rect(self.screen, config.COLOR_GRAY, backgroundRect)
        currentWidth = int(barWidth * self.boss.getHealthRatio())
        healthRect = pygame.Rect(barLeft, barTop, currentWidth, barHeight)
        pygame.draw.rect(self.screen, config.COLOR_RED, healthRect)
        self.drawTextWithShadow("BOSS", self.smallFont, config.COLOR_YELLOW, (10, barTop - 6))

    def drawStartScreen(self):
        """绘制开始画面，提示操作方式。"""
        self.background.drawSelf(self.screen)
        self.drawCenteredText("空 战 小 游 戏", self.largeFont, config.COLOR_WHITE, 220)
        self.drawCenteredText("方向键移动   空格键发射导弹", self.normalFont, config.COLOR_YELLOW, 330)
        self.drawCenteredText("消灭全部敌机后击败 BOSS 即可获胜", self.smallFont, config.COLOR_WHITE, 390)
        self.drawCenteredText("按任意键开始游戏", self.normalFont, config.COLOR_GREEN, 470)

    def drawEndOverlay(self):
        """在结算时绘制半透明遮罩与胜负提示。"""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.set_alpha(170)
        overlay.fill(config.COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        if self.gameState == config.STATE_WIN:
            resultText = "胜  利  !"
            resultColor = config.COLOR_GREEN
        else:
            resultText = "游  戏  失  败"
            resultColor = config.COLOR_RED

        self.drawCenteredText(resultText, self.largeFont, resultColor, 280)
        finalScoreText = "最终得分: %d" % self.playerScore
        self.drawCenteredText(finalScoreText, self.normalFont, config.COLOR_WHITE, 370)
        self.drawCenteredText("按 R 键重新开始", self.normalFont, config.COLOR_YELLOW, 440)

    def drawCenteredText(self, text, font, color, centerY):
        """在屏幕水平居中处绘制一行带阴影的文字。

        参数:
            text (str): 要绘制的文字。
            font (pygame.font.Font): 使用的字体。
            color (tuple): 文字颜色。
            centerY (int): 文字中心的纵坐标。
        """
        textSurface = font.render(text, True, color)
        textRect = textSurface.get_rect(center=(config.SCREEN_WIDTH // 2, centerY))
        self.drawTextWithShadow(text, font, color, textRect.topleft)

    def drawTextWithShadow(self, text, font, color, position):
        """绘制带黑色阴影的文字以增强在背景上的可读性。

        参数:
            text (str): 要绘制的文字。
            font (pygame.font.Font): 使用的字体。
            color (tuple): 文字颜色。
            position (tuple): 文字左上角坐标。
        """
        shadowOffset = 2
        shadowSurface = font.render(text, True, config.COLOR_SHADOW)
        textSurface = font.render(text, True, color)
        self.screen.blit(shadowSurface, (position[0] + shadowOffset, position[1] + shadowOffset))
        self.screen.blit(textSurface, position)
