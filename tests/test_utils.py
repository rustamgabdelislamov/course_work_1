import pytest
from unittest.mock import patch
import pandas as pd
from freezegun import freeze_time
from src.utils import get_read_xlsx, determining_time_day, get_operations_with_range, cards_and_transactions, \
    descriptions_and_transactions, get_currency_rates, read_user_settings, get_stock_rates, \
    get_search_transaction_individual


@patch('src.utils.pd.read_excel')
def test_get_read_xlsx_success(mock_get):
    """Тест если правильный путь до файла"""
    mock_get.return_value = pd.DataFrame({
        'Column1': [1, 2, 3],
        'Column2': ['A', 'B', 'C']
    })
    path = 'data/operations.xlsx'
    result = get_read_xlsx(path)
    expected_result = pd.DataFrame({
        'Column1': [1, 2, 3],
        'Column2': ['A', 'B', 'C']
    })
    assert result.equals(expected_result)


def test_get_read_xlsx_no_path():
    """Тест при неправильном пути"""
    with pytest.raises(FileNotFoundError) as ex:
        get_read_xlsx('123.xlsx')

    assert str(ex.value) == 'Файл не найден: 123.xlsx'


def test_get_read_xlsx_error_file():
    """Тест при пустом файле"""
    with pytest.raises(ValueError) as ex:
        path = 'data/123.xlsx'
        get_read_xlsx(path)

    assert str(ex.value) == f"Файл пуст: {path}"


@freeze_time("15:50:00")
def test_determining_time_day_success():
    """Тест при правильном формате даты"""
    assert determining_time_day() == 'Добрый день'


@freeze_time("20:50:00")
def test_determining_time_day_success_():
    """Тест при правильном формате даты"""
    assert determining_time_day() == 'Добрый вечер'


@patch('src.utils.get_read_xlsx')
def test_get_operations_with_range(mock_get_read_xlsx):
    """Тест на проверку фильтрации"""
    date_end = '2025-06-14 12:12:12'
    dict_ = {
        'Дата операции': [
            '2025-06-20 12:12:12', '2025-06-19 12:12:12', '2025-06-18 12:12:12', '2025-06-17 12:12:12',
            '2025-06-16 12:12:12', '2025-06-15 12:12:12', '2025-06-14 12:12:12', '2025-06-13 12:12:12'],
        'Статус': ['OK', 'OK', 'ERROR', 'OK', 'OK', 'OK', 'ERROR', 'OK'],
        'Категория': ['Переводы', 'Аптеки', 'Супермаркеты', 'Пополнения',
                      'Переводы', 'Аптеки', 'Супермаркеты', 'Пополнения'],
        'Номер карты': ['*5091', '*3456', '*4959', '', '*7654', '*4959', '*3456', ''],
        'Сумма платежа': [100.00, 50.00, 50.00, 200.00, 150.00, 50.00, 200.00, 150.00],
        'Описание': ['Сергей Г.', 'Аптека Вита', 'Магнит', 'Олег М.',
                     'Сергей Г.', 'Аптека Вита', 'Магнит', 'Олег М.']
    }
    df = pd.DataFrame(dict_)
    mock_get_read_xlsx.return_value = df
    result = get_operations_with_range(date_end)
    expected = pd.DataFrame({
                            'Дата операции': ['13.06.2025'],
                            'Статус': ['OK'],
                            'Категория': ['Пополнения'],
                            'Номер карты': [''],
                            'Сумма платежа': [150.00],
                            'Описание': ['Олег М.']
                            })
    assert result.reset_index(drop=True).equals(expected.reset_index(drop=True))


@patch('src.utils.get_read_xlsx')
def test_get_operations_with_range_empty(mock_get_read_xlsx):
    """Тест на проверку фильтрации при пустом файле"""
    date_end = '2025-06-14 12:12:12'
    empty_df = pd.DataFrame(columns=["Дата операции", "Статус"])
    mock_get_read_xlsx.return_value = empty_df
    result = get_operations_with_range(date_end)
    expected = "Данных транзакций за период не найдено"
    assert result == expected


def test_cards_and_transactions_success(sample_data):
    """Тест с правильными даннами"""
    result = cards_and_transactions(sample_data)
    expected = [
                {'last_digits': '3456', 'total_spent': 50.0, 'cashback': 0.50},
                {'last_digits': '4959', 'total_spent': 200.0, 'cashback': 2.0},
                {'last_digits': '5091', 'total_spent': 100.0, 'cashback': 1.0}
                ]

    assert result == expected


def test_cards_and_transactions_empty(sample_data_empty):
    """Тест с пустым DataFrame"""
    result = cards_and_transactions(sample_data_empty)
    expected = "Данных транзакций за период не найдено"
    assert result == expected


