import math
import pygame
import time
import copy
import random
from paddle import Paddle

width, height = 1500, 1000
white = (255, 255, 255)
black = (0, 0, 0)
class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.x_vel = -4
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, white, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = width // 2
        self.y = height // 2
        self.x_vel = -4
        self.y_vel = 0

    # ma matrice
    #       -90
    #        |
    #  -180<----->0
    #        |
    #        90

    def updateTrajectoryP2(self, paddle):

        currentTs = time.time()
        if paddle.lastTouch > currentTs - 0.5:
            print("Too soon for new touch")
            return
        paddle.lastTouch = currentTs

        current_xvel = self.x_vel
        current_yvel = self.y_vel
        currentSpeed = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
        relativeImpactPoint = (self.y - paddle.y) / paddle.height
        currentAngle = math.degrees(math.atan2(self.y_vel, self.x_vel))
        naturalAngle = math.degrees(math.atan2(self.y_vel, -self.x_vel))
        if (relativeImpactPoint > 1):
            relativeImpactPoint = 1
        if (relativeImpactPoint < 0):
            relativeImpactPoint = 0

        arete = False

        print(
            f"ON TOUCH P2:\nxvel = {current_xvel}\nyvel = {current_yvel}\nrelative Impact Point = {relativeImpactPoint}\nspeed = {currentSpeed}\nCurrentAngle: {currentAngle}\nnatural Angle: {naturalAngle}\nball X: {self.x}\n ball Y: {self.y}\npaddle X: {paddle.x}\npaddle Y: {paddle.y}")

        goalAngle: float

        if self.x + self.radius / 2 > paddle.x + paddle.width:
            arete = True
            paddle.canMove = False
            print("touch ARETE")
            if self.y > paddle.y:
                print("bottom Arete")
                goalAngle = 80
            else:
                print("top Arete")
                goalAngle = -80


        elif currentAngle < 15 and currentAngle > -15:
            goalAngle = naturalAngle - (35 * (relativeImpactPoint - 0.5))
            print(f"got in flat angle. New Angle: {goalAngle}")

        elif (currentAngle < 0):
            # la balle monte
            if relativeImpactPoint < 0.5:
                # tape haut -> angle va tendre vers -90 degres
                goalAngle = naturalAngle + (35 * (1 - relativeImpactPoint))
                print(f"Ball goes up, hit with top. New Angle: {goalAngle}")
                if (goalAngle > -130):
                    goalAngle = -130
                    print(f"    Angle corrected. now {goalAngle}")

            else:
                # tape bas -> angle va tendre vers -180
                goalAngle = naturalAngle - (((180 - abs(naturalAngle)) * relativeImpactPoint))
                print(f"Ball goes up, hit with bottom. New Angle: {goalAngle}")
        else:
            # balle descend
            if relativeImpactPoint < 0.5:
                # tape haut -> angle va tendre vers 180 degres
                goalAngle = naturalAngle + ((180 - abs(naturalAngle)) * (1 - relativeImpactPoint))
                print(f"Ball goes down, hit with top. New Angle: {goalAngle}")

            else:
                # tape bas -> angle va tendre vers 90
                goalAngle = naturalAngle - (35 * (relativeImpactPoint - 0.5))
                print(f"Ball goes down, hit with bottom. New Angle: {goalAngle}")
                if (goalAngle < 130):
                    goalAngle = 130
                    print(f"    Angle corrected. now {goalAngle}")

        if math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) < 35:
            self.x_vel = currentSpeed * 1.05 * math.cos(math.radians(goalAngle))
            self.y_vel = currentSpeed * 1.05 * math.sin(math.radians(goalAngle))
            if (arete):
                self.x_vel *= 2
                self.y_vel *= 2
            if (abs(goalAngle) > 180 - 20 and math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) < 35):
                self.x_vel *= 1.1
                self.y_vel *= 1.1

    def updateTrajectoryP1(self, paddle):

        currentTs = time.time()
        if paddle.lastTouch > currentTs - 0.5:
            print("Too soon for new touch")
            return
        paddle.lastTouch = currentTs

        current_xvel = self.x_vel
        current_yvel = self.y_vel
        currentSpeed = math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)
        relativeImpactPoint = (self.y - paddle.y) / paddle.height
        currentAngle = math.degrees(math.atan2(self.y_vel, self.x_vel))
        naturalAngle = math.degrees(math.atan2(self.y_vel, -self.x_vel))
        if (relativeImpactPoint > 1):
            relativeImpactPoint = 1
        if (relativeImpactPoint < 0):
            relativeImpactPoint = 0
        goalAngle: float
        arete = False
        print("ON P1")

        print(
            f"ON TOUCH P1:\nxvel = {current_xvel}\nyvel = {current_yvel}\nrelative Impact Point = {relativeImpactPoint}\nspeed = {currentSpeed}\nCurrentAngle: {currentAngle}\nnatural Angle: {naturalAngle}\nball X: {self.x}\n ball Y: {self.y}\npaddle X: {paddle.x}\n paddle Y: {paddle.y}")

        if self.x - self.radius / 2 < paddle.x + paddle.width:
            arete = True
            paddle.canMove = False
            print("touch ARETE")
            if self.y > paddle.y:
                print("bottom Arete")
                goalAngle = 100
            else:
                print("top Arete")
                goalAngle = -100


        elif currentAngle > 165 or currentAngle < -165:
            goalAngle = naturalAngle + (40 * (relativeImpactPoint - 0.5))
            print(f"got in flat angle. New Angle: {goalAngle}\n")

        elif (currentAngle < 0):
            # la balle monte
            if relativeImpactPoint < 0.5:
                # tape haut -> angle va tendre vers -90 degres
                goalAngle = naturalAngle - (35 * (1 - relativeImpactPoint))
                print(f"Ball goes up, hit with top. New Angle: {goalAngle}\n")
                if goalAngle < -50:
                    goalAngle = -50
                self.x += 10

            else:
                # tape bas -> angle va tendre vers -180
                goalAngle = naturalAngle + (((abs(naturalAngle)) * relativeImpactPoint))
                print(f"Ball goes up, hit with bottom. New Angle: {goalAngle}\n")

        else:
            # balle descend
            if relativeImpactPoint < 0.5:
                # tape haut -> angle va tendre vers 180 degres
                goalAngle = naturalAngle - ((abs(naturalAngle)) * (1 - relativeImpactPoint))
                print(f"Ball goes down, hit with top. New Angle: {goalAngle}\n")
            else:
                # tape bas -> angle va tendre vers 90

                goalAngle = naturalAngle

                goalAngle = (naturalAngle + (35 * relativeImpactPoint))
                print(f"Ball goes down, hit with bottom. New Angle: {goalAngle}\n")
                self.x += 10
                if goalAngle > 50:
                    goalAngle = 50
                    print(f"    Angle corrected. now {goalAngle}")
                    self.x += 2

        self.x_vel = currentSpeed * 1.05 * math.cos(math.radians(goalAngle))
        self.y_vel = currentSpeed * 1.05 * math.sin(math.radians(goalAngle))

        if math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) < 35:
            self.x_vel = currentSpeed * 1.05 * math.cos(math.radians(goalAngle))
            self.y_vel = currentSpeed * 1.05 * math.sin(math.radians(goalAngle))
            if (arete):
                self.x_vel *= 2
                self.y_vel *= 2
            if (abs(goalAngle) > 180 - 20 and math.sqrt(self.x_vel ** 2 + self.y_vel ** 2) < 35):
                self.x_vel *= 1.1
                self.y_vel *= 1.1

        pygame.time.delay(20)

    def check_collision(self, paddle:Paddle):
        if (self.x - self.radius < paddle.x + paddle.width and
            self.x + self.radius > paddle.x and
            self.y - self.radius < paddle.y + paddle.height and
            self.y + self.radius > paddle.y):
            return True
        return False

    def calculateNextCollisionPosition(self, paddle:Paddle):
        res = []
        if paddle.x < width // 2:
            res.append(-1)
        else:
            res.append(1)
        tempBall = copy.deepcopy(self)
        tempPaddle = copy.deepcopy(paddle)

        # Déplacement de la balle jusqu'à ce qu'elle atteigne la position x = paddle2_x
        while tempBall.check_collision(tempPaddle) == False and tempBall.x > 0 and tempBall.x < width:
            # Calcule la nouvelle position de la balle en ajoutant la vitesse de la balle à sa position actuelle
            # print(f"tempball.x: {tempBall.x}, tempball.y: {tempBall.y}")
            tempBall.x = tempBall.x + tempBall.x_vel
            tempBall.y = tempBall.y + tempBall.y_vel
            tempPaddle.y = tempBall.y

            # Vérifie si la nouvelle position de la balle dépasse les bords du terrain
            if tempBall.y - tempBall.radius <= 0 or tempBall.y + tempBall.radius >= height:
                tempBall.y_vel = -tempBall.y_vel

        print(f"contact zone = [{tempBall.y - tempPaddle.height / 2}, {tempBall.y + tempPaddle.height / 2}]")
        tempBall.y += random.uniform(-50, 50)
        res.append(tempBall.y)
        return res # Retourne la position y correspondant

    def serialize(self):
        res:dict = {}
        res["x"] = self.x
        res["y"] = self.y
        res["x_vel"] = self.x_vel
        res["y_vel"] = self.y_vel

        return res


