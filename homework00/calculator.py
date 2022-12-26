import math
import typing as tp


def convert(num: int, base: int) -> int:
    """Перевод числа из десятичной системы в другую с основанием до 10"""
    res = 0
    n = 1
    while num > 0:
        res += (num % base) * n
        n *= 10
        num //= base
    return res


def calc(num_1: float, num_2: float, command: str) -> tp.Union[float, str]:
    """Базовые операции с двумя числами"""
    if command == "+":
        return num_1 + num_2
    if command == "-":
        return num_1 - num_2
    if command == "/":
        try:
            return num_1 / num_2
        except Exception:
            return "На 0 делить нельзя!"
    if command == "^":
        return num_1**num_2
    if command == "*":
        return num_1 * num_2
    else:
        return f"Неизвестный оператор: {command!r}."


def calc_one_num(num: float, command: str) -> tp.Union[float, str]:
    """Операции с одним числом"""
    if command == "^2":
        return num**2
    if command == "tan":
        return math.tan(num)
    if command == "sin":
        return math.sin(num)
    if command == "cos":
        return math.cos(num)
    if command == "log":
        try:
            return math.log10(num)
        except Exception:
            return "Нельзя найти логарифм 0!"
    if command == "ln":
        try:
            return math.log(num)
        except Exception:
            return "Нельзя найти логарифм 0!"
    if command == "sqrt":
        try:
            return math.sqrt(num)
        except Exception:
            return "Нет действительных корней!"
    else:
        return f"Неизвестный оператор {command!r}."


if __name__ == "__main__":
    while True:
        COMMAND = input("Введите оперцию > ")
        if COMMAND.isdigit() and int(COMMAND) == 0:
            break
        if COMMAND in ["+", "-", "/", "*", "^"]:
            NUM_1 = float(input("Первое число > "))
            NUM_2 = float(input("Второе число > "))
            print(calc(NUM_1, NUM_2, COMMAND))
        if COMMAND.lower() in ["^2", "tan", "cos", "sin", "log", "ln", "sqrt"]:
            try:
                NUM = float(input("Число > "))
                print(calc_one_num(NUM, COMMAND.lower()))
            except Exception:
                print("Неверный ввод")
        if COMMAND.lower() == "convert":
            try:
                NUM = int(input("Число > "))
                BASE = int(input("Система счисления > "))
                print(convert(NUM, BASE))
            except Exception:
                print("Неверный ввод")
