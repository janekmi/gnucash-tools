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


def main(model: GnuCashModel) -> None:
    print(yaml.safe_dump(model.accounts_tree, sort_keys=False, default_flow_style=False))
    account = model.get_account_by_path("Assets/Starling")
    print(account.name)
    for _, txn in enumerate(account.transactions[:1]):
        print(f"Date:        {txn.date}")
        print(f"Description: {txn.description}")
        print(f"Deposit:     {txn.deposit}")
        print(f"Withdrawal:  {txn.withdrawal}")


if __name__ == "__main__":
    args = parser.parse_args()
    main(GnuCashModel(str(args.gnucash_file)))
