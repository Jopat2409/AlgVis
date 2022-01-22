from dataclasses import dataclass
import random
import pygame
import math
import time


@dataclass()
class Node:
    isAlive = False
    liveNeighbors = 0
    neighbors = []


class GameOfLife:

    def __init__(self, nodes: int, liveChance=10):

        self.m_initMousePos = None
        self.m_cYStart = 0
        self.m_cXStart = 0
        self.m_cYOffset = 0
        self.m_cXOffset = 0
        self.XOFFSET = [-1, 0, 1, -1, 1, -1, 0, 1]
        self.YOFFSET = [-1, -1, -1, 0, 0, 1, 1, 1]

        self.seed = time.time()
        random.seed(self.seed)
        print(f"Your seed is: {self.seed}")

        self.m_nNodes = nodes
        self.m_liveChance = liveChance

        self.m_map = [[Node() for row in range(self.m_nNodes)] for column in range(self.m_nNodes)]
        self.m_pxSize = None
        self.m_prevStep = None
        self.m_step = False
        self.SetupNodes()
        self.scrollDepth = 0.05

        self.m_isMoving = False

    def GetNeighbors(self, x: int, y: int, isAlive: bool) -> []:
        tempNeighbors = []
        for index in range(8):
            newX = x + self.XOFFSET[index]
            newY = y + self.YOFFSET[index]
            if (0 <= newX < self.m_nNodes) and (0 <= newY < self.m_nNodes):
                tempNeighbors.append((newX, newY))
                if isAlive:
                    self.m_map[newY][newX].liveNeighbors += 1
        return tempNeighbors

    def SetupNodes(self):
        al = 0
        for y, column in enumerate(self.m_map):
            for x, tempNode in enumerate(column):
                if random.randint(1, 101) <= self.m_liveChance:
                    al += 1

                    tempNode.isAlive = True

                tempNode.neighbors = self.GetNeighbors(x, y, tempNode.isAlive)

    def OnClientUpdate(self):

        if self.m_isMoving:
            tempMousePos = pygame.mouse.get_pos()
            diffX = tempMousePos[0] - self.m_initMousePos[0]
            diffY = tempMousePos[1] - self.m_initMousePos[1]
            self.m_cXOffset += diffX
            self.m_cYOffset += diffY
            self.m_initMousePos = tempMousePos

        if not self.m_step:
            return
        toAdd = []
        toRemove = []
        for y, column in enumerate(self.m_map):
            for x, tempNode in enumerate(column):
                if tempNode.isAlive:
                    if tempNode.liveNeighbors < 2 or tempNode.liveNeighbors > 3:
                        tempNode.isAlive = False
                        toRemove.extend(tempNode.neighbors)
                        continue
                    else:
                        tempNode.isAlive = True
                        continue
                else:
                    if tempNode.liveNeighbors == 3:
                        tempNode.isAlive = True
                        toAdd.extend(tempNode.neighbors)
                        continue

        for nodePosAdd in toAdd:
            self.m_map[nodePosAdd[1]][nodePosAdd[0]].liveNeighbors += 1
        for nodePosRemove in toRemove:
            self.m_map[nodePosRemove[1]][nodePosRemove[0]].liveNeighbors -= 1

        self.m_step = False

    def OnClientRender(self, surface):
        if not self.m_pxSize:
            self.m_pxSize = math.floor(min(surface.get_height(), surface.get_width()) / self.m_nNodes)
        surface.fill((255, 255, 255))

        self.m_cXStart = math.floor(((surface.get_width() - (self.m_pxSize*self.m_nNodes))/2))
        self.m_cYStart = math.floor((surface.get_height() - (self.m_pxSize * self.m_nNodes)) / 2)
        for y, column in enumerate(self.m_map):
            for x, tempNode in enumerate(column):
                tempX = self.m_cXOffset + self.m_cXStart + x*self.m_pxSize
                tempY = self.m_cYOffset + self.m_cYStart + y*self.m_pxSize
                if tempNode.isAlive:
                    pygame.draw.rect(surface, (0, 0, 0), (tempX, tempY,
                                                          self.m_pxSize, self.m_pxSize))
                    pygame.draw.rect(surface, (255, 255, 255), (tempX, tempY,
                                                                self.m_pxSize, self.m_pxSize), 2)
                else:
                    pygame.draw.rect(surface, (0, 0, 0), (tempX, tempY,
                                                          self.m_pxSize, self.m_pxSize), 2)

    def HandleInput(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                posX, posY = pygame.mouse.get_pos()
                nodeX = math.floor((posX-self.m_cXStart-self.m_cXOffset) / self.m_pxSize)
                nodeY = math.floor((posY-self.m_cYStart-self.m_cYOffset) / self.m_pxSize)
                print(nodeX, nodeY)
                try:
                    self.m_map[nodeY][nodeX].isAlive = not self.m_map[nodeY][nodeX].isAlive
                    for n in self.m_map[nodeY][nodeX].neighbors:
                        if self.m_map[nodeY][nodeX].isAlive:
                            self.m_map[n[1]][n[0]].liveNeighbors += 1
                        else:
                            self.m_map[n[1]][n[0]].liveNeighbors -= 1
                except IndexError:
                    self.m_step = True
            elif event.button == 5:
                self.m_pxSize *= (1 - self.scrollDepth)
            elif event.button == 4:
                self.m_pxSize *= (1 + self.scrollDepth)
            elif event.button == 3:
                c_mPos = pygame.mouse.get_pos()
                print("moving!")
                self.m_isMoving = True
                self.m_initMousePos = c_mPos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            print("not moving!")
            self.m_isMoving = False

