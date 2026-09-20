#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime


PROFILES = {
    "revolut": {
        "date_index": 0,
        "input_format": "%b %d, %Y"
    },
    "oinkoin": {
        "date_index": 2,
        "input_format": "%Y-%m-%dT%H:%M:%S.%f%z"
    }
}


# Arguments
parser = argparse.ArgumentParser(
    description="Convert dates in a CSV file for import into GnuCash."
)

parser.add_argument(
    "input_file",
    help="Input CSV file"
)
parser.add_argument(
    "output_file",
    help="Output CSV file"
)
parser.add_argument(
    "profile",
    choices=PROFILES.keys(),
    help="CSV profile"
)


def convert_dates(input_file, output_file, profile):
    date_index = PROFILES[profile]["date_index"]
    input_format = PROFILES[profile]["input_format"]
    output_format = "%Y-%m-%d"

    with open(input_file, "r", encoding="utf-8") as source, \
         open(output_file, "w", encoding="utf-8") as target:

        reader = csv.reader(source)
        writer = csv.writer(target)

        for line_number, row in enumerate(reader, start=1):
            if line_number == 1:
                writer.writerow(row)
                continue

            try:
                date = datetime.strptime(row[date_index], input_format)
            except ValueError as error:
                raise ValueError(
                    f"Invalid date on line {line_number}: "
                    f"{row[date_index]!r}. Expected format: {input_format!r}"
                ) from error

            row[date_index] = date.strftime(output_format)

            writer.writerow(row)


def main():
    args = parser.parse_args()
    convert_dates(args.input_file, args.output_file, args.profile)


if __name__ == "__main__":
    main()
