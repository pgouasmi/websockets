import numpy as np
import pickle
import random

class QL_AI:
    def __init__(self, width, height, paddle_width, paddle_height) -> None:
        self.win_width = width
        self.win_height = height
        self.paddle_height = paddle_height
        self.paddle_width = paddle_width
        self.alpha = 0.4
        self.gamma = 0.7
        self.epsilon_decay = 0.00001 #baisse du taux d'apprentissage au fur et a mesure du jeu
        self.epsilon_min = 0.01
        self.epsilon = 1 # 1 = uniquement exploration
        self.qtable = {}
        self.rewards = []
        self.episodes = []
        self.average = []
        self.name = "Test"

    def epsilon_greedy(self):
        if self.epsilon == self.epsilon_min:
            return
        self.epsilon -= self.epsilon_decay
        if self.epsilon < self.epsilon_min:
            self.epsilon = self.epsilon_min

    def getAction(self, state):
        # print(f"In get Action, state: {state}")
        if state not in self.qtable:
            print("this state is not in qtable")
            self.qtable[state] = np.zeros(3)
        self.epsilon_greedy()
        if self.training == True: #need to implement training modes
            if np.random.uniform() < self.epsilon:
                action = np.random.choice(3)
            else:
                action = np.argmax(self.qtable[state])
        else:
            action = np.argmax(self.qtable[state])
        
        return action
    
    def upadateQTable(self, state, action, reward, nextState):
        if nextState not in self.qtable:
            self.qtable[nextState] = np.zeros(3)
        tdTarget = reward + self.gamma * np.max(self.qtable[nextState])
        tdError = tdTarget - self.qtable[state][action]
        self.qtable[state][action] += self.alpha * tdError

    def getReward(self, nextCollision, action, previousPosition, difficulty):

        maxReward = 10
        minReward = -10
        result:int = 0

        # print(f"nextCollision: {nextCollision}")
        if difficulty == 1:
            nextCollision[1] += random.randint(-5, 5)
        if nextCollision[0] == 1:
            if action == 1:
                if nextCollision[1] < (previousPosition + self.paddle_height // 2):
                    result = maxReward
                else:
                    result = minReward
            elif action == 2:
                if nextCollision[1] > (previousPosition + self.paddle_height // 2):
                    result = maxReward
                else:
                    result = minReward
            elif action == 0:
                if previousPosition + self.paddle_height // 2 >= nextCollision[1] - 10 and previousPosition + self.paddle_height // 2 <= nextCollision[1] + 10:
                    result = maxReward
                else:
                    result = minReward
        else:
            if difficulty == 3:
                if action == 1 and nextCollision[1] < previousPosition + self.paddle_height and previousPosition > self.win_height // 4:
                    result = maxReward
                elif action == 2 and nextCollision[1] > previousPosition + self.paddle_height and previousPosition < self.win_height  * 0.75:
                    result = maxReward
                elif action == 0 and abs(nextCollision[1] - previousPosition) < self.paddle_height:
                    result = maxReward
                else:
                    result = minReward
            else:
                if action == 1 or action == 2:
                    result = minReward
                else:
                    result = maxReward

        print(f"REWARD: {result}\n")
        return result
     
    def save(self, name):
        with open(f"AI_{name}.pkl", 'wb') as file:
            pickle.dump(self.qtable, file)

    def load(self, name):
        with open(name, 'rb') as file:
            self.qtable = pickle.load(file)



        
