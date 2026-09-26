# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from textual.widgets import TabPane, DataTable
from textual.app import ComposeResult
from gnucash_model import GnuCashModel
from monthyear_picker import MonthYear


COLUMNS = ["Date", "Description", "Deposit", "Withdrawal"]


class AccountPane(TabPane):
    def __init__(
        self,
        label: str,
        monthyear: MonthYear,
        model: GnuCashModel,
        path: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(label, *args, **kwargs)
        self._monthyear = monthyear
        self._year = monthyear._year
        self._month = monthyear._month
        self._model = model
        self._path = path
        self._account = self._model.get_account_by_path(self._path)

    def compose(self) -> ComposeResult:
        """Create child widgets of an account pane."""
        yield DataTable()

    def _load_data(self) -> None:
        for index, txn in enumerate(self._account.get_transactions_by_date(self._year, self._month)):
                self._table.add_row(
                    txn.date,
                    txn.description,
                    txn.deposit,
                    txn.withdrawal
                )

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
        self._load_data()
        self._table.move_cursor(row=0, column=0)
        self._table.focus()
