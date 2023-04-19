import pathlib
import random
import typing as tp

import pygame
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        grid = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                cell = 0
                if randomize:
                    cell = random.randint(0, 1)
                row.append(cell)
            grid.append(row)
        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        neighbours = []
        positions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

        for pos in positions:
            x = cell[1] + pos[0]
            y = cell[0] + pos[1]
            if x < 0 or y < 0:
                continue
            if x > self.cols - 1 or y > self.rows - 1:
                continue
            val = self.curr_generation[y][x]
            neighbours.append(val)
        return neighbours

    def get_next_generation(self) -> Grid:
        new_grid = [row.copy() for row in self.curr_generation]
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                neighbours_list = self.get_neighbours((row_index, col_index))
                alive_neighbours = sum(neighbours_list)

                if not self.curr_generation[row_index][col_index] and alive_neighbours == 3:
                    new_grid[row_index][col_index] = 1
                elif self.curr_generation[row_index][col_index] and alive_neighbours not in (2, 3):
                    new_grid[row_index][col_index] = 0

        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        self.prev_generation, self.curr_generation = (
            self.curr_generation,
            self.get_next_generation(),
        )
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return self.generations >= self.max_generations  # type: ignore

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return self.prev_generation != self.curr_generation

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        grid_file = "\n".join("".join(str(value) for value in row) for row in self.curr_generation)
        filename.write_text(grid_file)


def from_file(filename: pathlib.Path) -> "GameOfLife":
    """
    Прочитать состояние клеток из указанного файла.
    """
    grid_file = filename.read_text()
    grid_array = [[int(value) for value in row] for row in grid_file.split()]
    return GameOfLife(grid=grid_array, size=(len(grid_array), len(grid_array[0])))  # type: ignore
