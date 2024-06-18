
from paddle import Paddle
from ball import Ball
import math
import time
import json
import pygame
import random
from pong_ql import QL_AI
import asyncio


class Game:
    def __init__(self):
        # print("Game constructor")
        self.width = 1500
        self.height = 1000
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        self.display = True
        self.CLI_controls = True
        self.goal1 = False
        self.goal2 = False

        self.ball: Ball = Ball(self.width // 2, self.height // 2, self.height // 100, self.width, self.height)
        self.paddle1: Paddle = Paddle(self.width // 30, self.height // 2 - 60, self.height // 150, self.height // 6, self.width, self.height)
        self.paddle2: Paddle = Paddle(self.width - self.width // 30, self.height // 2 - 60, self.height // 150, self.height // 6, self.width, self.height)

        self.ai = QL_AI(self.width, self.height, self.paddle2.width, self.paddle2.height)

        self.scoreLimit = 3
        self.DIFFICULTY = 3
        self.RUNNING_AI = True
        self.SAVING = True
        self.TRAINING = True
        self.TRAININGPARTNER = True
        self.LOADING = False
        self.testing = False
        self.lastDump = 0
        self.ai.training = self.TRAINING
        self.gameOver = False

        self.run = True
        self.pause = True

        self.currentTs = time.time()
        self.NewCalculusNeeded = True
        self.pauseCoolDown = self.currentTs
        self.lastSentInfos = 0
        self.gameState = {}
        self.are_args_set = False

        self.init_ai()
        if self.display == True or self.CLI_controls == True:
            pygame.init()
            if self.display == True:
                self.win = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption("Pong")
        self.last_frame_time = 0
        # self.rungame()


    def handleArguments(self, event):
        print(event)
        # handling the argumemnts -> if OK ->
        self.are_args_set = True

    def handlePauseResetQuit(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameOver = True
                    self.run = False
        self.keys = pygame.key.get_pressed()
        keys = self.keys
        if keys[pygame.K_r]:
            self.ball.reset()
        if keys[pygame.K_ESCAPE]:
            self.gameOver = True
        if keys[pygame.K_SPACE]:
            self.currentTs = time.time()
            if self.currentTs - 0.2 > self.pauseCoolDown:
                self.pauseCoolDown = self.currentTs
                if self.pause == True:
                    self.pause = False
                else:
                    self.pause = True
    

    def handlePlayer1Inputs(self):
        keys = self.keys

        if keys[pygame.K_w] and self.paddle1.canMove == True:
            self.paddle1.move(self.height, up=True)
        if keys[pygame.K_s] and self.paddle1.canMove == True:
            self.paddle1.move(self.height, up=False)

    
    def handlePlayer2Inputs(self):
        keys = self.keys

        if keys[pygame.K_UP] and self.paddle2.canMove == True:
            self.paddle2.move(self.height, up=True)
        if keys[pygame.K_DOWN] and self.paddle2.canMove == True:
            self.paddle2.move(self.height, up=False)

    def save_qtable(self):
        ai = self.ai

        if self.testing == True:
            ai.save('testing')
            pygame.quit
        if self.DIFFICULTY == 3:
            ai.save('hard')
        elif self.DIFFICULTY == 2:
            ai.save('medium')
        elif self.DIFFICULTY == 1:
            ai.save('easy')


    async def rungame(self):
        ball = self.ball
        paddle1 = self.paddle1
        paddle2 = self.paddle2
        ai = self.ai


        while self.run:

            current_time = time.time()

            if self.NewCalculusNeeded == True:
                if ball.x_vel < 0:
                    self.nextCollision = ball.calculateNextCollisionPosition(paddle1)
                else:
                    self.nextCollision = ball.calculateNextCollisionPosition(paddle2)
                if self.TRAININGPARTNER == True:
                    half_height = paddle2.height // 2
                    paddle1.y = self.nextCollision[1] + random.uniform(-half_height, half_height) - half_height
                self.NewCalculusNeeded = False
                
            self.state = None
            self.nextState = None

            pygame.time.delay(1)
            if self.CLI_controls == True:
                self.handlePauseResetQuit()

            if not self.pause:

                if self.TRAININGPARTNER == False:
                    if self.display == True:
                        self.handlePlayer1Inputs()
                else:
                    self.paddle1.y = self.nextCollision[1] - self.paddle1.height // 2

                if not self.RUNNING_AI:
                    if self.CLI_controls == True:
                        self.handlePlayer2Inputs()
                else:
                    self.interactWithAI()

                ball.move()

                # Gestion des collisions avec les raquettes
                if ball.check_collision(paddle1):
                    ball.updateTrajectoryP1(paddle1)
                    self.NewCalculusNeeded = True

                if ball.check_collision(paddle2):
                    # print(f"onpaddle2, px: {paddle2.x}, py: [{paddle2.y}, {paddle2.y + paddle2.height}]\n")
                    ball.updateTrajectoryP2(paddle2)
                    self.NewCalculusNeeded = True

                # Gestion des collisions avec les bords supérieur et inférieur
                if ball.y - ball.radius <= 0 or ball.y + ball.radius >= self.height:
                    if ball.y - ball.radius <= 0:
                        ball.touchedWall = "top"
                    else:
                        ball.touchedWall = "bottom"
                    ball.y_vel = -ball.y_vel

                # Vérification des points
                if ball.x <= 0:
                    self.goal2 = True
                    paddle2.score += 1
                    paddle1.canMove = True
                    paddle2.canMove = True
                    ball.reset()
                    self.NewCalculusNeeded = True
                    self.pause = True

                if ball.x >= self.width:
                    self.goal1 = True
                    paddle1.score += 1
                    paddle1.canMove = True
                    paddle2.canMove = True
                    ball.reset()
                    self.NewCalculusNeeded = True
                    self.pause = True

                # print(f"qtable size: {ai.qtable.__sizeof__()}")
                if self.display == True:
                    self.redraw_window()

                # send JSON game state
            if current_time - self.last_frame_time >= 1/60 or self.isgameover() == True:
                self.serialize()
                self.last_frame_time = current_time
                yield json.dumps(self.gameState)

    def quit(self):
        if self.SAVING == True:
            self.save_qtable()
        if self.display == True or self.CLI_controls:
            pygame.quit()

    def redraw_window(self):
        self.win.fill(self.black)
        self.paddle1.draw(self.win)
        self.paddle2.draw(self.win)
        self.ball.draw(self.win)
        pygame.display.update()

    def resetPaddles(self):
        self.paddle1.y = self.height // 2
        self.paddle2.y = self.height // 2

    def init_ai(self):
        if self.LOADING == True:
            if self.testing == True:
                self.ai.load('AI_testing.pkl')
            elif self.DIFFICULTY == 3:
                self.ai.load("AI_hard.pkl")
                print("hard AI loaded")
            elif self.DIFFICULTY == 2:
                self.ai.load("AI_medium.pkl")
            elif self.DIFFICULTY == 1:
                self.ai.load("AI_easy.pkl")

    def getGameState(self):
        res = []

        res.append(int(self.ball.x / 10))
        res.append(int(self.ball.y / 10))
        res.append(int(math.degrees(math.atan2(self.ball.y_vel, self.ball.x_vel))) / 10)
        res.append(int((self.paddle2.y + self.paddle2.height / 2) / 10))

        return res


    def interactWithAI(self):
        newTS = time.time()
        if self.TRAINING == False:
            # print(f"newTS: {newTS}, lastSentInfos: {self.lastSentInfos}\n")
            if (newTS - self.lastSentInfos >= 1):
                self.lastSentInfos = newTS
                self.state = self.getGameState()
                print("NEW STATE: ", self.state)
        else:
            self.state = self.getGameState()
        res = self.ai.getAction(repr(self.state))
        print(f"AI RES: {res}\n")

        prevY = self.paddle2.y

        if res == 0:
            pass
            # print("STAYS STILL")
        if res == 1 and self.paddle2.canMove == True:
            self.paddle2.move(self.height, up=True)
            # print("GOES UP")
        if res == 2 and self.paddle2.canMove == True:
            self.paddle2.move(self.height, up=False)
            # print("GOES DOWN")

        if self.TRAINING == True:
            nextState = self.state
            reward = self.ai.getReward(self.nextCollision, res, prevY, self.DIFFICULTY)
            # print("states: ", self.state[1], self.state[3], self.nextState[1], self.nextState[3])
            self.ai.upadateQTable(repr(self.state), res, reward, repr(self.nextState))


    def isgameover(self):
        if self.TRAINING == False:
            if self.paddle1.score >= self.scoreLimit or self.paddle2.score >= self.scoreLimit:
                self.gameOver = True
                return True
        if self.gameOver == True:
            return True
        return False


    def serialize(self):
        if self.isgameover():
            self.gameState["type"] = "gameover"
        else:
            self.gameState["type"] = "None"
        if self.goal1 == True:
            self.gameState["goal"] = "1"
            self.goal1 = False
        elif self.goal2 == True:
            self.gameState["goal"] = "2"
            self.goal2 = False
        else:
            self.gameState["goal"] = "None"
        if self.pause == False:
            self.gameState["game"] = self.gameSerialize()
            self.gameState["ball"] = self.ball.serialize(self)
            self.gameState["paddle1"] = self.paddle1.serialize(self)
            self.gameState["paddle2"] = self.paddle2.serialize(self)
    
    def gameSerialize(self):
        res:dict = {}
        res["scoreLimit"] = self.scoreLimit
        res["pause"] = self.pause

        return res

    def update(self):
        pass