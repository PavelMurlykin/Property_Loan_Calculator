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


# Функция для определения квартала
def get_quarter(date):
    return date.year, (date.month - 1) // 3 + 1


def calculate_installment(params):
    """
    Функция расчета рассрочки. Принимает параметры, возвращает словарь с результатами:
    - full_cost: полная стоимость с учетом удорожания
    - payments: список словарей с датой и суммой платежей
    """
    result = {}
    # Расчет полной стоимости
    result['full_cost'] = params['cost'] * (1 + params['markup'] / 100)
    initial_payment = (params['down_payment'] / 100) * result['full_cost']
    remaining = result['full_cost'] - initial_payment
    part_payment = remaining / 4  # Каждая часть из 4-х оставшихся платежей

    payments = []
    # Первый платеж (дата ДДУ)
    payments.append({'date': params['ddu_date'], 'amount': initial_payment})

    commissioning_yr_qr = get_quarter(params['commissioning_date'])

    # Определение условий для платежей
    if commissioning_yr_qr >= (2027, 3):
        # Условие 1: все платежи по стандартному графику
        payments.append({'date': params['ddu_date'] + relativedelta(months=12), 'amount': part_payment})
        payments.append({'date': params['ddu_date'] + relativedelta(months=24), 'amount': part_payment})
        payments.append({'date': params['commissioning_date'] - relativedelta(months=3), 'amount': part_payment})
    elif (2026, 3) <= commissioning_yr_qr <= (2027, 2):
        # Условие 2: объединение 3-го и 4-го платежей
        payments.append({'date': params['ddu_date'] + relativedelta(months=12), 'amount': part_payment})
        merged_3_4 = {
            'date': params['commissioning_date'] - relativedelta(months=3),
            'amount': part_payment * 2
        }
        payments.append(merged_3_4)
    else:
        # Условие 3: объединение 2-го, 3-го и 4-го платежей
        merged_2_3_4 = {
            'date': params['commissioning_date'] - relativedelta(months=3),
            'amount': part_payment * 3
        }
        payments.append(merged_2_3_4)

    # Пятый платеж (всегда через 3 месяца после выдачи ключей)
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
    print(f'\nПолная стоимость объекта с учетом удорожания: {result["full_cost"]:.2f} руб.')
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
