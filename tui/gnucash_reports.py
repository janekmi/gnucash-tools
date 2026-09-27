# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from typing import Callable
from gnucash_model import GnuCashModel, GnuCashAccount, GnuCashTransaction, GnuCashAmount


class GnuCashCustomReport:
    INCOME_PATH = "Income"
    EXPENSES_PATH = "Expenses"
    LIABILITIES_PATH = "Liabilities"

    def __init__(self, model: GnuCashModel, filter: Callable[[GnuCashTransaction], bool]):
        def _sum_account_and_children(account: GnuCashAccount, filter: Callable[[GnuCashTransaction], bool]) -> float:
            sum: float = 0.0
            for tx in account.get_transactions_with_filter(filter):
                # print(tx.description)
                sum += tx.amount
            for child in account.children:
                sum += _sum_account_and_children(child, filter)
            return sum
        self._model = model
        # income
        account = model.get_account_by_path(self.INCOME_PATH)
        self._income = GnuCashAmount(_sum_account_and_children(account, filter))
        # expense
        account = model.get_account_by_path(self.EXPENSES_PATH)
        self._expense = GnuCashAmount(_sum_account_and_children(account, filter))
        # liabilities
        account = model.get_account_by_path(self.LIABILITIES_PATH)
        self._liabilities = GnuCashAmount(_sum_account_and_children(account, filter))

    @property
    def income(self):
        return self._income

    @property
    def expense(self):
        return self._expense
    
    @property
    def liabilities(self):
        return self._liabilities

    @property
    def deposit(self):
        return self._income.deposit + self._expense.deposit + self._liabilities.deposit

    @property
    def withdrawal(self):
        return self._income.withdrawal + self._expense.withdrawal + self._liabilities.withdrawal

    @property
    def deposit_str(self):
        return GnuCashAmount.format(self.deposit)

    @property
    def withdrawal_str(self):
        return GnuCashAmount.format(self.withdrawal)

    @property
    def total(self):
        return GnuCashAmount(self.deposit - self.withdrawal)


class GnuCashMonthReport(GnuCashCustomReport):
    def __init__(self, model: GnuCashModel, year: int, month: int):
        def filter(tx: GnuCashTransaction) -> bool:
            return tx.date.startswith(f"{year}-{month:02d}")
        super().__init__(model, filter)


class GnuCash12MonthReport(GnuCashCustomReport):
    def __init__(self, model: GnuCashModel, year_start: int, month_start: int):
        month_end = month_start - 11
        if month_end > 0:
            year_end = year_start
        else:
            month_end += 12
            year_end = year_start - 1
        def filter(tx: GnuCashTransaction) -> bool:
            if tx.year == year_start:
                return tx.month <= month_start
            elif tx.year == year_end:
                return tx.month >= month_end
        super().__init__(model, filter)
