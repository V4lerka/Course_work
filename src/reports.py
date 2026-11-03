import os
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas import DataFrame

from src.services import excel_file_reader
from src.utils import reports_logger


def reports_saver_decorator(filename: Optional[str] = None):
    """Декоратор сохраняет дата-фрэйм в файл с указанным именем"""
    reports_logger.info("Вызов функции декоратора")

    def wrapper(func: Callable[[DataFrame, str, str], DataFrame]):
        @wraps(func)
        def inner(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> DataFrame:
            result = func(transactions, category, date)
            if filename is not None:
                full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../reports", f"{filename}"))
            else:
                full_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "../reports", "default_report.xlsx")
                )
            result.to_excel(full_path, sheet_name="Траты по категориям", index=False)
            return result

        return inner

    reports_logger.info("Функция декоратор завершила работу")
    return wrapper


@reports_saver_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает дата-фрэйм и возвращает траты по заданной категории за последние три месяца
    (от переданной даты) или от текущей даты."""
    if date is not None:
        date_obj_end = datetime.strptime(date, "%d.%m.%Y")
        date_obj_start = date_obj_end - relativedelta(months=3)
    else:
        date_obj_end = datetime.now()
        date_obj_start = date_obj_end - relativedelta(months=3)
    transactions["Дата операции"] = transactions["Дата операции"].map(
        lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M:%S")
    )
    transactions_filtered = transactions.loc[
        (transactions["Категория"] == category)
        & (transactions["Статус"] == "OK")
        & (transactions["Сумма операции"] < 0)
        & (transactions["Дата операции"] > date_obj_start)
        & (transactions["Дата операции"] < date_obj_end)
    ]
    if not transactions_filtered.empty:
        reports_logger.info("Функция spending_by_category успешно завершила работу")
        return transactions_filtered
    else:
        print("Транзакции под условия фильтрации не найдены")
        reports_logger.info("Функция spending_by_category завершила работу")
        return DataFrame({})


if __name__ == "__main__":
    data = excel_file_reader("operations.xlsx")
    reports_logger.info("Функция spending_by_category начала работу")
    df = spending_by_category(data, "Супермаркеты", "12.11.2019")
    if not df.empty:
        print(df[["Дата операции", "Номер карты", "Сумма операции"]].head())
