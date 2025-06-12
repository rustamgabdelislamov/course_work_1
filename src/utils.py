from datetime import datetime

import pandas as pd
import os
from dotenv import load_dotenv
import requests
import json
import logging

logger = logging.getLogger('utils')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/utils.log', mode='w', encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_ALPHAVANTAGE = os.getenv('API_KEY_ALPHAVANTAGE')


def get_read_xlsx(path: str) -> pd.DataFrame:
    """Функция принимает путь к excel файлу и преобразует в dataFrame"""
    logger.info(f"открываем файл по пути{path}")
    if not os.path.isfile(path):
        logger.error(f"ошибка не найден файл по данному пути{path}")
        raise FileNotFoundError(f"Файл не найден: {path}")
    try:
        df = pd.read_excel(path)
        logger.info(f"открыли файл по данному пути{path}")
        if df.empty:
            logger.error(f"Файл пуст или поврежден {path}")
            raise ValueError(f"Файл пуст или поврежден: {path}")
        return df

    except ValueError as e:
        logging.error(f"Ошибка при чтении файла {path}: {e}")
        raise ValueError(f"Файл пуст: {path}")


def determining_time_day() -> str:
    """Функция выводит приветствие в зависимости от времени суток"""
    now = datetime.now()
    hour = now.hour
    logger.info("сравниваем текущую дату с условиями")
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_operations_with_range(date_end: str) -> pd.DataFrame | str:
    """Функция получения операций за период"""
    df = get_read_xlsx('data/operations.xlsx')
    logger.info("открываем файл через get_read_xlsx")
    date_start = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-01 00:00:00")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    logger.info("сортируем даты операции по дате и со статусом ок")
    filter_operations = df[
        (df["Дата операции"] >= date_start) &
        (df["Дата операции"] <= date_end) &
        (df["Статус"] == "OK")
    ].copy()
    logger.info("произошла сортировка")

    if filter_operations.empty:
        logger.info("Данных транзакций за период не найдено")
        return "Данных транзакций за период не найдено"
    logger.info("Замена даты из формата datatime в формат строки")
    filter_operations["Дата операции"] = filter_operations["Дата операции"].dt.strftime("%d.%m.%Y")
    logger.info("возврат отфильтрованных данных")
    return filter_operations


def cards_and_transactions(df: pd.DataFrame) -> list[dict] | str:
    """Функция получения по номерам карт: сумм платежа и кэшбэка с учетом фильтрации по дате"""
    filter_operations = df[(df["Статус"] == "OK") & (df["Категория"] != "Пополнения")]

    if filter_operations.empty:
        logger.info("Данных транзакций за период не найдено")
        return "Данных транзакций за период не найдено"
    logger.info("группировка по номеру карты")
    operation_group = filter_operations[["Номер карты", "Сумма платежа"]].groupby("Номер карты").sum().reset_index()
    logger.info("перевод в словарь")
    operations = operation_group.to_dict(orient='records')

    result_cards = []
    logger.info("начинаем цикл")
    for operation in operations:
        last_digits = operation.get("Номер карты")[1:]
        total_spent = round(operation.get("Сумма платежа"), 2)
        cashback = abs(round(total_spent * 0.01, 2))
        logger.info("Получение результата")
        result = {
            "last_digits": last_digits,
            "total_spent": total_spent,
            "cashback": cashback
        }
        result_cards.append(result)
    logger.info("Возврат результата")
    return result_cards


def descriptions_and_transactions(df: pd.DataFrame) -> list[dict] | str:
    """Функция принимает DataFrame с транзакциями и возвращает отсортированный список топ 5 транзакций"""
    filter_operations = df[df["Статус"] == "OK"]

    if filter_operations.empty:
        return "Данных транзакций за период не найдено"

    transactions = filter_operations.to_dict(orient='records')
    result_descriptions = []

    for transaction in transactions:
        if transaction.get('Статус') == 'OK':
            date = transaction.get('Дата платежа')
            amount = transaction.get('Сумма платежа')
            category = transaction.get('Категория')
            description = transaction.get('Описание')
            result_descriptions.append({
                'date': date,
                'amount': amount,
                'category': category,
                'description': description
            })

    top_transactions = sorted(result_descriptions, key=lambda x: abs(x['amount']), reverse=True)[:5]
    return top_transactions


def read_user_settings(file_path):
    """Функция чтения json"""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f'Файл {file_path} не найден.')
    except json.JSONDecodeError:
        raise ValueError('Ошибка при чтении JSON файла.')


def get_currency_rates(date: str) -> list[dict] | str:
    """Функция принимает дату и выдает курс который есть в документе user_setting.json"""
    user_data = read_user_settings('data/user_settings.json')
    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    rates = []
    start_date = formatted_date
    end_date = formatted_date

    target_currency = "RUB"

    for data in user_data.get("user_currencies"):
        base_currency = data
        url = (f"https://api.apilayer.com/currency_data/change?start_date={start_date}&end_date={end_date}"
               f"&currencies={target_currency}&source={base_currency}")
        headers = {
            "apikey": API_KEY
        }

        try:
            response = requests.get(url, headers=headers)
            status_code = response.status_code

            if status_code == 200:
                result = response.json()
                currency_key = f"{base_currency}{target_currency}"
                quote_data = result.get("quotes", {}).get(currency_key)

                if quote_data:
                    start_rate = quote_data.get("start_rate")
                    result_dict = {
                        'currency': base_currency,
                        "rate": start_rate
                    }
                    rates.append(result_dict)
                else:
                    result = {f"Курс для {base_currency} не найден."}
                    rates.append(result)

            else:
                return 'Проблема с сетью или сервером'

        except requests.exceptions.RequestException as e:
            print(f"Проблема c ответом от сервера {e}")

    return rates


def get_stock_rates() -> list[dict] | str:
    """Функция выдает курс акций который есть в документе user_setting.json на текущую дату"""
    rates = []
    user_data = read_user_settings('data/user_settings.json')
    for data in user_data.get("user_stocks"):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": data,
            "apikey": API_KEY_ALPHAVANTAGE
        }

        try:
            response = requests.get(url, params=params)
            status_code = response.status_code

            if status_code == 200:

                result = response.json()
                global_quote = result.get("Global Quote", {})
                if global_quote:
                    result_dict = {
                        "stock": data,
                        "price": result.get("Global Quote", {}).get("05. price", {})
                    }
                    rates.append(result_dict)
                else:
                    result = {f"Курс для {data} не найден."}
                    rates.append(result)

            else:
                return 'Проблема с сетью'

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса для {data}: {e}")

    return rates


def get_search_transaction_individual(df: pd.DataFrame) -> list[dict] | str:
    """Функция возвращает список имен кому был совершен перевод"""
    filter_operations = df[(df["Статус"] == "OK") & (df["Категория"] == "Переводы")]

    if filter_operations.empty:
        return "Данных транзакций за период не найдено"

    pattern = r'[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.'
    result_filter = filter_operations[filter_operations["Описание"].str.contains(pattern, regex=True)]
    names = result_filter['Описание'].tolist()
    unique_names = list(set(names))
    result_list = []
    result_dict = {
        'transfers': unique_names
    }
    result_list.append(result_dict)
    return result_list
