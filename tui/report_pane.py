# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from gnucash_model import GnuCashAmount
from gnucash_pane import GnuCashPane
from gnucash_reports import GnuCashCustomReport, GnuCash12MonthReport


class ReportPane(GnuCashPane):
    COLUMNS = ["Account", "Deposit", "Withdrawal"]

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__("12 month report", *args, **kwargs)

    def load_data(self) -> None:
        report = GnuCash12MonthReport(self._model, self._year, self._month)
        rows = [
            (GnuCashCustomReport.INCOME_PATH, report.income.deposit_str, report.income.withdrawal_str),
            (GnuCashCustomReport.EXPENSES_PATH, report.expense.deposit_str, report.expense.withdrawal_str),
            (GnuCashCustomReport.LIABILITIES_PATH, report.liabilities.deposit_str, report.liabilities.withdrawal_str),
        ]
        for row in rows:
                self._table.add_row(*row)
