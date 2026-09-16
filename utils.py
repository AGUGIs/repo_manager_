"""Вспомогательные функции ввода с обработкой ошибок."""

from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число.

    При некорректном вводе запрос повторяется.
    """
    while True:
        raw = input(prompt)
        try:
            return int(raw)
        except ValueError:
            print('Введите целое число.')


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ.

    При некорректном формате запрос повторяется.
    """
    while True:
        raw = input(prompt)
        try:
            return datetime.strptime(raw, '%d.%m.%Y').date()
        except ValueError:
            print('Введите дату в формате ДД.ММ.ГГГГ.')


def input_bool(prompt: str) -> bool:
    """Запросить ответ да/нет и вернуть bool."""
    while True:
        raw = input(prompt).strip().lower()
        if raw in {'да', 'yes', 'y', '1'}:
            return True
        if raw in {'нет', 'no', 'n', '0'}:
            return False
        print('Введите да или нет.')
