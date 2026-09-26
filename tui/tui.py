#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

import argparse

from pathlib import Path
from typing import List
from gnucash_model import GnuCashModel
from account_pane import AccountPane
from monthyear_picker import MonthYearPicker, MonthYear
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Markdown, TabbedContent, TabPane, Tree, Static, DataTable

# Arguments
parser = argparse.ArgumentParser(description="Apply rules")
parser.add_argument(
    "--gnucash_file",
    type=Path,
    required=True,
    help="Path to the GnuCash file (.gnucash, .xac, etc.)"
)


def str2id(value: str) -> str:
    return value.replace(" ", "_").lower()


class GnuCashTUI(App):
    """Simple GnuCash TUI."""

    CSS = """
    TabbedContent {
        height: 1fr;
        width: 1fr;
    }

    TabPane {
        height: 1fr;
        width: 1fr;
    }

    DataTable {
        height: 1fr;
    }
    """

    BINDINGS = [
        ("a", "show_tab('accounts')", "Accounts"),
        ("o", "open_tab()", "Open"),
        ("c", "close_tab()", "Close"),
        ("d", "date_picker()", "Date"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, model: GnuCashModel):
        super().__init__()
        self._model = model
        self._month_year = MonthYear()

    def _populate_tree(self, tree, accs: List, path: str) -> None:
        """Populate the accounts tree with GnuCash accounts."""
        tree.expand()
        for acc in accs:
            current_path = f"{path}/{acc['name']}" if path else acc["name"]
            if not acc["children"]:
                tree.add_leaf(acc["name"], data=current_path)
            else:
                subtree = tree.add(acc["name"], data=current_path)
                self._populate_tree(subtree, acc["children"], current_path)

    def compose(self) -> ComposeResult:
        """Compose app with tabbed content."""
        yield Header()
        with TabbedContent(initial="accounts", id="tabs"):
            with TabPane("Accounts", id="accounts"):
                yield Tree("Accounts", id="tree")
        yield Footer()

    def on_mount(self) -> None:
        self._tree = self.query_one("#tree", Tree)
        self._tabs = self.query_one("#tabs", TabbedContent)
        self.title = self._model.gnucash_file
        self.sub_title = str(self._month_year)
        self._populate_tree(self._tree.root, self._model.accounts_tree, "")
        self._tree.focus()

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self._tabs.active = tab
        self._tree.focus()

    def action_open_tab(self) -> None:
        """Open a new tab."""
        node = self._tree.cursor_node
        label: str = str(node.label)
        id = str2id(label)
        if not node or label == "Accounts":
            self.notify("Select an account first.")
            return
        for pane in self._tabs.query(AccountPane):
            if pane.id == id:
                self._tabs.active = id
                return
        pane = AccountPane(
            label,
            monthyear=self._month_year,
            model=self._model,
            path=self._tree.cursor_node.data,
            id=id
        )
        self._tabs.add_pane(pane)
        self._tabs.active = id

    async def action_close_tab(self) -> None:
        """Close the currently active tab."""
        if not self._tabs.active:
            return
        if self._tabs.active == "accounts":
            self.notify("Cannot close the Accounts tab.")
            return
        await self._tabs.remove_pane(self._tabs.active)
        if str(self._tabs.active) == "accounts":
            self._tree.focus()

    def action_date_picker(self) -> None:
        """Open the date picker modal."""
        self.push_screen(MonthYearPicker(self._month_year), self.month_year_selected)

    def month_year_selected(self, result: tuple[int, int] | None) -> None:
        if result is None:
            return

        year, month = result
        self._month_year.set(year, month)
        self.sub_title = str(self._month_year)

        for pane in self._tabs.query(AccountPane):
            pane.update_monthyear()
        # self.notify(f"Selected: {year:04d}-{month:02d}")


if __name__ == "__main__":
    args = parser.parse_args()
    app = GnuCashTUI(GnuCashModel(str(args.gnucash_file)))
    app.run()
