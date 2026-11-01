import json
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest
from requests import RequestException

import src.views
from src.views import (
    file_reader,
    find_top_five_transactions,
    get_card_stats,
    get_currency_rate,
    get_stock_rate,
    open_settings,
)


def test_open_settings_false_extension(capsys):
    """Тест неверного расширения"""
    result = open_settings("user_settings.txt")
    assert result == {}
    captured = capsys.readouterr()
    assert captured.out == "Неверный формат файла настроек\n"


def test_open_settings_ok(json_file_content):
    """Успешный тест"""
    file_content = json.dumps(json_file_content)
    mocked_file = mock_open(read_data=file_content)
    with patch("builtins.open", mocked_file), patch("os.path.abspath", return_value="/fake/path/fake.json"):
        result = open_settings("fake.json")
    assert result == json_file_content


def test_open_settings_error(capsys):
    """Тест с пустым файлом, ошибка чтения"""
    file_content = ""
    mocked_file = mock_open(read_data=file_content)
    with patch("builtins.open", mocked_file), patch("os.path.abspath", return_value="/fake/path/fake.json"):
        result = open_settings("fake.json")
    captured = capsys.readouterr()
    assert result == {}
    assert captured.out == "Ошибка чтения файла: Expecting value: line 1 column 1 (char 0)\n"


def test_open_settings_file_not_found(capsys):
    """Тест, если файл не найден"""

    def mock_open_raise_error(*args, **kwargs):
        raise FileNotFoundError("[Errno 2] No such file or directory")

    with (
        patch("builtins.open", mock_open_raise_error),
        patch("os.path.abspath", return_value="/fake/path/missing.json"),
    ):
        result = open_settings("missing.json")
    assert result == {}
    captured = capsys.readouterr()
    assert "Ошибка: [Errno 2] No such file or directory" in captured.out


def test_get_currency_rate_empty_settings():
    """Тест, если переданы пустые настройки"""
    result = get_currency_rate({})
    assert result == []


def test_get_currency_rate_ok(json_file_content, response_get_currency_rate, result_get_currency_rate):
    """Успешный ответ от API: выдается обменный курс"""
    mock_response = Mock()
    mock_response.json.return_value = response_get_currency_rate
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_response
        assert get_currency_rate(json_file_content) == result_get_currency_rate
    mock_get.assert_called_once()


def test_get_currency_rate_failed(json_file_content, response_get_currency_rate_empty):
    """Сервер ответил (код 200), но конвертация не прошла (словарь conversion rates пуст)"""
    mock_response = Mock()
    mock_response.json.return_value = response_get_currency_rate_empty
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_response
        assert get_currency_rate(json_file_content) == []
    mock_get.assert_called_once()


def test_get_currency_rate_http_error(json_file_content, capsys):
    """Тест ошибочных запросов"""

    def raise_http_error():
        raise RequestException("Ошибка сервера или неверный API-ключ")

    mock_response = Mock()
    mock_response.raise_for_status = raise_http_error
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_response
        result = get_currency_rate(json_file_content)
        assert result == []
        captured = capsys.readouterr()
        assert "Ошибка при конвертации валюты" in captured.out


def test_get_stock_rate_empty_settings(capsys):
    """Тест, если переданы пустые настройки"""
    result = get_stock_rate({})
    assert result == []
    captured = capsys.readouterr()
    assert captured.out == "Ошибка. Отсутсвуют входные данные.\n"


def test_get_stock_rate_http_error(json_file_content, capsys):
    """Тест ошибочных запросов"""

    def raise_http_error():
        raise RequestException("Ошибка сервера или неверный API-ключ")

    mock_response = Mock()
    mock_response.raise_for_status = raise_http_error
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_response
        result = get_stock_rate(json_file_content)
        assert result == []
        captured = capsys.readouterr()
        assert "Ошибка при запросе информации об акциях" in captured.out


def test_get_stock_rate_failed(json_file_content, response_get_stock_empty, result_get_stock_empty, capsys):
    """Сервер ответил (код 200), но конвертация не прошла (словарь Global Quote пуст)"""
    mock_response = Mock()
    mock_response.json.return_value = response_get_stock_empty
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_response
        assert get_stock_rate(json_file_content) == result_get_stock_empty
        captured = capsys.readouterr()
        assert captured.out == (
            "Ошибка. Стоимость акций NVDA не определена\n"
            "Ошибка. Стоимость акций AAPL не определена\n"
            "Ошибка. Стоимость акций MSFT не определена\n"
        )
    mock_get.assert_called()


