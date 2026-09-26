# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 Jan Michalski

from datetime import date

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select


class MonthYear:
    def __init__(self) -> None:
        initial = date.today()
        self._year: int = initial.year
        self._month: int = initial.month

    def __str__(self):
        return f"{self._year}-{self._month:02d}"

    def set(self, year: int, month: int) -> None:
        self._year = year
        self._month = month


class MonthYearPicker(ModalScreen[tuple[int, int] | None]):
    """Modal dialog that returns (year, month), or None if cancelled."""

    DEFAULT_CSS = """
    MonthYearPicker {
        align: center middle;
    }

    #dialog {
        width: 46;
        height: auto;
        padding: 1 2;
    }

    #selectors {
        height: auto;
        margin: 1 0;
    }

    #selectors Select {
        width: 1fr;
        margin-right: 1;
    }

    #buttons {
        height: auto;
        align: right middle;
    }

    #buttons Button {
        margin-left: 1;
    }
    """

    def __init__(
        self,
        initial: MonthYear,
    ):
        super().__init__()

        self._month_year = initial
        self._year: int = initial._year
        self._month: int = initial._month

    def compose(self) -> ComposeResult:
        years = [(str(year), year) for year in range(2000, 2031)]

        months = [
            ("January", 1),
            ("February", 2),
            ("March", 3),
            ("April", 4),
            ("May", 5),
            ("June", 6),
            ("July", 7),
            ("August", 8),
            ("September", 9),
            ("October", 10),
            ("November", 11),
            ("December", 12),
        ]

        with Container(id="dialog"):
            yield Label("Select month and year")

            with Horizontal(id="selectors"):
                yield Select(
                    years,
                    value=self._year,
                    id="year",
                    allow_blank=False,
                )
                yield Select(
                    months,
                    value=self._month,
                    id="month",
                    allow_blank=False,
                )

            with Horizontal(id="buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("OK", variant="primary", id="ok")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return

        if event.button.id == "ok":
            year = self.query_one("#year", Select).value
            month = self.query_one("#month", Select).value

            # allow_blank=False means these should not be None
            if isinstance(year, int) and isinstance(month, int):
                self.dismiss((year, month))
