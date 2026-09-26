# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from textual.widgets import TabPane, DataTable
from textual.app import ComposeResult
from gnucash_model import GnuCashModel
from monthyear_picker import MonthYear


class GnuCashPane(TabPane):
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
        self._year = monthyear._year
        self._month = monthyear._month
        self._model = model

    def compose(self) -> ComposeResult:
        """Create child widgets of an account pane."""
        yield DataTable()

    def load_data(self) -> None:
        pass

    def on_mount(self) -> None:
        self._table = self.query_one(DataTable)
        self._table.add_columns(*self.COLUMNS)
        self.load_data()
        self._table.move_cursor(row=0, column=0)
        self._table.focus()

    def update_monthyear(self) -> None:
        self._year = self._monthyear._year
        self._month = self._monthyear._month
        self._table.clear()
        self.load_data()
        self._table.move_cursor(row=0, column=0)
        self._table.focus()
