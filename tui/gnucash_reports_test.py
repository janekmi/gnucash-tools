#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

import argparse
import yaml

from pathlib import Path
from gnucash_model import GnuCashModel
from gnucash_reports import GnuCashCustomReport, GnuCashMonthReport, GnuCash12MonthReport


# Arguments
parser = argparse.ArgumentParser(description="Apply rules")
parser.add_argument(
    "--gnucash_file",
    type=Path,
    required=True,
    help="Path to the GnuCash file (.gnucash, .xac, etc.)"
)


def print_heler(report: GnuCashCustomReport) -> None:
    print(report.income)
    print(report.expense)
    print(report.liabilities) 


def test00(model: GnuCashModel) -> None:
    report = GnuCashMonthReport(model, 2026, 8)
    print_heler(report)


def test01(model: GnuCashModel) -> None:
    report = GnuCash12MonthReport(model, 2026, 8)
    print_heler(report)


def main(model: GnuCashModel) -> None:
    # test00(model)
    test01(model)


if __name__ == "__main__":
    args = parser.parse_args()
    main(GnuCashModel(str(args.gnucash_file)))
