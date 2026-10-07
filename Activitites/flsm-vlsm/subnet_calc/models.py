"""Modelos de datos y excepciones."""
from __future__ import annotations

import ipaddress
from dataclasses import dataclass

COLUMNS = ("Nombre", "Pedidos", "Útiles", "Red", "Máscara",
           "Primer host", "Último host", "Broadcast")


class SubnetError(ValueError):
    """Error de validación o de cálculo de subredes."""


@dataclass(frozen=True)
class Subnet:
    name: str
    network: ipaddress.IPv4Network
    need: int | None = None  # hosts pedidos (None en FLSM)

    @property
    def usable_hosts(self) -> int:
        return self.network.num_addresses - 2

    @property
    def first_host(self) -> ipaddress.IPv4Address:
        return self.network.network_address + 1

    @property
    def last_host(self) -> ipaddress.IPv4Address:
        return self.network.broadcast_address - 1

    def to_row(self) -> tuple[str, ...]:
        n = self.network
        return (
            self.name,
            "-" if self.need is None else str(self.need),
            str(self.usable_hosts),
            str(n),
            str(n.netmask),
            str(self.first_host),
            str(self.last_host),
            str(n.broadcast_address),
        )
