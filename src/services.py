import datetime
import json
import os
import re
from typing import Any, Hashable

import pandas as pd
from pandas import DataFrame


def excel_file_reader(filename: str) -> DataFrame:
    """Функция читает файл эксель и возвращает дата-фрэйм"""
    if filename.lower().endswith("xlsx") or filename.lower().endswith("xls"):
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data", f"{filename}"))
        try:
            data = pd.read_excel(full_path)
            return data
        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
            return DataFrame({})
        except Exception as e:
            print(f"Возникла непредвиденная ошибка чтения файла: {e}")
            return DataFrame({})
    print("Неверный формат файла")
    return DataFrame({})


def get_best_cashback(month: int, year: int, data: DataFrame) -> str:
    """Функция принимает год, месяц и данные, выдает JSON с анализом, сколько на каждой категории можно заработать
    кешбэка в указанном месяце года"""
    result = {}
    data_not_na = data[data["Дата платежа"].notnull()]
    data_not_na["Дата платежа"] = data_not_na["Дата платежа"].map(
        lambda date: datetime.datetime.strptime(date, "%d.%m.%Y")
    )
    filtered_data = data_not_na[data_not_na["Дата платежа"].map(lambda date: (date.year, date.month) == (year, month))]
    agg_data = filtered_data.groupby(by="Категория").agg({"Кэшбэк": "sum"})
    agg_data_with_cashback = agg_data[agg_data["Кэшбэк"] > 0].sort_values(by="Кэшбэк", ascending=False)
    if not agg_data_with_cashback.empty:
        for index, row in agg_data_with_cashback.iterrows():
            result[index] = round(row["Кэшбэк"])
        json_data = json.dumps(result, indent=4, ensure_ascii=False)
        return json_data
    print("Выгодные категории кэшбэка не найдены")
    return json.dumps(result)


def transform_expenses_to_list(operations: DataFrame, currency: str) -> list[dict[Hashable, Any]]:
    """Функция принимает дата-фрэйм файла с операциями и возвращает упрощенный список трат в указанной
    валюте ({"дата": "сумма"})"""
    data = operations[["Дата операции", "Сумма операции", "Валюта операции", "Категория"]]
    expenses = data.loc[
        (data["Категория"] != "Переводы") & (data["Сумма операции"] < 0) & (data["Валюта операции"] == currency)]
    expenses = expenses[["Дата операции", "Сумма операции"]]
    expenses["Дата операции"] = expenses["Дата операции"].map(
        lambda date: datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    )
    expenses["Дата операции"] = expenses["Дата операции"].map(
        lambda date: datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
    )
    expenses["Дата операции"] = expenses["Дата операции"].map(lambda date: date.split()[0])
    list_operations = expenses.to_dict(orient="records")
    return list_operations


def investment_bank(month: str, transactions: list[dict[Hashable, Any]], limit: int) -> float:
    """Вычисляет сумму, отложенную в инвест-копилку за определенный месяц,
    на основе округления трат до выбранного лимита (10, 50 или 100)."""
    filtered_transactions = [transaction for transaction in transactions if
                             month in str(transaction.get("Дата операции"))]
    investment = 0.0
    if filtered_transactions:
        for transaction in filtered_transactions:
            amount = -1 * float(transaction.get("Сумма операции", 0))
            if amount % limit == 0:
                continue
            rounded_amount = ((amount // limit) + 1) * limit
            round_up_rest = float(rounded_amount) - amount
            investment += round_up_rest
        return round(investment, 1)
    return investment


def find_remittance_to_people(operations: DataFrame) -> str:
    """Функция принимает дата-фрэйм и возвращает JSON с транзакциями, относящимися к успешным переводам людям"""
    pattern = r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\."
    remittance = operations.loc[
        (operations["Категория"] == "Переводы") & (operations["Статус"] == "OK") & (operations["Описание"].notna())]
    remittance_filtered = remittance[
        remittance["Описание"].apply(lambda description: bool(re.search(pattern, description)))
    ]
    return remittance_filtered.to_json(orient="records", indent=4, force_ascii=False)


if __name__ == "__main__":
    df = excel_file_reader("operations.xlsx")
    # Определяем категории кэшбэка за указанный период
    print(get_best_cashback(10, 2019, df))
    # Считаем инвесткопилку при заданном шаге округления
    expenses_for_investment = transform_expenses_to_list(df, "RUB")
    print(investment_bank("2019-10", expenses_for_investment, 50))
    # Поиск переводов людям
    print(find_remittance_to_people(df))
