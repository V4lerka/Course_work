from src.reports import reports_saver_decorator, spending_by_category
import os
import pandas as pd


def test_reports_saver_decorator():
    """Тест декоратора на сохранение метаданных функции"""

    @reports_saver_decorator()
    def foo(x, y):
        """Простая тестовая функция"""
        return x / y

    assert foo.__name__ == "foo"
    assert foo.__doc__ == "Простая тестовая функция"


def test_reports_saver_decorator_work(decorator_test_data):
    """Тест работы декоратора"""
    test_filename = "test_report.xlsx"
    temp_file_xls = os.path.abspath(os.path.join(os.path.dirname(__file__), "../reports", test_filename))
    if os.path.exists(temp_file_xls):
        os.remove(temp_file_xls)

    @reports_saver_decorator(filename=test_filename)
    def foo2(transactions: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
        return transactions[(transactions["category"] == category) & (transactions["date"] == date)]

    df_result = foo2(decorator_test_data, "Продукты", "2026-11-01")
    assert isinstance(df_result, pd.DataFrame)
    assert len(df_result) == 2
    assert os.path.exists(temp_file_xls), f"Файл не был найден по пути: {temp_file_xls}"

    df_from_excel = pd.read_excel(temp_file_xls, sheet_name="Траты по категориям")
    assert len(df_from_excel) == 2
    assert list(df_from_excel["category"].unique()) == ["Продукты"]
    os.remove(temp_file_xls)


def test_spending_by_category(spending_by_category_test_data):
    """Тест базовой функции, возврат не пустого дата-фрэйма"""
    df_result = spending_by_category(spending_by_category_test_data, "Продукты", "25.06.2018")
    assert len(df_result) == 3
    assert list(df_result["Категория"].unique()) == ["Продукты"]


def test_spending_by_category_empty(spending_by_category_test_data, capsys):
    """Тест базовой функции, возврат пустого дата-фрэйма"""
    df_result = spending_by_category(spending_by_category_test_data, "Супермаркеты", "25.06.2018")
    assert df_result.empty is True
    captured = capsys.readouterr()
    assert captured.out == "Транзакции под условия фильтрации не найдены\n"


def test_spending_by_category_empty2(spending_by_category_test_data, capsys):
    """Тест, если передан пустой дата-фрэйм"""
    df_result = spending_by_category(pd.DataFrame(), "Супермаркеты", "25.06.2018")
    assert df_result.empty is True
    captured = capsys.readouterr()
    assert captured.out == "Передан пустой дата-фрэйм. Ничего не найдено.\n"


def test_spending_by_category_wrong(spending_by_category_test_data2, capsys):
    """Тест, если не найден столбец в дата-фрэйм"""
    df_result = spending_by_category(spending_by_category_test_data2, "Продукты", "25.06.2018")
    assert df_result.empty is True
    captured = capsys.readouterr()
    assert "Ошибка" in captured.out