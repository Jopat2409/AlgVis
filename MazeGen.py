from dataclasses import dataclass
import random
import pygame
import math


@dataclass()
class PathNode:
    id: int
    isVisited = False
    neighbors = {}
    unvisitedNeighbors = {}
    walls = [True, True, True, True]


class MazeGen:

    def __init__(self, nodeCountX, nodeCountY):

        self.dirOffsets = None
        self.m_nodeCountX = nodeCountX
        self.m_nodeCountY = nodeCountY

        self.XOFFSET = [0, 1, 0, -1]
        self.YOFFSET = [-1, 0, 1, 0]
        self.m_playingField = []
        _id = 0
        # no I am not retarded, list comp would not work with ids
        for y in range(nodeCountY):
            tempRow = []
            for x in range(nodeCountX):
                a = PathNode(_id)
                a.walls = [True, True, True, True]
                tempRow.append(a)
                _id += 1
            self.m_playingField.append(tempRow)

        self.m_cNode = (random.randint(0, self.m_nodeCountX - 1), random.randint(0, self.m_nodeCountY - 1))
        print(self.m_cNode)
        self.m_nodeStack = [self.m_cNode]

        self.m_pxSize = None
        self.m_completedMaze = False

        self.m_shouldStep = True

        self.SetupNeighbors()

    def GetNodeBounds(self, x, y):
        if (0 <= y < self.m_nodeCountY) and (0 <= x < self.m_nodeCountX):
            return True
        return False

    def SetupNeighbors(self):

        for y, col in enumerate(self.m_playingField):
            for x, tNode in enumerate(col):
                neighbors = {}
                n2eighbors = {}
                for i in range(4):

                    newX = x + self.XOFFSET[i]
                    newY = y + self.YOFFSET[i]
                    if self.GetNodeBounds(newX, newY):
                        neighbors.update({(newX, newY): i})
                        n2eighbors.update({(newX, newY): i})
                tNode.unvisitedNeighbors = neighbors
                tNode.neighbors = n2eighbors

    def DrawWalls(self, surface, tempX, tempY):

        worldSpaceX = tempX * self.m_pxSize
        worldSpaceY = tempY * self.m_pxSize
        cNode = self.GetNodeFromPos((tempX, tempY))
        for direction, i in enumerate(cNode.walls):
            if i:
                tempOffsets = self.dirOffsets[direction]
                tStartPos = (worldSpaceX + tempOffsets[0][0], worldSpaceY + tempOffsets[0][1])
                tEndPos = (worldSpaceX + tempOffsets[1][0], worldSpaceY + tempOffsets[1][1])
                pygame.draw.line(surface, (0, 0, 0), tStartPos, tEndPos)

    def OnClientRender(self, surface):
        if not self.m_pxSize:
            self.m_pxSize = math.floor(min(surface.get_width() / self.m_nodeCountX,
                                           surface.get_height() / self.m_nodeCountY))
            self.dirOffsets = {0: [(0, 0), (self.m_pxSize, 0)], 1: [(self.m_pxSize, 0), (self.m_pxSize, self.m_pxSize)],
                               2: [(self.m_pxSize, self.m_pxSize), (0, self.m_pxSize)], 3: [(0, self.m_pxSize), (0, 0)]}

        surface.fill((255, 255, 255))
        for y, col in enumerate(self.m_playingField):
            for x, tNode in enumerate(col):
                tempX = self.m_pxSize * x
                tempY = self.m_pxSize * y

                if self.GetNodeFromPos((x, y)).isVisited:
                    if (x, y) in self.m_nodeStack:
                        pygame.draw.rect(surface, (244, 226, 198), (tempX, tempY, self.m_pxSize, self.m_pxSize))
                    else:
                        pygame.draw.rect(surface, (255, 255, 255), (tempX, tempY, self.m_pxSize, self.m_pxSize))
                try:
                    if (x, y) == self.m_nodeStack[-1]:
                        pygame.draw.rect(surface, (255, 0, 0), (tempX, tempY, self.m_pxSize, self.m_pxSize))
                except IndexError:
                    self.m_nodeStack.append(self.m_cNode)
                self.DrawWalls(surface, x, y)

    def GetNodeFromPos(self, pos):
        return self.m_playingField[pos[1]][pos[0]]

    def HandleInput(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.m_shouldStep = True

    def RemoveFromNeighbors(self, pos):

        tNode = self.GetNodeFromPos(pos)
        for bNode in tNode.neighbors:
            tempNode = self.GetNodeFromPos(bNode)
            try:
                tempNode.unvisitedNeighbors.pop(pos)
            except KeyError:
                pass




    def OnClientUpdate(self):
        if self.m_completedMaze or not self.m_shouldStep:
            return
        try:
            cNode = self.GetNodeFromPos(self.m_nodeStack[-1])
        except IndexError:
            self.m_completedMaze = True
            return
        if not cNode.isVisited:
            cNode.isVisited = True
        if len(cNode.unvisitedNeighbors) == 0:
            print("popped node!")
            self.RemoveFromNeighbors(self.m_nodeStack[-1])
            self.m_nodeStack.pop()
            self.m_shouldStep = True
            return
        else:
            tChoice = random.choice(list(cNode.unvisitedNeighbors.keys()))
            tNode = self.GetNodeFromPos(tChoice)

            tNode.walls[tNode.neighbors[self.m_nodeStack[-1]]] = False
            cNode.walls[cNode.unvisitedNeighbors[tChoice]] = False


            self.RemoveFromNeighbors(self.m_nodeStack[-1])
            cNode.unvisitedNeighbors.pop(tChoice)



            self.m_nodeStack.append(tChoice)
            self.m_shouldStep = True
            return
