from src.utils import get_operations_with_range, cards_and_transactions, descriptions_and_transactions
from src.views import get_json_answer

if __name__ == '__main__':
    date_end = '2021-12-03 16:42:17'
    operations_df = get_operations_with_range(date_end)
    # print(cards_and_transactions(operations_df))
    print(get_json_answer('2021-12-03 23:42:17'))
    # trans = get_read_xlsx('data/operations.xlsx')
    # print(get_stock_rates('2025-05-29 16:42:17'))
    # print(get_currency_rates('2025-05-30 10:44:17'))
    # print(descriptions_and_transactions(operations_df))
    # print(cards_and_transactions(trans))

