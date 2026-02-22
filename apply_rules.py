#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

# pylint: disable=missing-module-docstring,missing-function-docstring

from datetime import datetime
import yaml
from gnucash import Session, SessionOpenMode, GncNumeric
import argparse
from pathlib import Path

# Arguments
Parser = argparse.ArgumentParser(description="Apply rules")
Parser.add_argument(
    "--rules",
    type=Path,
    required=True,
    help="Path to the rules.yaml file"
)
Parser.add_argument(
    "--gnucash_file",
    type=Path,
    required=True,
    help="Path to the GnuCash file (.gnucash, .xac, etc.)"
)
Parser.add_argument(
    "--year",
    type=int,
    required=True,
    help="Year to process (e.g., 2026)"
)
Parser.add_argument(
    "--month",
    type=int,
    choices=range(1, 13),
    required=True,
    help="Month to process (1–12)"
)


# Globals
PriceDb = None

# Constants
ACCOUNTS_TO_SCAN_KEY = "Accounts to scan"
RULES_KEY = "Rules"


def account_lookup_by_path(account, path_str):
    def _account_lookup_by_path(account, path):
        name = path.pop(0)
        child = account.lookup_by_name(name)
        if len(path) == 0:
            return child
        return _account_lookup_by_path(child, path)
    return _account_lookup_by_path(account, path_str.split(":"))


def filter_out(dt, year, month):
    dt1 = datetime(year, month, 1)
    if month == 12:
        dt2 = datetime(year + 1, 1, 1)
    else:
        dt2 = datetime(year, month + 1, 1)
    return dt < dt1 or dt >= dt2


def get_transactions(account, year, month):
    return [
        split.parent for split in account.GetSplitList()
        if not filter_out(split.parent.GetDate(), year, month)]


def is_split_imbalanced(split):
    name = split.GetAccount().GetName()
    return name.startswith("Imbalance-")


def is_imbalanced(txn):
    imbalanced = [
        split for split in txn.GetSplitList()
        if is_split_imbalanced(split)]
    return len(imbalanced) != 0


def print_txn(txn):
    dts = txn.GetDate().strftime("%Y-%m-%d")
    split = txn.GetSplitList()[0]
    amount = split.GetAmount().to_double()
    print(f"{dts} {txn.GetDescription():20}  {amount:10.2f}")


def accounts_eq_commodities(src_account, dst_account):
    # get respective commodities
    src = src_account.GetCommodity().get_mnemonic()
    dst = dst_account.GetCommodity().get_mnemonic()

    return src == dst


def get_exchange_rate(src_account, dst_account, date):
    # get respective commodities
    comm = src_account.GetCommodity()
    curr = dst_account.GetCommodity()

    # find the nearest in time exchange rate
    price = PriceDb.lookup_nearest_in_time64(comm, curr, date)
    value = price.get_value()
    return GncNumeric(value.num, value.denom).to_double()


def set_dst_account(txn, dst_account):
    print_txn(txn)

    splits = txn.GetSplitList()
    assert len(splits) == 2

    # identify source and destination splits
    if is_split_imbalanced(splits[0]):
        src = splits[1]
        dst = splits[0]
    else:
        src = splits[0]
        dst = splits[1]

    src_account = src.GetAccount()

    txn.BeginEdit()
    dst.SetAccount(dst_account)
    if not accounts_eq_commodities(src_account, dst_account):
        exchange_rate = get_exchange_rate(src_account, dst_account, txn.GetDate())
        amount = dst.GetAmount().to_double()
        dst.SetAmount(GncNumeric(int(amount * exchange_rate * 1000), 1000))
    txn.CommitEdit()


def apply_rule(txns, description, dst_account):
    txns = [txn for txn in txns if txn.GetDescription() == description]
    for txn in txns:
        set_dst_account(txn, dst_account)


def rules2darules(config):
    return {key: target for target, descs in config.items() for key in descs}


def process(root, rules, year, month):
    da_rules = rules2darules(rules[RULES_KEY])

    for account_path in rules[ACCOUNTS_TO_SCAN_KEY]:
        print(account_path)
        account = account_lookup_by_path(root, account_path)
        txns = get_transactions(account, year, month)
        txns = [txn for txn in txns if is_imbalanced(txn)]
        for desc, dst_account_path in da_rules.items():
            apply_rule(txns, desc, account_lookup_by_path(root, dst_account_path))


def main():
    global PriceDb

    args = Parser.parse_args()

    with open(args.rules, "r") as f:
        rules = yaml.safe_load(f)

    with Session(str(args.gnucash_file), mode=SessionOpenMode.SESSION_NORMAL_OPEN) as session:
        book = session.book
        root = book.get_root_account()
        PriceDb = book.get_price_db()
        process(root, rules, args.year, args.month)
        session.save()


if __name__ == "__main__":
    main()
