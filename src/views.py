import json
import os
import time
from datetime import datetime
from json import JSONDecodeError
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame
from requests import RequestException

from src.utils import views_logger

load_dotenv()
api_key = os.getenv("API_KEY")
api_key2 = os.getenv("API_KEY2")


def open_settings(filename: str) -> dict[str, Any] | Any:
    """Функция читает JSON-файл с пользовательскими настройками"""
    full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", f"{filename}"))
    if filename.endswith("json"):
        try:
            views_logger.info("Попытка открытия файла настроек")
            with open(full_path) as f:
                try:
                    views_logger.info("Попытка чтения файла настроек")
                    user_settings = json.load(f)
                    views_logger.info("Функция успешно завершила работу")
                    return user_settings
                except JSONDecodeError as e:
                    views_logger.error("Ошибка чтения файла настроек")
                    print(f"Ошибка чтения файла: {e}")
                    return {}
        except FileNotFoundError as e:
            views_logger.error("Файл настроек не был найден")
            print(f"Ошибка: {e}")
            return {}
    else:
        views_logger.error("Обнаружено неверное разрешение файла настроек")
        print("Неверный формат файла настроек")
        return {}


def get_currency_rate(settings: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Функция выводит текущие курсы иностранных валют в рублях согласно настройкам в JSON-файле."""
    currency_rates = []
    if settings != {}:
        try:
            views_logger.info("Попытка запроса на сервер курса валют")
            response = requests.get(url=f"https://v6.exchangerate-api.com/v6/{api_key}/latest/RUB", timeout=5)
            response.raise_for_status()
            data = response.json()
            for currency in settings.get("user_currencies", []):
                if data.get("conversion_rates", {}).get(f"{currency}") is not None:
                    currency_rates.append(
                        {"currency": f"{currency}", "rate": round(1 / data["conversion_rates"][f"{currency}"], 2)}
                    )
            views_logger.info("Функция успешно завершила работу")
            return currency_rates
        except RequestException as e:
            views_logger.error("Ошибка запроса на сервер курса валют")
            print(f"Ошибка при конвертации валюты: {e}")
            return currency_rates
    views_logger.warning("Файл настроек пуст, курс валют не определен")
    return currency_rates


def get_stock_rate(settings: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Функция выводит текущие курсы акций согласно настройкам в JSON-файле."""
    stock_rates: list[Any] = []
    if settings != {}:
        for stock in settings.get("user_stocks", []):
            try:
                views_logger.info("Попытка запроса на сервер стоимости акций")
                response = requests.get(
                    url=f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key2}",
                    timeout=5)
                response.raise_for_status()
                data = response.json()
            except RequestException as e:
                views_logger.error("Ошибка запроса на сервер стоимости акций")
                print(f"Ошибка при запросе информации об акциях: {e}")
                return stock_rates
            else:
                if data.get("Global Quote", {}).get("05. price") is not None:
                    stock_rates.append(
                        {"stock": f"{stock}", "price": round(float(data["Global Quote"]["05. price"]), 2)}
                    )
            time.sleep(1.2)
        views_logger.info("Функция успешно завершила работу")
        return stock_rates
    views_logger.warning("Файл настроек пуст, стоимость акций не определена")
    return stock_rates


def user_greeting() -> str:
    """ "Функция выводит приветствие пользователю в зависимости от времени суток."""
    current_time = datetime.now()
    str_current_time = current_time.strftime("%Y-%m-%d %H-%M-%S").split()
    if "06-00-00" < str_current_time[1] < "12-00-00":
        greeting = "Доброе утро!"
    elif "12-00-00" < str_current_time[1] < "18-00-00":
        greeting = "Добрый день!"
    elif "18-00-00" < str_current_time[1] < "23-00-00":
        greeting = "Добрый вечер!"
    else:
        greeting = "Доброй ночи!"
    views_logger.info("Функция приветствия успешно завершила работу")
    return greeting


