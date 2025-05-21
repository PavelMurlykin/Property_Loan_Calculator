# Импорт модуля datetime для работы с датами
from datetime import datetime


def input_parameters():
    """
    Запрашивает у пользователя параметры и сохраняет их в словарь.
    Возвращает словарь с параметрами.
    """
    params = {}
    # Ввод основных параметров
    params['cost'] = float(input('Введите стоимость объекта, руб.: '))
    params['markup'] = float(input('Введите удорожание, %: '))
    params['initial_percent'] = float(input('Введите первоначальный взнос, %: '))
    params['loan_term_years'] = int(input('Введите срок кредита, лет: '))
    params['num_tranches'] = int(input('Введите количество траншей: '))
    params['tranches'] = []

    # Ввод данных для каждого транша
    for i in range(params['num_tranches']):
        tranche = {}
        print(f'Транш {i + 1}:')
        tranche['date'] = input('Дата транша (формат ГГГГ-ММ): ')
        # Для последнего транша процент не запрашивается
        if i < params['num_tranches'] - 1:
            tranche['percent'] = float(input('Сумма транша, % от стоимости: '))
        tranche['rate'] = float(input('Годовая ставка, %: '))
        params['tranches'].append(tranche)

    return params


def calculate_mortgage(params):
    """
    Выполняет расчет ипотеки на основе переданных параметров.
    Возвращает словарь с результатами расчета.
    """
    # Расчет полной стоимости с учетом удорожания
    full_cost = params['cost'] * (1 + params['markup'] / 100)
    # Расчет суммы первоначального взноса
    initial_payment = full_cost * params['initial_percent'] / 100
    # Сумма кредита (полная стоимость минус первоначальный взнос)
    loan_amount = full_cost - initial_payment

    # Сортировка траншей по дате
    sorted_tranches = sorted(
        params['tranches'],
        key=lambda x: datetime.strptime(x['date'], '%Y-%m')
    )
    # Список сумм траншей
    tranche_amounts = []

    # Расчет сумм траншей (кроме последнего)
    for i in range(params['num_tranches'] - 1):
        percent = sorted_tranches[i]['percent']
        tranche_amount = full_cost * percent / 100
        tranche_amounts.append(tranche_amount)

    # Расчет суммы последнего транша (остаток)
    last_tranche = loan_amount - sum(tranche_amounts)
    tranche_amounts.append(last_tranche)

    # Определение общей длительности кредита в месяцах
    loan_term_months = params['loan_term_years'] * 12
    # Дата начала кредита (дата первого транша)
    start_date = sorted_tranches[0]['date']
    start_date_dt = datetime.strptime(start_date, '%Y-%m')

    results = {
        'full_cost': full_cost,
        'initial_payment': {
            'amount': initial_payment,
            'date': start_date  # Дата первого транша считается датой первого взноса
        },
        'tranches': []
    }

    total_issued = 0  # Общая сумма выданных траншей

    # Расчет данных для каждого транша
    for i in range(params['num_tranches']):
        tranche = sorted_tranches[i]
        amount = tranche_amounts[i]
        date = tranche['date']
        rate = tranche['rate']

        # Расчет разницы в месяцах между датой транша и началом кредита
        current_date_dt = datetime.strptime(date, '%Y-%m')
        delta_months = (current_date_dt.year - start_date_dt.year) * 12 + (current_date_dt.month - start_date_dt.month)
        # Количество платежей для транша
        num_payments = max(loan_term_months - delta_months, 0)

        # Расчет ежемесячного платежа
        monthly_rate = rate / 100 / 12
        if num_payments == 0 or monthly_rate == 0:
            monthly_payment = 0.0
        else:
            monthly_payment = (amount * monthly_rate) / (1 - (1 + monthly_rate) ** -num_payments)

        # Обновление общей выданной суммы
        total_issued += amount

        # Сохранение результатов транша
        results['tranches'].append({
            'date': date,
            'num_payments': num_payments,
            'monthly_payment': monthly_payment,
            'total_loan': total_issued
        })

    return results


def print_results(results):
    """Выводит результаты расчета на экран."""
    print(f'\nПолная стоимость объекта: {results["full_cost"]:.2f} руб.')
    print(f'Дата первого взноса: {results["initial_payment"]["date"]}')
    print(f'Сумма первого взноса: {results["initial_payment"]["amount"]:.2f} руб.')

    # Вывод данных по каждому траншу
    for i, tranche in enumerate(results['tranches']):
        print(f'\nТранш {i + 1}:')
        print(f'Дата: {tranche["date"]}')
        print(f'Платежей: {tranche["num_payments"]}')
        print(f'Ежемесячный платеж: {tranche["monthly_payment"]:.2f} руб.')
        print(f'Общая сумма кредита: {tranche["total_loan"]:.2f} руб.')


def main():
    """Основная функция программы."""
    params = input_parameters()
    results = calculate_mortgage(params)
    print_results(results)


if __name__ == '__main__':
    main()
