def _check_borders(
        number: float | int,
        name: str,
        lower_border: float | int | None,
        top_border: float | int | None
) -> None:
    """Внутренняя функция для проверки граничных значений."""
    if lower_border is not None and top_border is not None:
        if lower_border > top_border:
            raise ValueError(f'Нижний предел "{name}" должен быть меньше верхнего.')
        if not (lower_border <= number <= top_border):
            raise ValueError(f'Параметр "{name}" должен находиться в диапазоне от {lower_border} до {top_border}.')

    elif lower_border is not None and number < lower_border:
        raise ValueError(f'Параметр "{name}" должен быть не меньше {lower_border}.')

    elif top_border is not None and number > top_border:
        raise ValueError(f'Параметр "{name}" должен быть не больше {top_border}.')


def validate_float(
        value: str,
        name: str,
        lower_border: float | None = None,
        upper_border: float | None = None
) -> float:
    """
    Проверяет, что введенное значение является числом.
    Учитывает верхний и нижний диапазон, в котором должно находиться число.
    """
    try:
        number = float(value)
    except ValueError:
        raise ValueError(f'Некорректное значение "{name}". Введите число.')

    _check_borders(number, name, lower_border, upper_border)

    return number


def validate_int(
        value: str,
        name: str,
        lower_border: int | None = None,
        upper_border: int | None = None
) -> int:
    """
    Проверяет, что введенное значение является целым числом.
    Учитывает верхний и нижний диапазон, в котором должно находиться число.
    """
    try:
        number = int(value)
    except ValueError:
        try:
            float_num = float(value)
            if not float_num.is_integer():
                raise ValueError(f'Некорректное значение "{name}". Введите целое число.')
            number = int(float_num)
        except (ValueError, TypeError):
            raise ValueError(f'Некорректное значение "{name}". Введите целое число.')

    _check_borders(number, name, lower_border, upper_border)

    return number


def get_input(prompt: str, validation_function, **kwargs):
    """Циклически запрашивает ввод, пока не будет получено корректное значение."""
    while True:
        try:
            user_input = input(prompt)
            return validation_function(user_input, **kwargs) if kwargs else validation_function(user_input)
        except ValueError as err:
            print(f"❌ Ошибка: {err}\n")


if __name__ == '__main__':
    print('Введите параметры расчета:')
    get_input('Стоимость объекта (руб.): ',
              lambda value: validate_float(value, 'Стоимость объекта', 0))
    get_input('Срок кредита (лет): ',
              lambda value: validate_int(value, 'Срок кредита', 0, 30))
