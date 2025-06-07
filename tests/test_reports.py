from datetime import datetime
from unittest.mock import patch
import pandas as pd
from src.reports import get_operations_with_range_3_month, writing_to_file
from src.utils import get_read_xlsx
import os

@patch('src.reports.get_read_xlsx')
def test_get_operations_with_range_3(mock_get_read_xlsx):
    """Тест на проверку фильтрации"""
    date_end = '2025-06-15 12:12:12'
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
    result = get_operations_with_range_3_month(date_end)
    expected = pd.DataFrame({
        'Дата операции': ['15.06.2025', '13.06.2025'],
        'Статус': ['OK', 'OK',],
        'Категория': ['Аптеки', 'Пополнения'],
        'Номер карты': ['*4959', ''],
        'Сумма платежа': [50.00, 150],
        'Описание': ['Аптека Вита', 'Олег М.']
    })
    assert result.reset_index(drop=True).equals(expected.reset_index(drop=True))


@writing_to_file
def get_data():
    """Эта фиктивная функция будет возвращать DataFrame,который ожидает декоратор writing_to_file."""
    return pd.DataFrame({"Категория": ["Еда"], "Сумма": [100.0]})


# Патчим datetime.today() и save_to_file в модуле, где они используются декоратором.
# Предполагаем, что это src.decorators
@patch('src.reports.datetime')
@patch('src.reports.save_to_file')
def test_writing_to_file_corrected(mock_save_to_file, mock_datetime):
    """Тест на успешное выполнение декоратора writing_to_file"""
    # 1. Мокируем datetime.today() для предсказуемой даты
    # Устанавливаем ту же дату, что и в вашем выводе ошибки, для ясности.
    fixed_date = datetime(2025, 6, 7)
    mock_datetime.today.return_value = fixed_date
    # 2. Вызываем декорированную функцию
    # get_data теперь возвращает DataFrame, который ожидает декоратор.
    # Декоратор не возвращает результат декорируемой функции (нет 'return result'),
    # поэтому ожидаем None в случае успеха.
    result_from_decorator = get_data()

    # 3. Проверяем, что декоратор успешно выполнился (вернул None)
    assert result_from_decorator is None

    # 4. Проверяем, что mock_save_to_file был вызван ровно один раз
    mock_save_to_file.assert_called_once()

    # 5. Проверяем аргументы, с которыми был вызван mock_save_to_file
    # mock_save_to_file.call_args возвращает кортеж ((args), {kwargs})
    called_data, called_file_path = mock_save_to_file.call_args[0] # args[0] это первый позиционный аргумент, args[1] второй

    # Проверяем DataFrame, который был передан save_to_file
    expected_df_to_save = pd.DataFrame({
        "Категория": ["Еда"],
        "Сумма": [100.0]
    })
    pd.testing.assert_frame_equal(called_data, expected_df_to_save)

    # Проверяем ожидаемое имя файла и путь
    expected_category = expected_df_to_save["Категория"].values[0] # "Еда"
    expected_file_name = f'{fixed_date.strftime("%Y-%m-%d")}_{expected_category}.json'
    expected_file_path = f'logs/{expected_file_name}'

    assert called_file_path == expected_file_path
