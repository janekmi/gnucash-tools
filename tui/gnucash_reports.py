# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from typing import Callable
from gnucash_model import GnuCashModel, GnuCashAccount, GnuCashTransaction


class GnuCashIncomeExpenseMonthReport:
    INCOME_PATH = "Income"
    EXPENSES_PATH = "Expenses"
    LIABILITIES_PATH = "Liabilities"

    def __init__(self, model: GnuCashModel, year: int, month: int):
        def _sum_account_and_children(account: GnuCashAccount, year: int, month: int) -> float:
            sum: float = 0.0
            for tx in account.get_transactions_by_month(year, month):
                # print(tx.description)
                sum += tx.amount
            for child in account.children:
                sum += _sum_account_and_children(child, year, month)
            return sum
        self._model = model
        # income
        account = model.get_account_by_path(self.INCOME_PATH)
        self._income: float = _sum_account_and_children(account, year, month)
        # expense
        account = model.get_account_by_path(self.EXPENSES_PATH)
        self._expense: float = _sum_account_and_children(account, year, month)
        # liabilities
        account = model.get_account_by_path(self.LIABILITIES_PATH)
        self._liabilities: float = _sum_account_and_children(account, year, month)

    @property
    def income(self):
        return self._income

    @property
    def expense(self):
        return self._expense
    
    @property
    def liabilities(self):
        return self._liabilities

class GnuCashIncomeExpense12MonthReport:
    def __init__(self, model: GnuCashModel, year_init: int, month_init: int):
        self._income: float = 0
        self._expense: float = 0
        self._liabilities: float = 0
        for i in range(0, 12):
            month = month_init - i
            if month > 0:
                year = year_init
            else:
                month += 12
                year = year_init - 1
            # print(f"{year} {month}")
            rep = GnuCashIncomeExpenseMonthReport(model, year, month)
            self._income += rep.income
            self._expense += rep.expense
            self._liabilities += rep.liabilities

    @property
    def income(self):
        return self._income

    @property
    def expense(self):
        return self._expense

    @property
    def liabilities(self):
        return self._liabilities
