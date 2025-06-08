import pandas as pd
import json

from src.utils import get_read_xlsx
from datetime import datetime
from dateutil.relativedelta import relativedelta


def save_to_file(data: pd.DataFrame, file_path: str) -> str:
    """Сохранение данных по указанному пути"""
    data_dict = data.to_dict(orient='records')
    try:
        with open(file_path, 'w', encoding='utf-8') as data_file:
            json.dump(data_dict, data_file, ensure_ascii=False, indent=4)
    except Exception as ex:
        return []


def writing_to_file(func):
    """Декоратор для записи в файл"""
    def wrapper(*args, **kwargs):
        try:
            today = datetime.today()
            today_string = today.strftime('%Y-%m-%d')
            result = func(*args, **kwargs)
            file_name = f'{today_string}_{result["Категория"].values[0]}.json'
            file_path = f'logs/{file_name}'
            save_to_file(result, file_path)
            print(type(result))
            print(result)
            return result
        except Exception as ex:
            return []

    return wrapper


def get_operations_with_range_3_month(date_end:str) -> pd.DataFrame:
    """Функция получения операций за период 3 месяца"""
    df = get_read_xlsx('data/operations.xlsx')
    date_end_dt = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")
    date_start_dt = date_end_dt - relativedelta(months=3)
    date_start = date_start_dt.strftime("%Y-%m-%d 00:00:00")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    filter_operations = df[(df["Дата операции"] >= date_start) & (df["Дата операции"] <= date_end) & (df["Статус"] == "OK")].copy()
    filter_operations["Дата операции"] = filter_operations["Дата операции"].apply(lambda x: x.strftime("%d.%m.%Y"))
    return filter_operations


@writing_to_file
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: str = None) -> pd.DataFrame:
    if date is None:
        date_now = datetime.now()
        transactions = get_operations_with_range_3_month(date_now)
    else:
        transactions = get_operations_with_range_3_month(date)
    filter_operations = transactions[(transactions["Статус"] == "OK") & (transactions["Категория"] == category)]
    operation_group = filter_operations[["Категория", "Сумма платежа"]].groupby("Категория").sum().reset_index()
    return operation_group
