#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

# pylint: disable=missing-module-docstring,missing-function-docstring

import argparse
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import yaml
from gnucash import Session, SessionOpenMode

# Arguments
parser = argparse.ArgumentParser(description="Apply rules")
parser.add_argument(
    "--layout",
    type=Path,
    required=True,
    help="Path to the layout.yaml file"
)
parser.add_argument(
    "--gnucash_file",
    type=Path,
    required=True,
    help="Path to the GnuCash file (.gnucash, .xac, etc.)"
)
parser.add_argument(
    "--year",
    type=int,
    required=True,
    help="Year to start process from (e.g., 2026)"
)
parser.add_argument(
    "--month",
    type=int,
    choices=range(1, 13),
    required=True,
    help="Month to start process from (1–12)"
)
parser.add_argument(
    "--num_months",
    type=int,
    default=1,
    help="Number of months to process"
)
parser.add_argument(
    "--output",
    type=Path,
    required=True,
    help="Name of the output file. Extension is added automatically."
)


# Constants
MMD_HEADER = """---
config:
  sankey:
    showValues: false
---
sankey-beta

"""
DEBUG_ACCOUNT = ''


@dataclass
class MonthRange: # pylint: disable=missing-class-docstring
    year: int
    month: int
    num_months: int


def account_lookup_by_path(account, path_str):
    def _account_lookup_by_path(account, path):
        name = path.pop(0)
        child = account.lookup_by_name(name)
        if len(path) == 0:
            return child
        return _account_lookup_by_path(child, path)
    return _account_lookup_by_path(account, path_str.split(":"))


def filter_out(dt, months):
    year = months.year
    dt1 = datetime(year, months.month, 1)
    month2 = ((months.month - 1) + months.num_months) % 12 + 1
    year += (months.month + months.num_months) // 12
    dt2 = datetime(year, month2, 1)
    return dt < dt1 or dt >= dt2


def get_transactions(account, months):
    return [
        split.parent for split in account.GetSplitList()
        if not filter_out(split.parent.GetDate(), months)]


def print_txn(txn, account_path):
    account_name = account_path.split(':')[-1]
    dts = txn.GetDate().strftime("%Y-%m-%d")
    for split in txn.GetSplitList():
        if split.GetAccount().GetName() == account_name:
            amount = split.GetAmount().to_double()
    print(f"{dts} {txn.GetDescription():20}  {amount:10.2f}")


def txn_get_amount(txn, account_path):
    account_name = account_path.split(':')[-1]
    for split in txn.GetSplitList():
        if split.GetAccount().GetName() == account_name:
            return split.GetAmount().to_double()
    raise ValueError(f'The account {account_path} does not participate in the transaction')


def get_all_transactions_sum(root, account_path, months):
    account = account_lookup_by_path(root, account_path)
    txns = get_transactions(account, months)
    if account_path == DEBUG_ACCOUNT:
        for txn in txns:
            print_txn(txn, account_path)
    values = [txn_get_amount(txn, account_path) for txn in txns]
    return sum(values)


def process(root, layout, months, output):
    nodes = {}

    for group in layout.keys():
        group_meta = group.split(':')
        group_name = group_meta[0]
        direction = group_meta[1]
        invisible = len(group_meta) > 2
        if direction == 'out':
            nodes[group_name] = 0
        for account_path in layout[group]:
            if account_path in nodes:
                account_name = account_path
                value = nodes[account_path]
            else:
                account_name = account_path.split(':')[-1]
                value = get_all_transactions_sum(root, account_path, months)
                if direction == 'in':
                    value = -value

            if direction == 'out':
                nodes[group_name] += value
            prefix = '%% ' if invisible or value <= 0 else ''
            if direction == 'in':
                output.write(f'{prefix}{account_name},{group_name},{value:.2f}\n')
            else:
                output.write(f'{prefix}{group_name},{account_name},{value:.2f}\n')


def main():
    args = parser.parse_args()

    months = MonthRange(args.year, args.month, args.num_months)

    with open(args.layout, "r", encoding="utf-8") as f:
        layout = yaml.safe_load(f)

    with Session(str(args.gnucash_file), mode=SessionOpenMode.SESSION_READ_ONLY) as session:
        book = session.book
        root = book.get_root_account()
        with open(str(args.output) + '.mmd', "w", encoding="utf-8") as output:
            output.write(MMD_HEADER)
            process(root, layout, months, output)


if __name__ == "__main__":
    main()
