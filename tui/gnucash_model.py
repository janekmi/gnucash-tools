# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from __future__ import annotations

from gnucash import Session, SessionOpenMode

class GnuCashTransaction:
    def __init__(self, account: GnuCashAccount, transaction):
        self._account = account
        self._transaction = transaction
        self._is_multi_split = len(transaction.GetSplitList()) > 2
        for split in self._transaction.GetSplitList():
            if split.GetAccount().GetName() == self._account.name:
                self._amount = split.GetAmount().to_double() 

    @property
    def date(self):
        return self._transaction.GetDate().strftime("%Y-%m-%d")

    @property
    def description(self) -> str:
        return self._transaction.GetDescription()

    @property
    def is_multi_split(self) -> bool:
        return self._is_multi_split

    @property
    def deposit(self) -> str:
        if self._is_multi_split:
            return "---"
        if self._amount >= 0:
            return f"{self._amount:10.2f}"
        return ""

    @property
    def withdrawal(self) -> str:
        if self._is_multi_split:
            return "---"
        if self._amount < 0:
            return f"{-self._amount:10.2f}"
        return ""


class GnuCashAccount:
    def __init__(self, account):
        self._account = account

    @property
    def name(self) -> str:
        return self._account.GetName()

    @property
    def transactions(self):
        return [GnuCashTransaction(self, split.parent) for split in self._account.GetSplitList()]

    def get_transactions_by_date(self, year: int, month: int) -> list[GnuCashTransaction]:
        return [
            tx for tx in self.transactions
            if tx.date.startswith(f"{year:04d}-{month:02d}")
        ]


class GnuCashModel:
    def __init__(self, gnucash_file: str):
        self._gnucash_file = gnucash_file
        self._session = Session(gnucash_file, mode=SessionOpenMode.SESSION_READ_ONLY)

    @property
    def gnucash_file(self) -> str:
        return self._gnucash_file

    @property
    def accounts_tree(self):
        def build_tree(account):
            return {
                "name": account.GetName(),
                "children": [
                    build_tree(child)
                    for child in account.get_children()
                ],
            }

        root_account = self._session.book.get_root_account()

        return [
            build_tree(child)
            for child in root_account.get_children()
        ]

    def get_account_by_path(self, path: str) -> GnuCashAccount:
        def find_account(account, path_parts):
            if not path_parts:
                return GnuCashAccount(account)
            child = account.lookup_by_name(path_parts[0])
            return find_account(child, path_parts[1:])

        path_parts = path.split("/")
        root_account = self._session.book.get_root_account()
        return find_account(root_account, path_parts)