def test_descriptions_and_transactions_success(sample_data):
    """Тест с правильными даннами"""
    result = descriptions_and_transactions(sample_data)
    expected = [{'date': '17.06.2025', 'amount': 200.0, 'category': 'Пополнения', 'description': 'Олег М.'},
                {'date': '16.05.2025', 'amount': 150.0, 'category': 'Переводы', 'description': 'Сергей Г.'},
                {'date': '13.06.2025', 'amount': 150.0, 'category': 'Пополнения', 'description': 'Олег М.'},
                {'date': '20.06.2025', 'amount': 100.0, 'category': 'Переводы', 'description': 'Сергей Г.'},
                {'date': '19.06.2025', 'amount': 50.0, 'category': 'Аптеки', 'description': 'Аптека Вита'}]
    assert result == expected


def test_descriptions_and_transactions_empty(sample_data_empty):
    """Тест с пустым DataFrame"""
    result = descriptions_and_transactions(sample_data_empty)
    expected = "Данных транзакций за период не найдено"
    assert result == expected


def test_read_user_settings_success():
    """Тест при правильном пути и наличию json """
    result = read_user_settings('data/user_settings.json')
    expected = {
                "user_currencies": ["USD", "EUR"],
                "user_stocks": ["AAPL", "AMZN"]}
    assert result == expected


def test_read_user_settings_error():
    """Тест при неправильном пути"""
    path = 'data/user.json'
    with pytest.raises(FileNotFoundError) as ex:
        read_user_settings(path)
    assert str(ex.value) == f'Файл {path} не найден.'


@patch('src.utils.requests')
def test_get_currency_rates_success(mock_requests):
    """Тест с ответом от сети с правильным ответом"""
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'quotes': {
            'USDRUB': {
                'start_rate': 73.973038,
            },
            'EURRUB': {
                'start_rate': 83.688986,
            }
        }
    }

    result = get_currency_rates('2021-12-03 12:12:12')
    expected = [{"currency": "USD", "rate": 73.973038}, {"currency": "EUR", "rate": 83.688986}]
    assert result == expected


@patch('src.utils.requests')
def test_get_currency_rates_success_no_response(mock_requests):
    """Тест с ответом от сети с неправильным ответом"""
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
            'quotes': {
                'RUB': {
                    'start_rate': 73.973038,
                },
                'UB': {
                    'start_rate': 83.688986,
                }
            }
        }

    result = get_currency_rates('2021-12-03 12:12:12')
    expected = [{"Курс для USD не найден."}, {"Курс для EUR не найден."}]
    assert result == expected


@patch('src.utils.requests')
def test_get_currency_rates_success_no_200(mock_requests):
    """Тест со status_code не равным 200"""
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 404
    result = get_currency_rates('2021-12-03 12:12:12')
    expected = 'Проблема с сетью или сервером'
    assert result == expected


@patch('src.utils.requests')
def test_get_stock_rates_success(mock_requests):
    """Тест с ответом от сети с правильным ответом"""
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 200
    # Предположим, что API возвращает поочередно данные для каждой акции
    mock_response.json.side_effect = [
        {"Global Quote": {"01. symbol": "AAPL", "05. price": "203.9200"}},
        {"Global Quote": {"01. symbol": "AMZN", "05. price": "213.5700"}}
    ]

    result = get_stock_rates()
    expected = [
        {"stock": "AAPL", "price": "203.9200"},
        {"stock": "AMZN", "price": "213.5700"}
    ]
    assert result == expected


@patch('src.utils.requests')
def test_get_stock_rates_success_no_response(mock_requests):
    """Тест с ответом от сети с неправильным ответом"""
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 200
    # Предположим, что API возвращает поочередно данные для каждой акции
    mock_response.json.side_effect = [
        {"Global": {"01. symbol": "AA", "05. price": "203.9200"}},
        {"Global": {"01. symbol": "AM", "05. price": "213.5700"}}
    ]
    result = get_stock_rates()
    expected = [{"Курс для AAPL не найден."}, {"Курс для AMZN не найден."}]
    assert result == expected


@patch('src.utils.requests')
def test_get_stock_rates_success_no_200(mock_requests):
    """Тест со status_code не равным 200"""
    mock_response = mock_requests.get.return_value
    mock_response.status_code = 404
    result = get_stock_rates()
    expected = 'Проблема с сетью'
    assert result == expected


def test_get_search_transaction_individual(sample_data):
    """Тест с правильными даннами"""
    result = get_search_transaction_individual(sample_data)
    expected = [{'transfers': ['Сергей Г.']}]
    assert result == expected


def test_get_search_transaction_individual_empty(sample_data_empty):
    """Тест с пустым DataFrame"""
    result = get_search_transaction_individual(sample_data_empty)
    expected = "Данных транзакций за период не найдено"
    assert result == expected
