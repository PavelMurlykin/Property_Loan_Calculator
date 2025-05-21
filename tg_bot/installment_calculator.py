from datetime import datetime
from dateutil.relativedelta import relativedelta

date_format = '%d.%m.%Y'

def get_parameters():
    """
    Функция для запроса параметров у пользователя и сохранения их в словарь.
    Возвращает словарь с параметрами:
    - cost: стоимость объекта
    - markup: удорожание в процентах
    - down_payment: первоначальный взнос в процентах
    - ddu_date: дата заключения ДДУ
    - commissioning_date: дата ввода в эксплуатацию
    - key_handover_date: дата выдачи ключей
    """
    params = {}
    params['cost'] = float(input('Введите стоимость объекта, руб.: '))
    params['markup'] = float(input('Введите удорожание, %: '))
    params['down_payment'] = float(input('Введите первоначальный взнос, %: '))
    ddu_date_str = input('Введите дату заключения ДДУ (ДД.ММ.ГГГГ): ')
    params['ddu_date'] = datetime.strptime(ddu_date_str, date_format)
    commissioning_date_str = input('Введите дату ввода объекта в эксплуатацию (ДД.ММ.ГГГГ): ')
    params['commissioning_date'] = datetime.strptime(commissioning_date_str, date_format)
    key_handover_str = input('Введите дату выдачи ключей (ДД.ММ.ГГГГ): ')
    params['key_handover_date'] = datetime.strptime(key_handover_str, date_format)
    return params


def calculate_installment(params):
    """
    Функция расчета рассрочки. Принимает параметры, возвращает словарь с результатами:
    - full_cost: полная стоимость с учетом удорожания
    - payments: список словарей с датой и суммой платежей
    """
    result = {}
    # Рассчитываем полную стоимость с учетом удорожания
    result['full_cost'] = params['cost'] * (1 + params['markup'] / 100)
    # Рассчитываем сумму первоначального взноса
    initial_payment = (params['down_payment'] / 100) * result['full_cost']
    # Остаток после первого взноса делится на 4 равные части
    remaining = result['full_cost'] - initial_payment
    part_payment = remaining / 4
    # Создаем список для хранения платежей
    payments = []
    # Первый платеж (дата заключения ДДУ)
    payments.append({'date': params['ddu_date'], 'amount': initial_payment})
    # Второй платеж (+12 месяцев к дате ДДУ)
    payments.append({
        'date': params['ddu_date'] + relativedelta(months=12),
        'amount': part_payment
    })
    # Третий платеж (+24 месяца к дате ДДУ)
    payments.append({
        'date': params['ddu_date'] + relativedelta(months=24),
        'amount': part_payment
    })
    # Четвертый платеж (за 3 месяца до ввода в эксплуатацию)
    payments.append({
        'date': params['commissioning_date'] - relativedelta(months=3),
        'amount': part_payment
    })
    # Пятый платеж (+3 месяца после выдачи ключей)
    payments.append({
        'date': params['key_handover_date'] + relativedelta(months=3),
        'amount': part_payment
    })
    result['payments'] = payments
    return result


def print_results(result):
    """
    Функция вывода результатов расчета.
    """
    # Полная стоимость
    print(f'Полная стоимость объекта с учетом удорожания: {result["full_cost"]:.2f} руб.')
    # Первый взнос
    # first_payment = result['payments'][0]
    # print(
    #     f'Дата и сумма первого взноса: {first_payment["date"].strftime("%Y-%m-%d")} - {first_payment["amount"]:.2f} руб.')
    # Все платежи
    print('Даты и суммы всех платежей:')
    for idx, payment in enumerate(result['payments'], 1):
        print(f'{idx}. {payment["date"].strftime("%Y-%m-%d")} - {payment["amount"]:.2f} руб.')


def main():
    # Получаем параметры
    params = get_parameters()
    # Производим расчет
    result = calculate_installment(params)
    # Выводим результат
    print_results(result)


if __name__ == '__main__':
    main()
