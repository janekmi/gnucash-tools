# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

"""TabPane variants displaying various GnuCash data."""

from textual.widgets import TabPane, DataTable
from textual.app import ComposeResult
from gnucash_model import GnuCashModel
from monthyear_picker import MonthYear
from gnucash_reports import GnuCashCustomReport, GnuCash12MonthReport


class GnuCashPane(TabPane):
    """Parent class taking care of composing and updating the contents"""
    COLUMNS = ["TBD"]

    def __init__(
        self,
        label: str,
        monthyear: MonthYear,
        model: GnuCashModel,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(label, *args, **kwargs)
        self._monthyear = monthyear
        self.year = monthyear.year
        self.month = monthyear.month
        self._model = model
        self._table = None

    def compose(self) -> ComposeResult:
        """Just add the DataTable."""
        yield DataTable(zebra_stripes=True)

    def load_data(self) -> None:
        """To be implemented by derivative classes."""

    def on_mount(self) -> None:
        """Take care of the loading process."""
        self._table = self.query_one(DataTable)
        self._table.add_columns(*self.COLUMNS)
        self.load_data()
        self._table.move_cursor(row=0, column=0)
        self._table.focus()

    def update_monthyear(self) -> None:
        """Refresh the contents after a different month got chosen."""
        self.year = self._monthyear.year
        self.month = self._monthyear.month
        self._table.clear()
        self.load_data()
        self._table.move_cursor(row=0, column=0)
        self._table.focus()


class AccountPane(GnuCashPane):
    """A pane displaying the contents of an account."""
    COLUMNS = ["Date", "Description", "Deposit", "Withdrawal", "Other account"]

    def __init__(
        self,
        label: str,
        path: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(label, *args, **kwargs)
        self._path = path
        self._account = self._model.get_account_by_path(self._path)

    def load_data(self) -> None:
        for _, txn in enumerate(
            self._account.get_transactions_by_month(self.year, self.month)):
            self._table.add_row(
                txn.date,
                txn.description,
                txn.deposit_str,
                txn.withdrawal_str,
                "---" if txn.is_multi_split else txn.other_account.name
            )


class ReportPane(GnuCashPane):
    """A pane displaying a 12 Month Report."""
    COLUMNS = ["Account", "Deposit", "Withdrawal"]

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__("12 month report", *args, **kwargs)

    def load_data(self) -> None:
        report = GnuCash12MonthReport(self._model, self.year, self.month)
        rows = [
            (GnuCashCustomReport.INCOME_PATH,
            report.income.deposit_str, report.income.withdrawal_str),
            (GnuCashCustomReport.EXPENSES_PATH,
            report.expense.deposit_str, report.expense.withdrawal_str),
            (GnuCashCustomReport.LIABILITIES_PATH,
            report.liabilities.deposit_str, report.liabilities.withdrawal_str),
        ]
        for row in rows:
            self._table.add_row(*row)
        self._table.add_row()
        self._table.add_row("Sum", report.deposit_str, report.withdrawal_str)
        self._table.add_row("Total", report.total.deposit_str, report.total.withdrawal_str)
