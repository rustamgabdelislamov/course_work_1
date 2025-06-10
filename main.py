from src.reports import spending_by_category, get_operations_with_range_3_month
from src.services import get_search_transaction_individual
from src.utils import get_read_xlsx, determining_time_day
from src.views import get_json_answer
from datetime import datetime


if __name__ == '__main__':
    while True:
        print(f'{determining_time_day()}!!! Добро пожаловать в программу работы с банковскими транзакциями.')
        print('''Выберите необходимый пункт меню:
                  1. Страница «Главная»
                  2. Страница «События»(Поиск переводов физическим лицам)
                  3. Категория «Сервисы» ''')
        input_menu = int(input())
        if input_menu == 1:
            while True:
                input_date = input('Введите дату в формате «Год-Месяц-День Часы:Минуты:Секунды»')
                try:
                    parsed_date = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
                    break
                except ValueError:
                    print("Ошибка: Неправильный формат даты.")
            print(get_json_answer(input_date))
        elif input_menu == 2:
            df = get_read_xlsx('data/operations.xlsx')
            print(f'Список переводов физическим лицам :{get_search_transaction_individual(df)}')
        elif input_menu == 3:
            while True:
                input_date_3 = input('Введите дату в формате «Год-Месяц-День Часы:Минуты:Секунды»')
                try:
                    parsed_date = datetime.strptime(input_date_3, "%Y-%m-%d %H:%M:%S")
                    break
                except ValueError:
                    print("Ошибка: Неправильный формат даты.")
            df_3 = get_operations_with_range_3_month(input_date_3)
            get_operations_with_range_3_month(input_date_3)
            input_category = input('Введите категорию для поиска')
            print(spending_by_category(df_3,input_category, input_date_3))
        else:
            print("Некорректный пункт меню. Пожалуйста, выберите 1, 2 или 3.")

        while True:
            continue_choice = input("Желаете ли продолжить? (да/нет): ").lower()
            if continue_choice == 'да':
                break
            elif continue_choice == 'нет':
                print("Спасибо за использование программы. До свидания!")
                exit()
            else:
                print("Пожалуйста, введите 'да' или 'нет'.")



