"""Проверка целочисленных параметров GET до обращения к SQLite."""


def integer_parameter(value, *, minimum=0):
    """Ограничить число: исключить отрицательные значения и переполнение."""
    if not value.isascii() or not value.isdecimal() or len(value) > 7:
        raise ValueError('Введите целое число от '
                         f'{minimum} до 1000000.')
    result = int(value)
    if not minimum <= result <= 1000000:
        raise ValueError(f'Введите целое число от {minimum} до 1000000.')
    return result
