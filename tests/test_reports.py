from datetime import datetime
from unittest.mock import patch
import pandas as pd
from src.reports import get_operations_with_range_3_month, writing_to_file, spending_by_category
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


def create_mock_dataframe():
    return pd.DataFrame({
        "Категория": ["Еда"],
        "Сумма": [100.0]
    })


# Патчим datetime.today() и save_to_file в модуле, где они используются декоратором.
@patch('src.reports.datetime')
@patch('src.reports.save_to_file')
def test_writing_to_file_corrected(mock_save_to_file, mock_datetime):
    """Тест на успешное выполнение декоратора writing_to_file"""
    # 1. Мокируем datetime.today() для предсказуемой даты
    fixed_date = datetime(2025, 6, 7)
    mock_datetime.today.return_value = fixed_date

    # 2. Создаем мокированную функцию, которую будем декорировать.
    #    В реальном коде это была бы ваша spending_by_category.
    @writing_to_file  # Предполагаем, что writing_to_file импортирован
    def mock_decorated_function():
        return create_mock_dataframe()

    # 3. Вызываем декорированную функцию
    result_from_decorator = mock_decorated_function()

    # 4. Проверяем, что декоратор успешно выполнился и вернул DataFrame
    expected_df = create_mock_dataframe()  # Получаем ожидаемый DataFrame
    pd.testing.assert_frame_equal(result_from_decorator, expected_df) #это функция из библиотеки pandas,
    # предназначенная для сравнения двух DataFrame и выдачи информативного сообщения об ошибке, если они не идентичны

    # 5. Проверяем, что mock_save_to_file был вызван ровно один раз
    mock_save_to_file.assert_called_once()

    # 6. Проверяем аргументы, с которыми был вызван mock_save_to_file
    called_data, called_file_path = mock_save_to_file.call_args[0] #Аргументы с которой вызывается функция
    # save_to_file

    # Проверяем DataFrame, который был передан save_to_file
    expected_df_to_save = create_mock_dataframe()
    pd.testing.assert_frame_equal(called_data, expected_df_to_save)

    # Проверяем ожидаемое имя файла и путь
    expected_category = expected_df_to_save["Категория"].values[0]  # "Еда"
    expected_file_name = f'{fixed_date.strftime("%Y-%m-%d")}_{expected_category}.json'
    expected_file_path = os.path.join('logs', expected_file_name)  # Используем os.path.join
    expected_file_path = os.path.normpath(expected_file_path)  # Нормализуем путь
    called_file_path = os.path.normpath(called_file_path)  # Нормализуем путь, который вернула функция
    assert called_file_path == expected_file_path


@patch('src.reports.get_operations_with_range_3_month')
def test_spending_by_category_date(mock_get_operations_with_range_3_month,sample_data):
    """Тестируем без указания даты"""
    mock_get_operations_with_range_3_month.return_value = sample_data
    result = spending_by_category(sample_data, "Пополнения", '2025-06-21 12:12:12')
    result_dict = result.to_dict(orient='records')
    expected = [{"Категория": "Пополнения", "Сумма платежа": 350.0}]
    assert result_dict == expected





