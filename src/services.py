import pandas as pd
import re
import json

def get_search_transaction_individual(df: pd.DataFrame) -> str:
    """Функция возвращает список имен кому был совершен перевод"""
    filter_operations = df[(df["Статус"] == "OK") & (df["Категория"] == "Переводы")]
    pattern = r'[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.'
    result_filter = filter_operations[filter_operations["Описание"].str.contains(pattern, regex=True)]
    names = result_filter['Описание'].tolist()
    unique_names = list(set(names))
    result_list = []
    result_dict = {
        'transfers': unique_names
    }
    result_list.append(result_dict)
    json_string = json.dumps(result_list, ensure_ascii=False, indent=4)
    return json_string