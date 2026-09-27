# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

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
            (GnuCashCustomReport.INCOME_PATH, report.income.deposit, report.income.withdrawal),
            (GnuCashCustomReport.EXPENSES_PATH, report.expense.deposit, report.expense.withdrawal),
            (GnuCashCustomReport.LIABILITIES_PATH, report.liabilities.deposit, report.liabilities.withdrawal),
        ]
        for row in rows:
                self._table.add_row(*row)
