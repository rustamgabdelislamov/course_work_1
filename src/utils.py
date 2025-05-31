from collections import defaultdict
from datetime import datetime, time


import pandas as pd
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_ALPHAVANTAGE = os.getenv('API_KEY_ALPHAVANTAGE')

def get_read_xlsx(path: str) -> list[dict]:
    """Функция принимает путь к excel файлу и преобразует в список словарей"""
    try:
        df = pd.read_excel(path)
        transactions = df.to_dict(orient='records')
        return transactions
    except Exception as e:
        return []


def determining_time_day(date_time: str) -> str:
    """Функция преобразовывает введенную дату в datatime и выводит приветствие в зависимости от времени суток"""
    dt = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    date = dt
    time_date = date.time()

    night_start = time(00, 0)
    night_end = time(6,0)
    morning_start = time(6, 1)
    morning_end = time(12, 0)
    day_start = time(12,1)
    day_end = time(18,0)
    evening_start = time(18,1)
    evening_end = time(23,59)

    if night_start <= time_date <= night_end:
        return 'Доброй ночи'
    elif morning_start <= time_date <= morning_end:
        return 'Доброе утро'
    elif day_start <= time_date <= day_end:
        return 'Добрый день'
    elif evening_start <= time_date <= evening_end:
        return 'Добрый вечер'


def cards_and_transactions(transactions:list[dict]) -> list[dict]:
    """Функция получения по номерам карт: сумм платежа и кэшбэка """
    card_sums = defaultdict(int)

    for transaction in transactions:
        if (transaction.get('Статус') == 'OK' and isinstance(transaction['Номер карты'], str)
                and transaction.get('Категория') != 'Пополнения'):
            card_sums[transaction['Номер карты']] += transaction['Сумма платежа']

    result_cards = []
    for key, value in card_sums.items():
        last_digits = key[1:]
        total_spent = abs(value)
        cashback = round(total_spent * 0.01, 2)

        result_cards.append({
            "last_digits": last_digits,
            "total_spent": round(total_spent, 2),
            "cashback": cashback
        })
    return result_cards


def descriptions_and_transactions(transactions: list[dict]) -> list[dict]:
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
                'category':category,
                'description': description
            })

    top_transactions = sorted(result_descriptions, key=lambda x: abs(x['amount']), reverse=True)[:5]
    return top_transactions


def get_currency_rates(date:str) -> list[dict]:
    """Функция принимает дату и выдает курс который есть в документе user_setting.json"""
    with open('data/user_settings.json', 'r') as file:
        user_data = json.load(file)
    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    rates = []
    start_date = formatted_date
    end_date = formatted_date

    target_currency = "RUB"
    for data in user_data.get("user_currencies"):
        base_currency = data
        url = f"https://api.apilayer.com/currency_data/change?start_date={start_date}&end_date={end_date}&currencies={target_currency}&source={base_currency}"
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
                start_rate = quote_data.get("start_rate")
                result_dict = {
                    'currency': data,
                    "rate": start_rate
                }
                rates.append(result_dict)
            else:
                return 'Проблема с сетью'
        except requests.exceptions.RequestException as e:
            print("Проблема")
    return rates


def get_stock_rates(date:str) -> list[dict]:
    """Функция принимает дату и выдает курс акций который есть в документе user_setting.json"""
    with open('data/user_settings.json', 'r') as file:
        user_data = json.load(file)
    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    formatted_date = date_obj.strftime("%Y-%m-%d")
    rates = []
    for data in user_data.get("user_stocks"):
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": data,
            "apikey": API_KEY_ALPHAVANTAGE
        }

        try:
            response = requests.get(url, params=params)
            status_code = response.status_code
            if status_code == 200:

                result = response.json()
                print(result)
                result_dict = {
                    "stock": data,
                    "price": result.get("Time Series (Daily)",{}).get(formatted_date,{}).get("4. close")
                }
                rates.append(result_dict)
            else:
                return 'Проблема с сетью'
        except requests.exceptions.RequestException as e:
            print("Проблема")
    return rates

