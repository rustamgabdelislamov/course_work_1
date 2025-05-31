from src.utils import determining_time_day, get_read_xlsx, cards_and_transactions, descriptions_and_transactions, \
    get_currency_rates, get_stock_rates
from src.views import get_json_answer

if __name__ == '__main__':
    # print(get_json_answer('2025-05-30 16:42:17'))
    # trans = get_read_xlsx('data/operations.xlsx')
    print(get_stock_rates('2025-05-29 16:42:17'))
    # print(get_currency_rates('2025-05-30 10:44:17'))
    # print(descriptions_and_transactions(trans))
    # print(cards_and_transactions(trans))
