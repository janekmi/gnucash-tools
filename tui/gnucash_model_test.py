#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

import argparse
import yaml

from pathlib import Path
from gnucash_model import GnuCashModel, GnuCashAccount, GnuCashTransaction


# Arguments
parser = argparse.ArgumentParser(description="Apply rules")
parser.add_argument(
    "--gnucash_file",
    type=Path,
    required=True,
    help="Path to the GnuCash file (.gnucash, .xac, etc.)"
)


def print_helper(txn: GnuCashTransaction) -> None:
    print("---")
    print(f"Date:          {txn.date}")
    print(f"Year:          {txn.year}")
    print(f"Month:         {txn.month}")
    print(f"Description:   {txn.description}")
    print(f"Deposit:       {txn.deposit}")
    print(f"Withdrawal:    {txn.withdrawal}")
    print(f"Other account: {txn.other_account.name}")


def test00(model: GnuCashModel) -> None:
    print(yaml.safe_dump(model.accounts_tree, sort_keys=False, default_flow_style=False))


def test01(model: GnuCashModel) -> None:
    account = model.get_account_by_path("Assets/Starling")
    print(account.name)
    for _, txn in enumerate(account.transactions[:1]):
        print_helper(txn)


def test02(model: GnuCashModel) -> None:
    account = model.get_account_by_path("Assets/Starling")
    print(account.name)
    for _, txn in enumerate(account.get_transactions_by_month(2026, 8)):
        print_helper(txn)


def test03(model: GnuCashModel) -> None:
    def filter(txn: GnuCashTransaction) -> bool:
        return txn.description == "eBay"
    account = model.get_account_by_path("Assets/Starling")
    print(account.name)
    for _, txn in enumerate(account.get_transactions_with_filter(filter)):
        print_helper(txn)


def test04(model: GnuCashModel) -> None:
    account = model.get_account_by_path("Income")
    for child in account.children:
        print(child.name)


def main(model: GnuCashModel) -> None:
    # test00(model)
    test01(model)
    # test02(model)
    # test03(model)
    # test04(model)


if __name__ == "__main__":
    args = parser.parse_args()
    main(GnuCashModel(str(args.gnucash_file)))