def test_get_stock_rate_success(json_file_content, response_get_stock_ok, result_get_stock_ok):
    """Успешный тест"""
    mock_response = Mock()
    mock_response.json.return_value = response_get_stock_ok
    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_response
        assert get_stock_rate(json_file_content) == result_get_stock_ok
    mock_get.assert_called()


@pytest.mark.parametrize(
    "current_time, expected",
    [
        ("2026-11-01 10-00-00", "Доброе утро!"),
        ("2026-11-01 14-00-00", "Добрый день!"),
        ("2026-11-01 19-00-00", "Добрый вечер!"),
        ("2026-11-01 02-00-00", "Доброй ночи!"),
    ],
)
def test_user_greeting(current_time, expected):
    target_path = f"{src.views.__name__}.datetime"
    with patch(target_path) as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = current_time
        assert src.views.user_greeting() == expected


def test_file_reader_wrong_extension(capsys):
    """Тест неверного расширения файла"""
    result = file_reader("21.10.2019", "operations.txt")
    assert result.empty is True
    captured = capsys.readouterr()
    assert captured.out == "Формат файла не поддерживается\n"


def test_file_reader_error(capsys):
    """Тест с пустым файлом, ошибка чтения"""
    file_content = ""
    mocked_file = mock_open(read_data=file_content)
    with patch("builtins.open", mocked_file), patch("os.path.abspath", return_value="/fake/path/fake.xlsx"):
        result = file_reader("21.10.2019", "fake.xlsx")
    assert result.empty is True
    captured = capsys.readouterr()
    assert "Возникла непредвиденная ошибка чтения файла" in captured.out


def test_file_reader_file_not_found(capsys):
    """Тест, если файл не найден"""

    def mock_open_raise_error(*args, **kwargs):
        raise FileNotFoundError("[Errno 2] No such file or directory")

    with (
        patch("builtins.open", mock_open_raise_error),
        patch("os.path.abspath", return_value="/fake/path/missing.xlsx"),
    ):
        result = file_reader("21.10.2019", "missing.xlsx")
    assert result.empty is True
    captured = capsys.readouterr()
    assert "Ошибка: [Errno 2] No such file or directory" in captured.out


def test_get_card_stats_empty(capsys):
    """Тест с пустым дата-фрэймом"""
    result = get_card_stats(pd.DataFrame({}))
    assert result == []
    captured = capsys.readouterr()
    assert captured.out == "Данные об операциях отсутствуют\n"


def test_get_card_stats_ok(get_card_stats_data, get_card_stats_expected):
    """Успешный тест"""
    result = get_card_stats(get_card_stats_data)
    assert sorted(result, key=lambda x: x["last_digits"]) == sorted(
        get_card_stats_expected, key=lambda x: x["last_digits"]
    )


def test_find_top_five_transactions_empty(capsys):
    """Тест с пустым дата-фрэймом"""
    result = find_top_five_transactions(pd.DataFrame({}))
    assert result == []
    captured = capsys.readouterr()
    assert captured.out == "Данные об операциях отсутствуют\n"


def test_find_top_five_transactions_ok(find_top_five_transactions_data):
    """Успешный тест"""
    result = find_top_five_transactions(find_top_five_transactions_data)
    assert len(result) == 5

    assert result[0] == {"date": "03.11.2026", "amount": -10000.0, "category": "Переводы", "description": "Маме"}
    assert result[1] == {"date": "02.11.2026", "amount": 5000.0, "category": "Зарплата", "description": "Аванс"}
    assert result[2] == {"date": "05.11.2026", "amount": -2500.0, "category": "Одежда", "description": "Зара"}
    assert result[3] == {"date": "06.11.2026", "amount": 300.0, "category": "Такси", "description": "Яндекс"}
    assert result[4] == {
        "date": "01.11.2026",
        "amount": -150.0,
        "category": "Супермаркеты",
        "description": "Пятерочка",
    }
