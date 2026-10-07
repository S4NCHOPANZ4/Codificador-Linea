"""Exportación de resultados."""
from __future__ import annotations

import csv
from typing import Iterable, Sequence


class CsvExporter:
    def __init__(self, columns: Sequence[str]):
        self.columns = columns

    def export(self, path: str, rows: Iterable[Sequence[str]]) -> None:
        """Escribe el CSV. Lanza OSError si no se puede guardar."""
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(rows)
