from src.reports import spending_by_category
from src.utils import get_operations_with_range, cards_and_transactions, descriptions_and_transactions, \
    get_search_transaction_individual, get_read_xlsx, read_user_settings
from src.views import get_json_answer

if __name__ == '__main__':
    date_end = '2021-12-03 09:00:00'
    # print(get_operations_with_range(date_end))
    # print(cards_and_transactions(operations_df))
    print(get_json_answer(date_end))
    # print(get_stock_rates('2025-05-29 16:42:17'))
    # print(get_currency_rates('2025-05-30 10:44:17'))
    # print(read_user_settings('data/user_setti.json'))
    # print(cards_and_transactions(trans))
    # print(get_search_transaction_individual(operations_df))
    # df = get_read_xlsx('data/operations.xlsx')
    # trans = get_operations_with_range(date_end)
    # # spending_by_category(operations_df,"Авиабилеты",date_end)
    #
    # print(descriptions_and_transactions(trans))