import curses
from time import sleep

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        horizontal = "-" * (self.life.cols + 2)
        vertical = "|"
        corner = "-"

        screen.addstr(0, 1, horizontal)
        screen.addstr(0, 0, corner)
        screen.addstr(0, self.life.cols + 1, corner)

        for i in range(self.life.rows):
            screen.addstr(i + 1, 0, vertical)
            screen.addstr(i + 1, self.life.cols + 1, vertical)

        screen.addstr(self.life.rows + 1, 0, corner)
        screen.addstr(self.life.rows + 1, 1, horizontal)
        screen.addstr(self.life.rows + 1, self.life.cols + 1, corner)

        screen.refresh()

    def draw_grid(self, screen) -> None:
        """Отобразить состояние клеток."""
        num_rows, num_cols = screen.getmaxyx()
        middle_col = num_cols // 2 - self.life.cols
        for row_index, row in enumerate(self.life.curr_generation):
            middle_row_position = num_rows // 2 - self.life.rows // 2 + row_index
            for col_index, value in enumerate(row):
                char = "★" if value else " "
                screen.addch(middle_row_position, col_index, char)

    def run(self) -> None:
        screen = curses.initscr()  # type: ignore
        self.draw_borders(screen)
        while True:
            self.draw_grid(screen)
            screen.refresh()
            sleep(1)
            self.life.step()


if __name__ == "__main__":
    game = GameOfLife(size=(20, 50), randomize=True, max_generations=100)
    console = Console(life=game)
    console.run()

curses.endwin()  # type: ignore
