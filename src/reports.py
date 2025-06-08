import pandas as pd
import json
import logging
from src.utils import get_read_xlsx
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger = logging.getLogger('reports')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/reports.log', mode='w', encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def save_to_file(data: pd.DataFrame, file_path: str) -> str:
    """Сохранение данных по указанному пути"""
    data_dict = data.to_dict(orient='records')
    try:
        with open(file_path, 'w', encoding='utf-8') as data_file:
            json.dump(data_dict, data_file, ensure_ascii=False, indent=4)
            logger.info('сохраняем данные в json')
    except Exception as ex:
        logger.error(f'Ошибка, что-то не так с путем или dataframe {ex}')
        return []


def writing_to_file(func):
    """Декоратор для записи в файл"""
    def wrapper(*args, **kwargs):
        try:
            today = datetime.today()
            logger.info("присвоили текущую дату")
            today_string = today.strftime('%Y-%m-%d')
            result = func(*args, **kwargs)
            logger.info("назначили результат декорируемой функции")
            file_name = f'{today_string}_{result["Категория"].values[0]}.json'
            logger.info("присвоили имя файла")
            file_path = f'logs/{file_name}'
            logger.info("путь файла")
            save_to_file(result, file_path)
            logger.info("записали рузультат")
            return result
        except Exception as ex:
            logger.error(f'Ошибка, что-то не так с путем или dataframe {ex}')

    return wrapper


def get_operations_with_range_3_month(date_end: str) -> pd.DataFrame:
    """Функция получения операций за период 3 месяца"""
    logger.info("получаем df из get_read_xlsx")
    df = get_read_xlsx('data/operations.xlsx')
    date_end_dt = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")
    logger.info("переводим время из строки в формат datetime")
    date_start_dt = date_end_dt - relativedelta(months=3)
    date_start = date_start_dt.strftime("%Y-%m-%d 00:00:00")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    filter_operations = df[(df["Дата операции"] >= date_start) &
                           (df["Дата операции"] <= date_end) &
                           (df["Статус"] == "OK")].copy()
    filter_operations["Дата операции"] = filter_operations["Дата операции"].apply(lambda x: x.strftime("%d.%m.%Y"))
    logger.info("возвращаем отфильтрованные операции")
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
