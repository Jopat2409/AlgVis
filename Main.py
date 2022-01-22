import pygame
import sys
import GameOfLife
import MazeGen
import time


class ProgramMain:

    def __init__(self, width=640, height=480, title="Program"):
        pygame.init()
        pygame.font.init()
        self.m_surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        self.m_cMode = MazeGen.MazeGen(50, 50)

        self.Run()

    def CallbackSwitchState(self, state):

        self.m_cMode = state

    def Run(self):
        isRunning = True
        while isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isRunning = False
                else:
                    self.m_cMode.HandleInput(event)
            self.m_cMode.OnClientUpdate()
            self.m_cMode.OnClientRender(self.m_surface)


            pygame.display.update()

        pygame.quit()
        sys.exit(0)


r = ProgramMain(1280, 960)
