"""Interfaz gráfica (tkinter): cada componente es una clase."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Mapping

from .export import CsvExporter
from .models import COLUMNS, Subnet, SubnetError
from .modes import MODES, Mode


class InputPanel(ttk.Frame):
    """Red, método, parámetro y botones."""

    def __init__(self, master, modes: Mapping[str, Mode],
                 on_calculate: Callable[[], None],
                 on_clear: Callable[[], None],
                 on_export: Callable[[], None]):
        super().__init__(master)
        self._modes = modes
        first = next(iter(modes.values()))
        self._net = tk.StringVar(value="192.168.10.0/24")
        self._mode_key = tk.StringVar(value=first.key)
        self._param = tk.StringVar(value=first.example)
        self._param_label = tk.StringVar(value=first.param_label)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Red (CIDR):").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(self, textvariable=self._net).grid(
            row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(self, text="Método:").grid(row=1, column=0, sticky="w", pady=3)
        radios = ttk.Frame(self)
        radios.grid(row=1, column=1, sticky="w", padx=(8, 0))
        for mode in modes.values():
            ttk.Radiobutton(radios, text=mode.title, value=mode.key,
                            variable=self._mode_key,
                            command=self._on_mode_change).pack(side="left", padx=(0, 16))

        ttk.Label(self, textvariable=self._param_label).grid(
            row=2, column=0, sticky="w", pady=3)
        ttk.Entry(self, textvariable=self._param).grid(
            row=2, column=1, sticky="ew", padx=(8, 0))

        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(buttons, text="Calcular", command=on_calculate).pack(side="left")
        ttk.Button(buttons, text="Limpiar", command=on_clear).pack(side="left", padx=6)
        ttk.Button(buttons, text="Exportar CSV", command=on_export).pack(side="left")

    @property
    def mode(self) -> Mode:
        return self._modes[self._mode_key.get()]

    @property
    def network_text(self) -> str:
        return self._net.get()

    @property
    def param_text(self) -> str:
        return self._param.get()

    def _on_mode_change(self) -> None:
        self._param_label.set(self.mode.param_label)
        self._param.set(self.mode.example)


class ResultsTable(ttk.Frame):
    """Tabla de resultados con scrollbars."""

    WIDTHS = (90, 70, 70, 140, 120, 120, 120, 120)

    def __init__(self, master):
        super().__init__(master)
        self._rows: list[tuple[str, ...]] = []
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", height=10)
        for col, width in zip(COLUMNS, self.WIDTHS):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center", stretch=True)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

    @property
    def rows(self) -> list[tuple[str, ...]]:
        return self._rows

    def show(self, subnets: list[Subnet]) -> None:
        self.clear()
        self._rows = [s.to_row() for s in subnets]
        for row in self._rows:
            self.tree.insert("", "end", values=row)

    def clear(self) -> None:
        self._rows = []
        self.tree.delete(*self.tree.get_children())


class StatusBar(ttk.Label):
    def __init__(self, master, wraplength: int = 860):
        self._text = tk.StringVar()
        super().__init__(master, textvariable=self._text, wraplength=wraplength)

    def show(self, text: str, error: bool = False) -> None:
        self._text.set(text)
        self.configure(foreground="red" if error else "")


class App(ttk.Frame):
    """Controlador: conecta el panel, la tabla, el cálculo y la exportación."""

    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=12)
        master.title("Calculadora FLSM / VLSM")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.bind("<Return>", lambda _e: self.calculate())
        self.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.exporter = CsvExporter(COLUMNS)
        self.panel = InputPanel(self, MODES, self.calculate, self.clear, self.export_csv)
        self.table = ResultsTable(self)
        self.status = StatusBar(self)
        self.panel.grid(row=0, column=0, sticky="ew")
        self.table.grid(row=1, column=0, sticky="nsew")
        self.status.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def calculate(self) -> None:
        try:
            result = self.panel.mode.run(self.panel.network_text, self.panel.param_text)
        except SubnetError as exc:
            self.status.show(f"Error: {exc}", error=True)
            messagebox.showerror("Error", str(exc))
            return
        self.table.show(result.subnets)
        msg = f"{len(result.subnets)} subredes calculadas."
        if result.warning:
            msg += " " + result.warning
        self.status.show(msg)

    def clear(self) -> None:
        self.table.clear()
        self.status.show("")

    def export_csv(self) -> None:
        if not self.table.rows:
            messagebox.showinfo("Exportar", "Primero calcula las subredes.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            self.exporter.export(path, self.table.rows)
        except OSError as exc:
            messagebox.showerror("Error al guardar", str(exc))
            return
        self.status.show(f"Exportado a {path}")


def run() -> None:
    root = tk.Tk()
    root.minsize(900, 420)
    App(root)
    root.mainloop()
