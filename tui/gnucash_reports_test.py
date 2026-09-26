#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

import argparse
import yaml

from pathlib import Path
from gnucash_model import GnuCashModel
from gnucash_reports import GnuCashIncomeExpenseMonthReport, GnuCashIncomeExpense12MonthReport


# Arguments
parser = argparse.ArgumentParser(description="Apply rules")
parser.add_argument(
    "--gnucash_file",
    type=Path,
    required=True,
    help="Path to the GnuCash file (.gnucash, .xac, etc.)"
)


def main(model: GnuCashModel) -> None:
    # report = GnuCashIncomeExpenseMonthReport(model, 2026, 8)
    report = GnuCashIncomeExpense12MonthReport(model, 2026, 8)
    print(report.income)
    print(report.expense)
    print(report.liabilities)


if __name__ == "__main__":
    args = parser.parse_args()
    main(GnuCashModel(str(args.gnucash_file)))
