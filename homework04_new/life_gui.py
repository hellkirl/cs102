from typing import Tuple  # type: ignore

import pygame  # type: ignore
from life import GameOfLife  # type: ignore
from pygame.locals import *  # type: ignore
from ui import UI  # type: ignore


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.life = life
        self.cell_size = cell_size
        self.width = self.life.cols * cell_size
        self.height = self.life.rows * cell_size
        self.speed = speed
        self.screen_size = self.width, self.height
        self.screen = pygame.display.set_mode(self.screen_size)

    def draw_lines(self) -> None:
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y), (self.width, y))

    def draw_grid(self) -> None:
        grid = self.life.curr_generation
        for row in range(self.life.rows):
            for col in range(self.life.cols):
                if grid[row][col] != 1:
                    color = "white"
                else:
                    color = "black"

                pygame.draw.rect(
                    self.screen,
                    pygame.Color(color),
                    (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size),
                )

    def run(self) -> None:
        """Запустить игру"""
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        # Создание списка клеток

        running = True
        pause = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pause = not pause
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_x, click_y = pygame.mouse.get_pos()
                    y, x = click_x // self.cell_size, click_y // self.cell_size
                    if self.life.curr_generation[x][y]:
                        self.life.curr_generation[x][y] = 0
                    else:
                        self.life.curr_generation[x][y] = 1

            if not pause:
                self.life.step()
            if not (not self.life.is_max_generations_exceeded and self.life.is_changing):
                pause = True

            self.draw_grid()
            self.draw_lines()
            pygame.display.flip()
            clock.tick(self.speed)

        pygame.quit()


if __name__ == "__main__":
    life = GameOfLife((90, 90), max_generations=10000)
    ui = GUI(life, 5)
    ui.run()
