# Home_works_13.1
#  Этот проект представляет собой набор инструментов для анализа банковских транзакций. Он позволяет обрабатывать данные о транзакциях из различных источников, классифицировать транзакции по категориям, вычислять статистику расходов и доходов, а также генерировать отчеты.
## Установка
1. Клонируйте репозиторий ```git@github.com:rustamgabdelislamov/home_works_10_1.git```
2. Установите зависимости ```poetry instal```
3. Для запуска используйте ```python main.py```
### Описание функций
Основные функции находятся в utils

get_read_xlsx(path: str) -> pd.DataFrame:
    """Функция принимает путь к excel файлу и преобразует в dataFrame"""

def determining_time_day() -> str:
    """Функция выводит приветствие в зависимости от времени суток"""

def get_operations_with_range(date_end:str) -> pd.DataFrame | str:
    """Функция получения операций за период"""

def cards_and_transactions(df: pd.DataFrame) -> list[dict] | str:
    """Функция получения по номерам карт: сумм платежа и кэшбэка с учетом фильтрации по дате"""

def descriptions_and_transactions(df: pd.DataFrame) -> list[dict] | str:
    """Функция принимает DataFrame с транзакциями и возвращает отсортированный список топ 5 транзакций"""

def read_user_settings(file_path):
    """Функция чтения json"""

def get_currency_rates(date:str) -> list[dict] | str:
    """Функция принимает дату и выдает курс который есть в документе user_setting.json"""

def get_stock_rates() -> list[dict] | str:
    """Функция выдает курс акций который есть в документе user_setting.json на текущую дату"""

def get_search_transaction_individual(df: pd.DataFrame) -> list[dict] | str:
    """Функция возвращает список имен кому был совершен перевод"""

Написан декоратор writing_to_file для записи результатов в файл.



        
