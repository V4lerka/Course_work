import datetime

import pandas as pd
import pytest

from src.services import get_best_cashback


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


@pytest.fixture
def decorator_test_data():
    return pd.DataFrame(
        [
            {"amount": 500, "category": "Продукты", "date": "2026-11-01"},
            {"amount": 1200, "category": "Транспорт", "date": "2026-11-02"},
            {"amount": 300, "category": "Продукты", "date": "2026-11-01"},
        ]
    )


@pytest.fixture
def spending_by_category_test_data():
    return pd.DataFrame(
        [
            {"Сумма операции": -500, "Категория": "Продукты", "Дата операции": "15.05.2018 12:25:19", "Статус": "OK"},
            {"Сумма операции": -200, "Категория": "Продукты", "Дата операции": "10.05.2018 17:25:29", "Статус": "OK"},
            {"Сумма операции": -1500, "Категория": "Продукты", "Дата операции": "25.04.2018 10:25:39", "Статус": "OK"},
            {"Сумма операции": -150, "Категория": "Транспорт", "Дата операции": "15.05.2019 11:25:19", "Статус": "OK"},
            {
                "Сумма операции": -100,
                "Категория": "Продукты",
                "Дата операции": "25.04.2018 10:25:39",
                "Статус": "FAILED",
            },
        ]
    )


@pytest.fixture()
def get_best_cashback_test_data():
    return pd.DataFrame(
        {
            "Дата платежа": [
                "05.11.2026",
                "12.11.2026",
                "25.11.2026",
                "01.12.2026",
                "15.11.2025",
                None,
                "18.11.2026",
                "20.11.2026",
            ],
            "Категория": [
                "Супермаркеты",
                "Такси",
                "Супермаркеты",
                "Супермаркеты",
                "Фастфуд",
                "Одежда",
                "Книги",
                "Развлечения",
            ],
            "Кэшбэк": [
                150.0,  # Супермаркеты
                45.6,  # Такси (округлится до 46)
                100.2,  # Супермаркеты (в сумме станет 250.2 -> 250)
                300.0,  # Игнорируется (декабрь)
                50.0,  # Игнорируется (2025 год)
                20.0,  # Игнорируется (нет даты)
                0.0,  # Игнорируется (кэшбэк == 0)
                -10.0,  # Игнорируется (кэшбэк < 0)
            ],
        }
    )

@pytest.fixture
def result_data_get_best_cashback():
    return {
        "Супермаркеты": 250,
        "Такси": 46}

@pytest.fixture()
def get_best_cashback_test_data2():
    return pd.DataFrame(
        {
            "Дата": [
                "05.11.2026",
                "12.11.2026",
                "25.11.2026",
                "01.12.2026",
                "15.11.2025",
                None,
                "18.11.2026",
                "20.11.2026",
            ],
            "Категория": [
                "Супермаркеты",
                "Такси",
                "Супермаркеты",
                "Супермаркеты",
                "Фастфуд",
                "Одежда",
                "Книги",
                "Развлечения",
            ],
            "Кэшбэк": [
                150.0,
                45.6,
                100.2,
                300.0,
                50.0,
                20.0,
                0.0,
                -10.0,
            ],
        }
    )

@pytest.fixture
def spending_by_category_test_data2():
    return pd.DataFrame(
        [
            {"Сумма": -500, "Категория": "Продукты", "Дата": "15.05.2018 12:25:19", "Статус": "OK"},
            {"Сумма": -200, "Категория": "Продукты", "Дата": "10.05.2018 17:25:29", "Статус": "OK"},
            {"Сумма": -1500, "Категория": "Продукты", "Дата": "25.04.2018 10:25:39", "Статус": "OK"},
            {"Сумма": -150, "Категория": "Транспорт", "Дата": "15.05.2019 11:25:19", "Статус": "OK"},
            {
                "Сумма": -100,
                "Категория": "Продукты",
                "Дата": "25.04.2018 10:25:39",
                "Статус": "FAILED",
            },
        ]
    )
