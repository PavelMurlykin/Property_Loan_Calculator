import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
)
from config import BOT_TOKEN
from mortgage_calculator import calculate_mortgage

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
(
    INPUT_OBJECT_COST,
    INPUT_DOWN_PAYMENT,
    INPUT_START_DATE,
    INPUT_LOAN_TERM,
    INPUT_RATE,
    INPUT_GRACE_PERIOD,
) = range(6)


def start(update: Update) -> int:
    user = update.message.from_user
    update.message.reply_text(
        f'Привет, {user.first_name}! Я помогу рассчитать ипотеку.\n'
        'Введите стоимость объекта (руб.):'
    )
    return INPUT_OBJECT_COST


def input_object_cost(update: Update, context: CallbackContext) -> int:
    try:
        cost = float(update.message.text)
        context.user_data['object_cost'] = cost
        update.message.reply_text('Введите первоначальный взнос (%):')
        return INPUT_DOWN_PAYMENT
    except ValueError:
        update.message.reply_text('❌ Ошибка! Введите число.')
        return INPUT_OBJECT_COST


# ... аналогичные обработчики для других шагов ...

def calculate(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    result = calculate_mortgage(user_data)

    response = (
        '📊 Результаты расчета:\n'
        f'▪ Ежемесячный платеж: {result['monthly_payment']:.2f} руб.\n'
        f'▪ Общая переплата: {result['total_overpayment']:.2f} руб.\n'
        # ... другие параметры ...
    )

    update.message.reply_text(response)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Расчет отменен.')
    return ConversationHandler.END


def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INPUT_OBJECT_COST: [MessageHandler(filters.text & ~filters.command, input_object_cost)],
            INPUT_DOWN_PAYMENT: [MessageHandler(filters.text & ~filters.command, input_down_payment)],
            # ... другие состояния ...
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
