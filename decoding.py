"""
decoding.py
-----------
Módulo de decodificación de línea.

Contiene las funciones inversas a las de encoding.py: reciben el
arreglo de niveles de la señal (numpy.ndarray) y devuelven la cadena
de bits original.
"""

from encoding import SAMPLES_PER_BIT, INITIAL_LEVEL


def decode_manchester(signal) -> str:
    """Decodifica una señal Manchester.

    Se evalúa el nivel en la primera mitad de cada periodo de bit:
        nivel alto -> '1'
        nivel bajo -> '0'
    """
    n_bits = len(signal) // SAMPLES_PER_BIT
    half = SAMPLES_PER_BIT // 2
    bits = []

    for i in range(n_bits):
        start = i * SAMPLES_PER_BIT
        sample_point = start + half // 2  # punto medio de la primera mitad
        bits.append("1" if signal[sample_point] > 0 else "0")

    return "".join(bits)


def decode_differential_manchester(signal) -> str:
    """Decodifica una señal Manchester Diferencial.

    Para cada bit se compara el nivel al inicio del periodo con el
    nivel final del periodo anterior (o con INITIAL_LEVEL para el
    primer bit):
        - si el nivel cambió respecto al bit anterior -> '0'
        - si el nivel se mantuvo igual                -> '1'
    """
    n_bits = len(signal) // SAMPLES_PER_BIT
    bits = []

    prev_level = INITIAL_LEVEL
    for i in range(n_bits):
        start = i * SAMPLES_PER_BIT
        end = start + SAMPLES_PER_BIT - 1

        start_level = signal[start + 1]  # justo después del flanco
        bits.append("0" if start_level != prev_level else "1")

        prev_level = signal[end]  # nivel final de este bit

    return "".join(bits)


def decode_multilevel(signal) -> str:
    """Decodifica una señal multinivel tipo Bipolar AMI.

    Se evalúa el nivel en la mitad de cada periodo de bit:
        nivel 0        -> '0'
        nivel +1 o -1  -> '1'
    """
    n_bits = len(signal) // SAMPLES_PER_BIT
    half = SAMPLES_PER_BIT // 2
    bits = []

    for i in range(n_bits):
        start = i * SAMPLES_PER_BIT
        sample_point = start + half
        value = signal[sample_point]
        bits.append("0" if abs(value) < 0.5 else "1")

    return "".join(bits)


# Registro de decodificadores disponibles, con las mismas claves que
# ENCODERS en encoding.py para que la GUI pueda emparejarlos.
DECODERS = {
    "Manchester": decode_manchester,
    "Manchester Diferencial": decode_differential_manchester,
    "Multinivel (AMI)": decode_multilevel,
}