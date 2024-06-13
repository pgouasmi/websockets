import pygame

width, height = 1200, 800
white = (255, 255, 255)
black = (0, 0, 0)
class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 3
        self.lastTouch = 0
        self.canMove = True
        self.score = 0

    def draw(self, win):
        pygame.draw.rect(win, white, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        temp = self.y
        if up:
            temp -= self.vel
            if temp < 0:
                temp = 0
        else:
            temp += self.vel
            if temp > height - self.height:
                temp = height - self.height
        self.y = temp

    def serialize(self):
        res:dict = {}
        res["x"] = self.x
        res["y"] = self.y

        return res