@pytest.fixture
def transform_expenses_to_list_test_data():
    return pd.DataFrame(
            {
                "Дата операции": [
                    "15.11.2026 14:30:00",
                    "16.11.2026 09:15:22",
                    "17.11.2026 18:00:10",
                    "18.11.2026 23:59:59",
                    "19.11.2026 10:20:00",
                ],
                "Сумма операции": [
                    -1500.50,
                    -5000.00,
                    2500.00,
                    -50.00,
                    -300.00,
                ],
                "Валюта операции": ["RUB", "RUB", "RUB", "USD", "RUB"],
                "Категория": ["Супермаркеты", "Переводы", "Красота", "Фастфуд", "Такси"],
            }
        )

@pytest.fixture
def transform_expenses_to_list_result_data():
    return [
            {"Дата операции": "2026-11-15", "Сумма операции": -1500.50},
            {"Дата операции": "2026-11-19", "Сумма операции": -300.00},
        ]

@pytest.fixture
def transform_expenses_to_list_test_data2():
    return pd.DataFrame(
            {
                "Дата": [
                    "15.11.2026 14:30:00",
                    "16.11.2026 09:15:22",
                    "17.11.2026 18:00:10",
                    "18.11.2026 23:59:59",
                    "19.11.2026 10:20:00",
                ],
                "Сумма операции": [
                    -1500.50,
                    -5000.00,
                    2500.00,
                    -50.00,
                    -300.00,
                ],
                "Валюта операции": ["RUB", "RUB", "RUB", "USD", "RUB"],
                "Категория": ["Супермаркеты", "Переводы", "Красота", "Фастфуд", "Такси"],
            }
        )

@pytest.fixture
def bank_transactions_test_data():
    return [
        {
            "Дата операции": "15.11.2026 14:30:00",
            "Сумма операции": -120.0,
        },
        {
            "Дата операции": "16.11.2026 09:15:22",
            "Сумма операции": -100.0,
        },
        {
            "Дата операции": "01.12.2026 18:00:10",
            "Сумма операции": -230.0,
        },
        {
            "Дата операции": "19.11.2026 10:20:00",
            "Сумма операции": -45.5,
        },
    ]

@pytest.fixture
def remittance_test_data():
    return pd.DataFrame(
        {
            "Категория": [
                "Переводы",
                "Переводы",
                "Супермаркеты",
                "Переводы",
                "Переводы",
                "Переводы",
            ],
            "Статус": ["OK", "OK", "OK", "FAILED", "OK", "OK"],
            "Описание": [
                "Перевод Иван И.",
                "Перевод в ООО Ромашка",
                "Покупка продуктов",
                "Перевод Петр С.",
                "Перевод Анна Б. другу",
                None,
            ],
            "Сумма": [-500, -1000, -150, -300, -200, -100],
        }
    )

@pytest.fixture
def remittance_test_data2():
    return pd.DataFrame(
        {
            "Категория": [
                "Переводы",
                "Переводы",
                "Супермаркеты",
                "Переводы",
                "Переводы",
                "Переводы",
            ],
            "Статус": ["OK", "OK", "OK", "FAILED", "OK", "OK"],
            "Описание": [
                "Перевод таксисту",
                "Перевод в ООО Ромашка",
                "Покупка продуктов",
                "Перевод себе",
                "Перевод другу",
                None,
            ],
            "Сумма": [-500, -1000, -150, -300, -200, -100],
        }
    )

@pytest.fixture
def remittance_test_data3():
    return pd.DataFrame(
        {
            "Категория": [
                "Переводы",
                "Переводы",
                "Супермаркеты",
                "Переводы",
                "Переводы",
                "Переводы",
            ],
            "Статус": ["OK", "OK", "OK", "FAILED", "OK", "OK"],
            "Описание операции": [
                "Перевод Иван И.",
                "Перевод в ООО Ромашка",
                "Покупка продуктов",
                "Перевод Петр С.",
                "Перевод Анна Б. другу",
                None,
            ],
            "Сумма": [-500, -1000, -150, -300, -200, -100],
        }
    )
