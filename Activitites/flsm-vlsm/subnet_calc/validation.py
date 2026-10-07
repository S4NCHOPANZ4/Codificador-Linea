"""Validación y conversión de las entradas del usuario."""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass

from .models import SubnetError


@dataclass(frozen=True)
class ParsedNetwork:
    network: ipaddress.IPv4Network
    warning: str | None = None


class InputParser:
    MAX_PREFIX = 30  # con /31 o /32 no quedan hosts útiles

    @classmethod
    def parse_network(cls, text: str) -> ParsedNetwork:
        text = text.strip()
        if "/" not in text:
            raise SubnetError("Usa formato CIDR, por ejemplo 192.168.10.0/24")
        try:
            iface = ipaddress.ip_interface(text)
        except ValueError:
            raise SubnetError(f"Red inválida: {text!r}") from None
        if iface.version != 4:
            raise SubnetError("Solo se soporta IPv4")

        net = iface.network
        if net.prefixlen > cls.MAX_PREFIX:
            raise SubnetError(
                f"El prefijo /{net.prefixlen} es demasiado largo: "
                f"debe ser /{cls.MAX_PREFIX} o menor")

        warning = None
        if iface.ip != net.network_address:
            warning = (f"Aviso: {iface.ip} no es dirección de red; "
                       f"se usó {net.network_address}/{net.prefixlen}.")
        return ParsedNetwork(net, warning)

    @staticmethod
    def parse_positive_int(text: str, name: str) -> int:
        try:
            value = int(text)
        except ValueError:
            raise SubnetError(
                f"{name} inválido: {text!r} (debe ser un entero)") from None
        if value < 1:
            raise SubnetError(f"{name} inválido: {value} (debe ser al menos 1)")
        return value

    @classmethod
    def parse_subnet_count(cls, text: str) -> int:
        return cls.parse_positive_int(text.strip(), "N.º de subredes")

    @classmethod
    def parse_hosts(cls, text: str) -> list[int]:
        parts = [p for p in re.split(r"[,\s;]+", text.strip()) if p]
        if not parts:
            raise SubnetError("Indica al menos un requerimiento de hosts")
        return [cls.parse_positive_int(p, "Hosts") for p in parts]
