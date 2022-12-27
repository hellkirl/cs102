from copy import deepcopy
from random import choice, randint
from typing import List, Optional, Tuple, Union

import pandas as pd  # type: ignore


def create_grid(rows: int = 15, cols: int = 15) -> List[List[Union[str, int]]]:
    return [["■"] * cols for _ in range(rows)]


def remove_wall(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> List[List[Union[str, int]]]:
    """

    :param grid:
    :param coord:
    :return:
    """
    i, j = coord[0], coord[1]
    direction = choice((True, False))
    if direction:
        if i == 1 and j != len(grid[0]) - 2:
            grid[i][j + 1] = " "
        else:
            grid[i - 1][j] = " "
    else:
        if j == len(grid[0]) - 2 and i != 1:
            grid[i - 1][j] = " "
        else:
            grid[i][j + 1] = " "
    return grid


def bin_tree_maze(rows: int = 15, cols: int = 15, random_exit: bool = True) -> List[List[Union[str, int]]]:
    """

    :param rows:
    :param cols:
    :param random_exit:
    :return:
    """

    grid = create_grid(rows, cols)
    empty_cells = []
    for i, row in enumerate(grid):
        for j, x in enumerate(row):
            if i % 2 == 1 and j % 2 == 1:
                grid[i][j] = " "
                empty_cells.append((i, j))

    for i in empty_cells:  # type: ignore
        cell_one = i[0]  # type: ignore
        cell_two = i[1]  # type: ignore
        remove_wall(grid, (cell_one, cell_two))
    if grid[1][len(grid) - 1] != "■":
        grid[1][len(grid) - 1] = "■"
    if grid[0][len(grid[0]) - 2] != "■":
        grid[0][len(grid[0]) - 2] = "■"

    # 1. выбрать любую клетку
    # 2. выбрать направление: наверх или направо.
    # Если в выбранном направлении следующая клетка лежит за границами поля,
    # выбрать второе возможное направление
    # 3. перейти в следующую клетку, сносим между клетками стену
    # 4. повторять 2-3 до тех пор, пока не будут пройдены все клетки

    # генерация входа и выхода
    if random_exit:
        x_in, x_out = randint(0, rows - 1), randint(0, rows - 1)
        y_in = randint(0, cols - 1) if x_in in (0, rows - 1) else choice((0, cols - 1))
        y_out = randint(0, cols - 1) if x_out in (0, rows - 1) else choice((0, cols - 1))
    else:
        x_in, y_in = 0, cols - 2
        x_out, y_out = rows - 1, 1

    grid[x_in][y_in], grid[x_out][y_out] = "X", "X"

    return grid


def get_exits(grid: List[List[Union[str, int]]]) -> List[Tuple[int, int]]:
    """

    :param grid:
    :return:
    """
    return [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == "X"]


def make_step(grid: List[List[Union[str, int]]], k: int) -> List[List[Union[str, int]]]:
    """

    :param grid:
    :param k:
    :return:
    """

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == k:
                if i + 1 <= len(grid) - 1:
                    if grid[i + 1][j] == 0:
                        grid[i + 1][j] = k + 1
                if i - 1 >= 0:
                    if grid[i - 1][j] == 0:
                        grid[i - 1][j] = k + 1
                if j + 1 <= len(grid[0]) - 1:
                    if grid[i][j + 1] == 0:
                        grid[i][j + 1] = k + 1
                if j - 1 >= 0:
                    if grid[i][j - 1] == 0:
                        grid[i][j - 1] = k + 1

    return grid


def shortest_path(
    grid: List[List[Union[str, int]]], exit_coord: Tuple[int, int]
) -> Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]:
    """

    :param grid:
    :param exit_coord:
    :return:
    """
    y, x = exit_coord[0], exit_coord[1]
    path = [(y, x)]
    k = int(grid[y][x])
    while k != 1:
        if y - 1 >= 0:
            if grid[y - 1][x] == k - 1:
                path.append((y - 1, x))
                k -= 1
                y -= 1
        if y + 1 <= len(grid) - 1:
            if grid[y + 1][x] == k - 1:
                path.append((y + 1, x))
                k -= 1
                y += 1
        if x - 1 >= 0:
            if grid[y][x - 1] == k - 1:
                path.append((y, x - 1))
                k -= 1
                x -= 1
        if x + 1 <= len(grid[0]) - 1:
            if grid[y][x + 1] == k - 1:
                path.append((y, x + 1))
                k -= 1
                x += 1
    if len(path) != grid[exit_coord[0]][exit_coord[1]]:
        grid[path[-2][0]][path[-2][1]] = " "
        shortest_path(grid, exit_coord)

    return path


def encircled_exit(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> bool:
    """

    :param grid:
    :param coord:
    :return:
    """
    square = 0
    empty = 0
    if grid[coord[0]][coord[1]] == " ":
        return False
    if coord[1] + 1 < len(grid[0]):
        if grid[coord[0]][coord[1] + 1] == " ":
            empty += 1
        else:
            square += 1

    if coord[1] - 1 > -1:
        if grid[coord[0]][coord[1] - 1] == " ":
            empty += 1
        else:
            square += 1

    if coord[0] + 1 < len(grid):
        if grid[coord[0] + 1][coord[1]] == " ":
            empty += 1
        else:
            square += 1

    if coord[0] - 1 > -1:
        if grid[coord[0] - 1][coord[1]] == " ":
            empty += 1
        else:
            square += 1

    return not (square == 2 and empty > 0)


def solve_maze(
    grid: List[List[Union[str, int]]]
) -> Tuple[List[List[Union[str, int]]], Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]]:
    """

    :param grid:
    :return:
    """
    counter = 0
    if len(get_exits(grid)) == 1:
        return grid, get_exits(grid)[0]

    enter = get_exits(grid)[0]
    exit = get_exits(grid)[1]

    if encircled_exit(grid, enter) or encircled_exit(grid, exit):
        return grid, None
    grid[enter[0]][enter[1]] = 1
    grid[exit[0]][exit[1]] = 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == " ":
                grid[i][j] = 0

    while grid[exit[0]][exit[1]] == 0:
        counter += 1
        make_step(grid, counter)

    return grid, shortest_path(grid, exit)


def add_path_to_grid(
    grid: List[List[Union[str, int]]], path: Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]
) -> List[List[Union[str, int]]]:
    """

    :param grid:
    :param path:
    :return:
    """
    if path:
        for i, row in enumerate(grid):
            for j, _ in enumerate(row):
                if (i, j) in path:
                    grid[i][j] = "X"
    return grid


if __name__ == "__main__":
    GRID = bin_tree_maze(15, 15)
    EMPTY_GRID = deepcopy(GRID)
    print(pd.DataFrame(GRID))
    _, PATH = solve_maze(GRID)
    MAZE = add_path_to_grid(EMPTY_GRID, PATH)
    print(pd.DataFrame(MAZE))
