"""
message_utils.py
-----------------
Módulo de procesamiento de mensajes.
Se encarga de convertir un mensaje de texto en una cadena de bits
(usando codificación UTF-8, 8 bits por byte) y de reconstruir el
mensaje original a partir de una cadena de bits.
"""


def text_to_bits(text: str) -> str:
    """Convierte un texto en una cadena de bits (string de '0' y '1').

    Cada carácter se codifica en UTF-8 y cada byte resultante se
    representa con 8 bits.
    """
    raw_bytes = text.encode("utf-8")
    return "".join(f"{byte:08b}" for byte in raw_bytes)


def bits_to_text(bits: str) -> str:
    """Convierte una cadena de bits en el texto original (UTF-8).

    Si la cantidad de bits no es múltiplo de 8 (por ejemplo, debido a
    errores de decodificación), se descartan los bits sobrantes al
    final para evitar excepciones.
    """
    usable_len = (len(bits) // 8) * 8
    bits = bits[:usable_len]

    byte_chunks = [bits[i:i + 8] for i in range(0, usable_len, 8)]
    raw_bytes = bytes(int(chunk, 2) for chunk in byte_chunks)

    return raw_bytes.decode("utf-8", errors="replace")