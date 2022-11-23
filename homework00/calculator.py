import math
import typing as tp


def calc(num_1: float, num_2: float, command: str) -> tp.Union[float, str]:
    if command == "+":
        return num_1 + num_2
    if command == "-":
        return num_1 - num_2
    if command == "/":
        return num_1 / num_2
    if command == "*":
        return num_1 * num_2
    if command == "^":
        return num_1**num_2
    else:
        return f"Неизвестный оператор: {command!r}."


def calc_onenum(num_1: float, command: str) -> tp.Union[float, str]:
    if command == "^2":
        return num_1**2
    if command == "cos":
        return math.cos(num_1)
    if command == "sin":
        return math.sin(num_1)
    if command == "tg":
        return math.tan(num_1)
    if command == "log":
        return math.log(num_1)
    if command == "log10":
        return math.log10(num_1)
    else:
        return f"Неизвестный оператор: {command!r}."


def match_case_calc_one(num_1: float, command: str) -> tp.Union[float, str]:
    match command:
        case "cos":
            return math.cos(num_1)
        case "sin":
            return math.sin(num_1)
        case "tg":
            return math.tan(num_1)
        case "log":
            return math.log(num_1)
        case "log10":
            return math.log10(num_1)
        case _:
            return f"Неизвестный оператор: {command!r}."


def match_case_calc_two(num_1: float, num_2: float, command: str) -> tp.Union[float, str]:
    match command:
        case "+":
            return num_1 + num_2
        case "-":
            return num_1 - num_2
        case "/":
            return num_1 / num_2
        case "*":
            return num_1 * num_2
        case "^":
            return num_1**num_2
        case "^2":
            return num_1**2
        case _:
            return f"Неизвестный оператор: {command!r}."


if __name__ == "__main__":
    while True:
        COMMAND = input("Введите оперцию > ")
        if COMMAND.isdigit() and int(COMMAND) == 0:
            break
        if COMMAND in ["+", "-", "/", "*", "^", "^2", "(", ")"]:
            NUM_1 = float(input("Первое число > "))
            NUM_2 = float(input("Второе число > "))
            print(match_case_calc_two(NUM_1, NUM_2, COMMAND))
        elif COMMAND in ["cos", "tg", "sin", "log", "log10"]:
            NUM_1 = float(input("Первое число > "))
            print(match_case_calc_one(NUM_1, COMMAND))
