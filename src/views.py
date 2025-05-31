import json

from src.utils import determining_time_day, get_read_xlsx, cards_and_transactions, descriptions_and_transactions, \
    get_currency_rates, get_stock_rates


def get_json_answer(data_time: str) -> dict[list]:
    path = 'data/operations.xlsx'
    greeting = determining_time_day(data_time)
    transactions = get_read_xlsx(path)
    cards = cards_and_transactions(transactions)
    top_transactions = descriptions_and_transactions(transactions)
    currency_rates = get_currency_rates(data_time)
    stock_prices = get_stock_rates(data_time)
    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    json_string = json.dumps(result, ensure_ascii=False)
    return json_string