"""Algoritmos de subneteo: una clase por método."""
from __future__ import annotations

import ipaddress
from abc import ABC, abstractmethod

from .models import Subnet, SubnetError


class SubnetCalculator(ABC):
    def __init__(self, network: ipaddress.IPv4Network):
        self.network = network

    @abstractmethod
    def calculate(self, parameter) -> list[Subnet]:
        """Devuelve las subredes calculadas o lanza SubnetError."""


class FLSMCalculator(SubnetCalculator):
    """Máscara fija: todas las subredes del mismo tamaño."""

    MAX_SUBNETS = 65536

    def calculate(self, count: int) -> list[Subnet]:
        extra_bits = (count - 1).bit_length()  # ceil(log2(count))
        new_prefix = self.network.prefixlen + extra_bits
        if new_prefix > 30:
            raise SubnetError(
                f"No hay bits suficientes para {count} subredes desde "
                f"/{self.network.prefixlen} (quedaría un /{new_prefix}, máximo /30)")
        if (1 << extra_bits) > self.MAX_SUBNETS:
            raise SubnetError(
                f"Demasiadas subredes ({1 << extra_bits}); "
                f"el máximo es {self.MAX_SUBNETS}")
        return [Subnet(f"Subred {i + 1}", sub)
                for i, sub in enumerate(self.network.subnets(new_prefix=new_prefix))]


class VLSMCalculator(SubnetCalculator):
    """Máscara variable: cada subred con el tamaño que necesita."""

    def calculate(self, requirements: list[int]) -> list[Subnet]:
        total = self.network.num_addresses
        max_hosts = total - 2
        for req in requirements:
            if req > max_hosts:
                raise SubnetError(
                    f"{req} hosts no caben en una /{self.network.prefixlen} "
                    f"(máximo {max_hosts})")

        cursor = int(self.network.network_address)
        end = cursor + total
        subnets: list[Subnet] = []
        for i, need in enumerate(sorted(requirements, reverse=True)):
            host_bits = (need + 1).bit_length()  # 2^h >= need + 2
            size = 1 << host_bits
            if cursor + size > end:
                raise SubnetError(
                    f"No cabe la subred de {need} hosts: necesita {size} "
                    f"direcciones y solo quedan {end - cursor} en la red")
            network = ipaddress.IPv4Network((cursor, 32 - host_bits))
            subnets.append(Subnet(f"Subred {i + 1}", network, need))
            cursor += size
        return subnets
