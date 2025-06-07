import json

from src.utils import determining_time_day, cards_and_transactions, descriptions_and_transactions, \
    get_currency_rates, get_stock_rates, get_operations_with_range, read_user_settings


def get_json_answer(data_time: str) -> str:
    """Функция принимает дату и возвращает json ответ"""
    greeting = determining_time_day(data_time)

    transactions = get_operations_with_range(data_time)
    cards = cards_and_transactions(transactions)
    top_transactions = descriptions_and_transactions(transactions)
    currency_rates = get_currency_rates(data_time)
    stock_prices = get_stock_rates()
    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    json_string = json.dumps(result, ensure_ascii=False)
    return json_string