def file_reader(input_date: str, filename: str) -> DataFrame:
    """Функция читает файл эксель и возвращает дата-фрэйм с транзакциями со статусом "ОК", за период времени с начала
    месяца по указанную дату"""
    if filename.lower().endswith("xlsx") or filename.lower().endswith("xls"):
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data", f"{filename}"))
        month = input_date.split(".")[1]
        year = input_date.split(".")[2]
        start_date = datetime.strptime(f"01.{month}.{year} 00:00:00", "%d.%m.%Y %H:%M:%S")
        end_date = datetime.strptime(f"{input_date} 23:59:59", "%d.%m.%Y %H:%M:%S")
        try:
            views_logger.info("Попытка чтения файла транзакций")
            data = pd.read_excel(full_path)
        except FileNotFoundError as e:
            views_logger.error("Файл транзакций не найден")
            print(f"Ошибка: {e}")
            return DataFrame({})
        except Exception as e:
            views_logger.error("Ошибка чтения файла транзакций")
            print(f"Возникла непредвиденная ошибка: {e}")
            return DataFrame({})
        else:
            data["Дата операции"] = data["Дата операции"].map(
                lambda date: datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
            )
            filtered_data = data.loc[
                (data["Дата операции"] <= end_date) & (data["Дата операции"] >= start_date) & (data["Статус"] == "OK")]
            views_logger.info("Функция чтения файла транзакций успешно завершила работу")
            return filtered_data
    else:
        views_logger.warning("Обнаружено неверное разрешение файла транзакций")
        print("Формат файла не поддерживается")
        return DataFrame({})


def find_top_five_transactions(operations: DataFrame) -> list[dict[str, Any]]:
    """Функция выводит топ-5 операций за период времени с начала месяца по указанную дату, отсортированных по
    убыванию в абсолютном выражении"""
    list_transactions = []
    if not operations.empty:
        sorted_data = operations.sort_values(
            by="Сумма операции", ascending=False, na_position="last", key=lambda x: abs(x)
        )
        top_transactions = sorted_data.head(5)
        top_transactions["Дата операции"] = top_transactions["Дата операции"].map(
            lambda date: datetime.strftime(date, "%d.%m.%Y %H:%M:%S")
        )
        top_transactions["Дата операции"] = top_transactions["Дата операции"].map(lambda date: date.split()[0])
        for _, row in top_transactions.iterrows():
            list_transactions.append(
                {
                    "date": row["Дата операции"],
                    "amount": row["Сумма операции"],
                    "category": row["Категория"],
                    "description": row["Описание"],
                }
            )
        views_logger.info("Функция поиска транзакций успешно завершила работу")
        return list_transactions
    else:
        views_logger.warning("Не найдено ни одной операции")
        print("Данные об операциях отсутствуют")
        return list_transactions


def get_card_stats(operations: DataFrame) -> list[dict[str, Any]]:
    """Функция выводит сумму трат и кэшбэк по картам в виде списка с начала месяца, на который выпадает входящая дата,
    по входящую дату (дд.мм.гггг)."""
    card_list = []
    if not operations.empty:
        filtered_data = operations.loc[operations["Сумма операции"] < 0]
        group_by_card = (
            filtered_data.groupby(by="Номер карты", dropna=True)
            .agg({"Сумма операции": "sum", "Кэшбэк": "sum"})
            .astype(object)
        )
        for index, row in group_by_card.iterrows():
            card_list.append(
                {
                    "last_digits": index,
                    "total_spent": -1 * round(row["Сумма операции"], 2),
                    "cashback": round(row["Кэшбэк"], 2)})
        views_logger.info("Функция поиска операций по картам упешно завершила работу")
        return card_list
    else:
        views_logger.warning("Не найдено ни одной операции по картам")
        print("Данные об операциях отсутствуют")
        return card_list


def main_page(date: str) -> str:
    """Функция формирует JSON-ответ по транзакциям с начала месяца на который выпадает входящая дата, по входящую
    дату (дд.мм.гггг), а также выдает текущие курсы валют и акций"""
    df = file_reader(f"{date}", "operations.xlsx")
    user_settings = open_settings("user_settings.json")
    result = {
        "greeting": user_greeting(),
        "cards": get_card_stats(df),
        "top_transactions": find_top_five_transactions(df),
        "currency_rates": get_currency_rate(user_settings),
        "stock_prices": get_stock_rate(user_settings),
    }
    json_data = json.dumps(result, indent=4, ensure_ascii=False)
    views_logger.info("Функция main_page заввершила работу")
    return json_data


if __name__ == "__main__":
    views_logger.info("Функция main_page начала работу")
    print(main_page("31.12.2019"))
