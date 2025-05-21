from datetime import datetime
from dateutil.relativedelta import relativedelta

# date_format = '%Y-%m-%d'
date_format = '%d.%m.%Y'


def validate_positive_float(value: str, name: str) -> float:
    """Проверяет, что введенное значение является положительным числом."""
    try:
        num = float(value)
        if num <= 0:
            raise ValueError(f'Параметр "{name}" должен быть больше нуля.')
        return num
    except ValueError:
        raise ValueError(f'Некорректное значение параметра "{name}". Введите число.')


def validate_date(date_str: str) -> datetime.date:
    """Проверяет корректность формата даты (ДД.ММ.ГГГГ)."""
    try:
        return datetime.strptime(date_str, date_format).date()
    except ValueError:
        raise ValueError('Неверный формат даты. Используйте ДД.ММ.ГГГГ.')


def validate_percent(value: str, name: str) -> float:
    """Проверяет, что значение процента находится в диапазоне 0-100."""
    percent = validate_positive_float(value, name)
    if percent > 100:
        raise ValueError(f'{name} не может превышать 100%.')
    return percent


def validate_yes_no(value: str) -> bool:
    """Проверяет, что введено 'Да' или 'Нет'."""
    cleaned_value = value.strip().lower()
    if cleaned_value not in ('да', 'нет'):
        raise ValueError('Ответ должен быть "да" или "нет".')
    return cleaned_value == 'да'


def get_input(prompt: str, validation_function, **kwargs):
    """Циклически запрашивает ввод, пока не будет получено корректное значение."""
    while True:
        try:
            user_input = input(prompt)
            return validation_function(user_input, **kwargs) if kwargs else validation_function(user_input)
        except ValueError as err:
            print(f"❌ Ошибка: {err}\n")


def calculate_annuity(loan_amount: float, months: int, monthly_rate: float) -> float:
    """
    Рассчитывает аннуитетный платеж.
    Платеж = (Сумма * Месячная_ставка) / (1 - (1 + Месячная_ставка)^-Количество_платежей)
    """
    if monthly_rate == 0:
        return loan_amount / months
    annuity_factor = (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return loan_amount * annuity_factor


# def calculate_mortgage(params: dict) -> dict:
def calculate_mortgage():
    """
    Ипотечный калькулятор для расчета параметров кредита.
    Запрашивает у пользователя входные данные и выводит результаты расчетов.
    """
    print('Введите параметры расчета ипотеки:')

    # Основные параметры
    object_cost = get_input('Введите стоимость объекта (руб.): ',
                            lambda vld: validate_positive_float(vld, 'Стоимость объекта'))
    down_payment_percent = get_input('Введите первоначальный взнос (%): ',
                                     lambda vld: validate_percent(vld, 'Первоначальный взнос'))
    start_date = get_input('Введите дату первоначального взноса (ДД.ММ.ГГГГ): ', validate_date)
    loan_term_years = get_input('Введите срок кредита (лет): ',
                                lambda vld: int(validate_positive_float(vld, 'Срок кредита')))
    annual_rate = get_input('Введите годовую ставку (%): ',
                            lambda vld: validate_positive_float(vld, 'Годовая ставка'))
    has_grace_period = get_input('Есть льготный период? (да/нет): ', validate_yes_no)

    # Параметры льготного периода
    grace_years = 0
    grace_rate = 0.0
    if has_grace_period:
        grace_years = get_input(
            'Введите срок льготного периода (лет): ',
            lambda vld: int(validate_positive_float(vld, 'Срок льготного периода'))
        )

        while grace_years >= loan_term_years:
            print('❌ Срок льготного периода должен быть меньше общего срока.')
            grace_years = get_input(
                'Введите срок льготного периода (лет): ',
                lambda vld: int(validate_positive_float(vld, 'Срок льготного периода'))
            )

        grace_rate = get_input(
            'Введите годовую ставку в льготный период (%): ',
            lambda vld: validate_positive_float(vld, 'Льготная ставка')
        )

    # Расчет базовых параметров
    down_payment = object_cost * (down_payment_percent / 100)  # Первоначальный взнос, руб.
    loan_amount = object_cost - down_payment  # Тело кредита, руб.
    total_payments = loan_term_years * 12  # Общее количество платежей (месяцев)

    # Расчет параметров льготного периода
    grace_payments = grace_years * 12 if has_grace_period else 0  # Количество льготных платежей (месяцев)
    main_payments = total_payments - grace_payments  # Количество основных платежей (месяцев)
    grace_monthly_payment = 0.0  # Ежемесячный платеж в льготный период, руб.
    remaining_loan = loan_amount  # Остаток тела кредита, руб.

    if has_grace_period:
        # Ежемесячный платеж в льготный период
        grace_monthly_rate = (grace_rate / 100) / 12
        grace_monthly_payment = calculate_annuity(loan_amount, total_payments, grace_monthly_rate)

        # Пересчет остатка после льготного периода
        remaining_loan = loan_amount * (1 + grace_monthly_rate) ** grace_payments - grace_monthly_payment * (
                ((1 + grace_monthly_rate) ** grace_payments - 1) / grace_monthly_rate)
        remaining_loan = max(remaining_loan, 0.0)  # Защита от отрицательных значений

    # Расчет платежей для основного периода
    main_monthly_rate = (annual_rate / 100) / 12
    main_monthly_payment = calculate_annuity(remaining_loan, main_payments,
                                             main_monthly_rate) if main_payments > 0 else 0.0

    # Общие выплаты
    total_grace_payment = grace_monthly_payment * grace_payments if has_grace_period else 0.0
    total_main_payment = main_monthly_payment * main_payments
    overpayment = (total_grace_payment + total_main_payment) - loan_amount

    # Даты платежей
    grace_end_date = start_date + relativedelta(months=+grace_payments) if has_grace_period else start_date
    final_end_date = grace_end_date + relativedelta(months=+main_payments)

    # Вывод результатов
    print('\nРезультаты расчета:')

    if has_grace_period:
        print(f'\nЛьготный период:')
        print(f'1. Число платежей: {grace_payments}')
        print(f'2. Дата окончания льготного периода: {grace_end_date.strftime(date_format)}')
        print(f'3. Сумма ежемесячного платежа: {grace_monthly_payment:.2f} руб.')
        print(f'4. Остаток долга после льготного периода: {remaining_loan:.2f} руб.')
        print(f'\nОсновной период:')

    print(f'1. Число платежей: {main_payments}')
    print(f'2. Дата последнего платежа: {final_end_date.strftime(date_format)}')
    print(f'3. Сумма ежемесячного платежа: {main_monthly_payment:.2f} руб.')
    print(f'4. Сумма кредита: {loan_amount:.2f} руб.')
    print(f'5. Сумма переплат: {overpayment:.2f} руб.')

    # return {
    #     'grace_payments': grace_payments,
    #     'grace_end_date': grace_end_date.strftime(date_format),
    #     'grace_monthly_payment': grace_monthly_payment,
    #
    #     'main_payments': main_payments,
    #     'final_end_date': final_end_date.strftime(date_format),
    #     'main_monthly_payment': main_monthly_payment,
    #     'loan_amount': loan_amount,
    #     'overpayment': overpayment
    # }


# Запуск калькулятора
if __name__ == '__main__':
    calculate_mortgage()
