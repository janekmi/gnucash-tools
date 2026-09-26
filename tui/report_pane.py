# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from textual.widgets import TabPane, DataTable
from textual.app import ComposeResult
from gnucash_model import GnuCashModel
from gnucash_reports import GnuCashCustomReport, GnuCash12MonthReport
from monthyear_picker import MonthYear


COLUMNS = ["Account", "Deposit", "Withdrawal"]


class ReportPane(TabPane):
    def __init__(
        self,
        monthyear: MonthYear,
        model: GnuCashModel,
        *args,
        **kwargs,
    ) -> None:
        super().__init__("12 month report", *args, **kwargs)
        self._monthyear = monthyear
        self._year = monthyear._year
        self._month = monthyear._month
        self._model = model
        self._report = GnuCash12MonthReport(model, self._year, self._month)

    def compose(self) -> ComposeResult:
        """Create child widgets of an account pane."""
        yield DataTable()

    def _load_data(self) -> None:
        rows = [
            (GnuCashCustomReport.INCOME_PATH, self._report.income),
            (GnuCashCustomReport.EXPENSES_PATH, self._report.expense),
            (GnuCashCustomReport.LIABILITIES_PATH, self._report.liabilities),
        ]
        for row in rows:
                self._table.add_row(*row)

    def on_mount(self) -> None:
        self._table = self.query_one(DataTable)
        self._table.add_columns(*COLUMNS)
        self._load_data()
        self._table.move_cursor(row=0, column=0)
        self._table.focus()

    def update_monthyear(self) -> None:
        self._year = self._monthyear._year
        self._month = self._monthyear._month
        self._table.clear()
        self._report = GnuCash12MonthReport(model, self._year, self._month)
        self._load_data()
        self._table.move_cursor(row=0, column=0)
        self._table.focus()
