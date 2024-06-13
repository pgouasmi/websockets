
from paddle import Paddle
from ball import Ball
import math
import time
import json
# import main
import pygame
import random
from pong_ql import QL_AI
import asyncio


class Game:
    def __init__(self):
        print("Game constructor")
        self.width = 1500
        self.height = 1000
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        self.ball: Ball = Ball(self.width // 2, self.height // 2, 15)
        self.paddle1: Paddle = Paddle(100, self.height // 2 - 60, 20, 120)
        self.paddle2: Paddle = Paddle(self.width - 100, self.height // 2 - 60, 20, 120)
        self.ai = QL_AI()

        self.scoreLimit = 1
        self.DIFFICULTY = 3
        self.RUNNING_AI = True
        self.SAVING = False
        self.TRAINING = True
        self.TRAININGPARTNER = True
        self.LOADING = False
        self.testing = True
        self.lastDump = 0
        self.ai.training = self.TRAINING

        self.run = True
        self.pause = False

        self.currentTs = time.time()
        self.NewCalculusNeeded = True
        self.pauseCoolDown = self.currentTs
        self.lastSentInfos = 0
        self.state = {}

        self.init_ai()
        pygame.init()
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pong")
        self.last_frame_time = 0
        # self.rungame()

    async def rungame(self):
        ball = self.ball
        paddle1 = self.paddle1
        paddle2 = self.paddle2
        ai = self.ai


        while self.run:

            # if pause == False and self.lastDump == 0 or time.time() - self.lastDump > 1 / 60:
            #     print("NEW DUMP")
            #     self.dump_file = open("dump_file.json", "w+")
            #     json.dump(self.serialize(), self.dump_file, indent=6)
            #     self.lastDump = time.time()
            #     self.dump_file.close()
            # if self.lastSentInfos == 0:
            #     self.state = self.getGameState()
            current_time = time.time()

            if self.NewCalculusNeeded == True:
                if ball.x_vel < 0:
                    self.nextCollision = ball.calculateNextCollisionPosition(paddle1)
                else:
                    self.nextCollision = ball.calculateNextCollisionPosition(paddle2)
                if self.TRAININGPARTNER == True:
                    paddle1.y = self.nextCollision[1] + random.uniform(-30, 30) - 60
                self.NewCalculusNeeded = False
                # print(f"next collision: {self.nextCollision}")
            self.state = None
            self.nextState = None

            pygame.time.delay(1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.run = False
            if keys[pygame.K_SPACE]:
                self.currentTs = time.time()
                if self.currentTs - 0.2 > self.pauseCoolDown:
                    self.pauseCoolDown = self.currentTs
                    if self.pause == True:
                        self.pause = False
                    else:
                        self.pause = True

            if not self.pause:
                # print(f"qtable size: {ai.qtable.__sizeof__()}")
                if self.TRAININGPARTNER == False:
                    if keys[pygame.K_r]:
                        ball.reset()
                    if keys[pygame.K_w] and paddle1.canMove == True:
                        paddle1.move(up=True)
                    if keys[pygame.K_s] and paddle1.canMove == True:
                        paddle1.move(up=False)
                else:
                    self.paddle1.y = self.nextCollision[1] - self.paddle1.height // 2

                if not self.RUNNING_AI:
                    if keys[pygame.K_UP] and paddle2.canMove == True:
                        paddle2.move(up=True)
                    if keys[pygame.K_DOWN] and paddle2.canMove == True:
                        paddle2.move(up=False)

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
                    ball.y_vel = -ball.y_vel

                # Vérification des points
                if ball.x <= 0:
                    # Point pour le joueur 2
                    print(f"POINT GAUCHE: {ball.x}, {ball.y}\n\n\n")
                    paddle2.score += 1
                    # if paddle2.score == self.scoreLimit:
                        # pygame.display.set_mode(self.width / 2, 100)
                        # pygame.display.set_caption("player 2 won")
                        # self.pause = True
                    paddle1.canMove = True
                    paddle2.canMove = True
                    ball.reset()
                    self.NewCalculusNeeded = True
                    # pause = True
                    # resetPaddles(paddle1, paddle2)
                if ball.x >= self.width:
                    # Point pour le joueur 1
                    print(f"POINT DROITE {ball.x}, {ball.y}\n\n\n")
                    print("ball_y: ", ball.y)
                    paddle1.score += 1
                    # if paddle1.score == self.scoreLimit:
                    #     pygame.display.set_mode((self.width / 2, 100))
                    #     pygame.display.set_caption("player 1 won")
                    #     pause = True
                    paddle1.canMove = True
                    paddle2.canMove = True
                    ball.reset()
                    self.NewCalculusNeeded = True
                    # pause = True

                    # resetPaddles(paddle1, paddle2)
                # print(type(self.state))
                # self.state['ball'] = self.ball.x
                self.redraw_window()
                print(f"current time: {current_time}, last frame time: {self.last_frame_time}\n")
                if current_time - self.last_frame_time >= 1/60:
                    new_state = self.getGameState()
                    self.last_frame_time = current_time
                    yield new_state
        if self.SAVING == True:
            if self.testing == True:
                ai.save('testing')
                pygame.quit
            if self.DIFFICULTY == 3:
                ai.save('hard')
            elif self.DIFFICULTY == 2:
                ai.save('medium')
            elif self.DIFFICULTY == 1:
                ai.save('easy')
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
            elif self.DIFFICULTY == 2:
                self.ai.load("AI_medium.pkl")
            elif self.DIFFICULTY == 1:
                self.ai.load("AI_easy.pkl")

    def getGameState(self):
        res = []

        res.append(int(self.ball.x / 40))
        res.append(int(self.ball.y / 40))
        res.append(int(math.degrees(math.atan2(self.ball.y_vel, self.ball.x_vel))) / 10)
        res.append(int((self.paddle2.y + self.paddle2.height / 2) / 40))

        return res


    def interactWithAI(self):
        newTS = time.time()
        # print(f"timestamp in struct: {self.lastSentInfos}, current: {newTS}")
        if (newTS - self.lastSentInfos >= 1):
            self.lastSentInfos = newTS
            # print("NEW INFOS SENT")
            self.state = self.getGameState()
        res = self.ai.getAction(repr(self.state))
        # print(f"AI RES: {res}\n")

        prevY = self.paddle2.y

        if res == 0:
            pass
            # print("STAYS STILL")
        if res == 1 and self.paddle2.canMove == True:
            self.paddle2.move(up=True)
            # print("GOES UP")
        if res == 2 and self.paddle2.canMove == True:
            self.paddle2.move(up=False)
            # print("GOES DOWN")

        # if self.TRAINING == True:
        nextState = self.state
        reward = self.ai.getReward(self.nextCollision, res, prevY, self.DIFFICULTY)
        # print("states: ", self.state[1], self.state[3], self.nextState[1], self.nextState[3])
        self.ai.upadateQTable(repr(self.state), res, reward, repr(self.nextState))

    def serialize(self):
        res:dict = {}
        res["ball"] = self.ball.serialize()
        res["paddle1"] = self.paddle1.serialize()
        res["paddle2"] = self.paddle2.serialize()

        return res

    def update(self):
        pass