"""Modos de cálculo disponibles: une validación + algoritmo + textos de la UI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .calculators import FLSMCalculator, SubnetCalculator, VLSMCalculator
from .models import Subnet
from .validation import InputParser


@dataclass(frozen=True)
class CalculationResult:
    subnets: list[Subnet]
    warning: str | None = None


@dataclass(frozen=True)
class Mode:
    key: str
    title: str
    param_label: str
    example: str
    calculator_cls: type[SubnetCalculator]
    parse_param: Callable[[str], Any]

    def run(self, network_text: str, param_text: str) -> CalculationResult:
        parsed = InputParser.parse_network(network_text)
        param = self.parse_param(param_text)
        subnets = self.calculator_cls(parsed.network).calculate(param)
        return CalculationResult(subnets, parsed.warning)


MODES: dict[str, Mode] = {
    m.key: m for m in (
        Mode("flsm", "FLSM (máscara fija)", "N.º de subredes:", "4",
             FLSMCalculator, InputParser.parse_subnet_count),
        Mode("vlsm", "VLSM (máscara variable)",
             "Hosts por subred (separados por coma o espacio):", "100 50 25 10",
             VLSMCalculator, InputParser.parse_hosts),
    )
}
