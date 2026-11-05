import json
import os
from unittest.mock import patch

import pandas as pd

from src.services import (
    excel_file_reader,
    find_remittance_to_people,
    get_best_cashback,
    investment_bank,
    transform_expenses_to_list,
)


def test_excel_file_reader_false_extension(capsys):
    """Тест неверного расширения"""
    result = excel_file_reader("operations.txt")
    assert result.empty is True
    captured = capsys.readouterr()
    assert captured.out == "Неверный формат файла\n"


def test_excel_file_reader_ok(spending_by_category_test_data):
    """Успешный тест"""
    tmp_file_name = "fake.xlsx"
    path_to_tmp_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data", f"{tmp_file_name}"))
    spending_by_category_test_data.to_excel(path_to_tmp_file, index=False, sheet_name="Отчет по операциям")
    df_result = excel_file_reader(tmp_file_name)
    assert len(df_result) == 5
    assert list(df_result["Категория"].unique()) == ["Продукты", "Транспорт"]
    os.remove(path_to_tmp_file)


def test_excel_file_reader(capsys):
    """Тест с пустым файлом, ошибка чтения"""
    tmp_file_name = "fake.xlsx"
    path_to_tmp_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data", f"{tmp_file_name}"))
    pd.DataFrame().to_excel(path_to_tmp_file, index=False)
    df_result = excel_file_reader(tmp_file_name)
    captured = capsys.readouterr()
    assert df_result.empty is True
    assert "Возникла непредвиденная ошибка чтения файла" in captured.out
    os.remove(path_to_tmp_file)


def test_excel_file_reader_not_found(capsys):
    """Тест, если файл не найден"""

    def mock_open_raise_error(*args, **kwargs):
        raise FileNotFoundError("[Errno 2] No such file or directory")

    with (
        patch("builtins.open", mock_open_raise_error),
        patch("os.path.abspath", return_value="/fake/path/missing.xlsx"),
    ):
        result = excel_file_reader("missing.xlsx")
    assert result.empty is True
    captured = capsys.readouterr()
    assert "Ошибка: [Errno 2] No such file or directory" in captured.out


def test_get_best_cashback_ok(get_best_cashback_test_data, result_data_get_best_cashback):
    """Успешный тест"""
    result = get_best_cashback(11, 2026, get_best_cashback_test_data)
    assert result == json.dumps(result_data_get_best_cashback, indent=4, ensure_ascii=False)


def test_get_best_cashback_not_found(get_best_cashback_test_data, result_data_get_best_cashback, capsys):
    """Тест, если категории не найдены"""
    result = get_best_cashback(11, 2024, get_best_cashback_test_data)
    assert result == json.dumps({})
    captured = capsys.readouterr()
    assert captured.out == "Выгодные категории кэшбэка не найдены\n"


def test_get_best_cashback_empty(capsys):
    """Тест, если передан пустой дата-фрэйм"""
    result = get_best_cashback(11, 2024, pd.DataFrame())
    assert result == json.dumps({})
    captured = capsys.readouterr()
    assert captured.out == "Передан пустой дата-фрэйм. Ничего не найдено.\n"


def test_get_best_cashback_wrong_column(get_best_cashback_test_data2, capsys):
    """Тест, если столбец фрэйма не найден"""
    result = get_best_cashback(11, 2024, get_best_cashback_test_data2)
    assert result == json.dumps({})
    captured = capsys.readouterr()
    assert "Ошибка" in captured.out


def test_transform_expenses_to_list_ok(transform_expenses_to_list_test_data, transform_expenses_to_list_result_data):
    """Успешный тест"""
    result = transform_expenses_to_list(transform_expenses_to_list_test_data, "RUB")
    assert result == transform_expenses_to_list_result_data


def test_transform_expenses_to_list_empty(capsys):
    """Тест, если передан пустой дата-фрэйм"""
    result = transform_expenses_to_list(pd.DataFrame(), "RUB")
    assert result == []
    captured = capsys.readouterr()
    assert captured.out == "Передан пустой дата-фрэйм. Ничего не найдено.\n"


def test_transform_expenses_to_list_failed(transform_expenses_to_list_test_data2, capsys):
    """Тест, если столбец фрэйма не найден"""
    result = transform_expenses_to_list(transform_expenses_to_list_test_data2, "RUB")
    assert result == []
    captured = capsys.readouterr()
    assert "Ошибка" in captured.out


def test_investment_bank_ok(bank_transactions_test_data):
    """Успешный тест"""
    result = investment_bank("11.2026", bank_transactions_test_data, 50)
    assert result == 34.5


def test_investment_bank_empty_list(capsys):
    """Передан пустой список"""
    result = investment_bank("11.2026", [], 50)
    assert result == 0.0
    captured = capsys.readouterr()
    assert captured.out == "Список транзакций пуст\n"


def test_investment_bank_not_found(bank_transactions_test_data, capsys):
    """Не найдены транзакции"""
    result = investment_bank("10.2026", bank_transactions_test_data, 50)
    assert result == 0.0
    captured = capsys.readouterr()
    assert captured.out == "Операции, подходящие под условия фильтрации не найдены\n"


def test_find_remittance_to_people_ok(remittance_test_data):
    """Успешный тест"""
    result = find_remittance_to_people(remittance_test_data)
    result_list = json.loads(result)
    assert len(result_list) == 2
    assert result_list[0]["Описание"] == "Перевод Иван И."
    assert result_list[1]["Описание"] == "Перевод Анна Б. другу"


def test_find_remittance_to_people_not_found(remittance_test_data2, capsys):
    """Тест возврата пустого JSON-объекта, если подходящих переводов нет"""
    result = find_remittance_to_people(remittance_test_data2)
    assert result == json.dumps({})
    captured = capsys.readouterr()
    assert captured.out == "Транзакции не найдены\n"


def test_find_remittance_to_people_empty(capsys):
    """Тест возврата пустого JSON-объекта, если передан пустой датафрэйм"""
    result = find_remittance_to_people(pd.DataFrame())
    assert result == json.dumps({})
    captured = capsys.readouterr()
    assert captured.out == "Передан пустой дата-фрэйм. Ничего не найдено.\n"


def test_find_remittance_to_people_error(remittance_test_data3, capsys):
    """Тест возврата пустого JSON-объекта, если Key Error"""
    result = find_remittance_to_people(remittance_test_data3)
    assert result == json.dumps({})
    captured = capsys.readouterr()
    assert "Ошибка" in captured.out
