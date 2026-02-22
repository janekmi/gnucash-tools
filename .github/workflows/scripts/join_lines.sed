# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

# Read the entire file into the pattern space
:a
N
$!ba

# Replace all newlines with %0A for GitHub Actions
s/\n/%0A/g
