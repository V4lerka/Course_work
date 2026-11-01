import datetime

import pandas as pd
import pytest


@pytest.fixture
def json_file_content():
    return {"user_currencies": ["USD", "EUR", "CNY"], "user_stocks": ["NVDA", "AAPL", "MSFT"]}


@pytest.fixture
def response_get_currency_rate():
    return {
        "result": "success",
        "documentation": "https://www.exchangerate-api.com/docs",
        "terms_of_use": "https://www.exchangerate-api.com/terms",
        "time_last_update_unix": 1793491201,
        "time_last_update_utc": "Sun, 01 Nov 2026 00:00:01 +0000",
        "time_next_update_unix": 1793577601,
        "time_next_update_utc": "Mon, 02 Nov 2026 00:00:01 +0000",
        "base_code": "USD",
        "conversion_rates": {"USD": 1.0, "EUR": 0.8956, "CNY": 6.6710},
    }


@pytest.fixture
def result_get_currency_rate():
    return [{"currency": "USD", "rate": 1.0}, {"currency": "EUR", "rate": 1.12}, {"currency": "CNY", "rate": 0.15}]


@pytest.fixture
def response_get_currency_rate_empty():
    return {
        "result": "success",
        "documentation": "https://www.exchangerate-api.com/docs",
        "terms_of_use": "https://www.exchangerate-api.com/terms",
        "time_last_update_unix": 1793491201,
        "time_last_update_utc": "Sun, 01 Nov 2026 00:00:01 +0000",
        "time_next_update_unix": 1793577601,
        "time_next_update_utc": "Mon, 02 Nov 2026 00:00:01 +0000",
        "base_code": "USD",
        "conversion_rates": {},
    }


@pytest.fixture
def response_get_stock_ok():
    return {
        "Global Quote": {
            "01. symbol": "IBM",
            "02. open": "258.2800",
            "03. high": "259.5900",
            "04. low": "254.7105",
            "05. price": "257.8100",
            "06. volume": "5741772",
            "07. latest trading day": "2026-10-30",
            "08. previous close": "258.2800",
            "09. change": "-0.4700",
            "10. change percent": "-0.1820%",
        }
    }


@pytest.fixture
def response_get_stock_empty():
    return {"Global Quote": {}}


@pytest.fixture
def result_get_stock_empty():
    return [
        {"stock": "NVDA", "price": "Unknown"},
        {"stock": "AAPL", "price": "Unknown"},
        {"stock": "MSFT", "price": "Unknown"},
    ]


@pytest.fixture
def result_get_stock_ok():
    return [{"stock": "NVDA", "price": 257.81}, {"stock": "AAPL", "price": 257.81}, {"stock": "MSFT", "price": 257.81}]


@pytest.fixture
def get_card_stats_data():
    data = {
        "Номер карты": ["*1111", "*2222", "*1111", "*2222", "*1111"],
        "Сумма операции": [-100.50, -500.00, -200.25, 1000.00, -50.00],
        "Кэшбэк": [1.00, 5.00, 2.00, 0.00, 0.50],
    }
    return pd.DataFrame(data)


@pytest.fixture
def get_card_stats_expected():
    return [
        {"last_digits": "*1111", "total_spent": 350.75, "cashback": 3.50},
        {"last_digits": "*2222", "total_spent": 500.00, "cashback": 5.00},
    ]


@pytest.fixture
def find_top_five_transactions_data():
    data = {
        "Дата операции": [
            datetime.datetime(2026, 11, 1, 10, 0, 0),
            datetime.datetime(2026, 11, 2, 14, 30, 0),
            datetime.datetime(2026, 11, 3, 18, 15, 0),
            datetime.datetime(2026, 11, 4, 9, 0, 0),
            datetime.datetime(2026, 11, 5, 21, 45, 0),
            datetime.datetime(2026, 11, 6, 23, 0, 0),
        ],
        "Сумма операции": [-150.0, 5000.0, -10000.0, 50.0, -2500.0, 300.0],
        "Категория": ["Супермаркеты", "Зарплата", "Переводы", "Фастфуд", "Одежда", "Такси"],
        "Описание": ["Пятерочка", "Аванс", "Маме", "Макдак", "Зара", "Яндекс"],
    }
    return pd.DataFrame(data)
