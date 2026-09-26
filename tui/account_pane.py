# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from gnucash_pane import GnuCashPane


class AccountPane(GnuCashPane):
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
        for index, txn in enumerate(self._account.get_transactions_by_month(self._year, self._month)):
                self._table.add_row(
                    txn.date,
                    txn.description,
                    txn.deposit,
                    txn.withdrawal,
                    "---" if txn.is_multi_split else txn.other_account.name
                )
