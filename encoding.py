"""
encoding.py
-----------
Módulo de codificación de línea.

Implementa tres esquemas de codificación de línea sobre una cadena de
bits, generando un arreglo de niveles de señal (numpy) listo para ser
graficado en función del tiempo.

Cada función de codificación recibe una cadena de bits ('0'/'1') y
devuelve una tupla (t, signal):
    t      -> arreglo de tiempo (en unidades de "bit")
    signal -> arreglo de niveles de la señal (numpy.ndarray)
"""

import numpy as np

# Cantidad de muestras usadas para representar cada bit en la gráfica.
# Un valor mayor produce una señal más "suave" visualmente (flancos
# verticales bien definidos) sin afectar la lógica de codificación.
SAMPLES_PER_BIT = 100

# Nivel de referencia asumido en el "instante -1" (antes de transmitir
# el primer bit). Es necesario para la codificación/decodificación de
# Manchester Diferencial, ya que ese esquema es diferencial: cada bit
# se codifica en relación con el nivel final del bit anterior.
INITIAL_LEVEL = 1


def _time_axis(n_bits: int) -> np.ndarray:
    """Genera el eje de tiempo (en unidades de bit) para n_bits."""
    total_samples = n_bits * SAMPLES_PER_BIT
    return np.linspace(0, n_bits, total_samples, endpoint=False)


def encode_manchester(bits: str):
    """Codificación Manchester.

    Convención utilizada:
        bit '1' -> nivel alto en la primera mitad, bajo en la segunda.
        bit '0' -> nivel bajo en la primera mitad, alto en la segunda.

    Siempre hay una transición a la mitad de cada bit, lo que permite
    recuperar el reloj junto con los datos.
    """
    n = len(bits)
    signal = np.zeros(n * SAMPLES_PER_BIT)
    half = SAMPLES_PER_BIT // 2

    for i, bit in enumerate(bits):
        start = i * SAMPLES_PER_BIT
        mid = start + half
        end = start + SAMPLES_PER_BIT
        if bit == "1":
            signal[start:mid] = 1
            signal[mid:end] = -1
        else:
            signal[start:mid] = -1
            signal[mid:end] = 1

    return _time_axis(n), signal


def encode_differential_manchester(bits: str):
    """Codificación Manchester Diferencial.

    Reglas:
        - Siempre hay una transición a la mitad del periodo de bit
          (transición de reloj).
        - Si el bit es '0': hay una transición ADICIONAL al inicio
          del periodo (el nivel cambia respecto al nivel final del
          bit anterior).
        - Si el bit es '1': NO hay transición al inicio del periodo
          (el nivel se mantiene igual al nivel final del bit anterior).
    """
    n = len(bits)
    signal = np.zeros(n * SAMPLES_PER_BIT)
    half = SAMPLES_PER_BIT // 2

    current_level = INITIAL_LEVEL
    for i, bit in enumerate(bits):
        start = i * SAMPLES_PER_BIT
        mid = start + half
        end = start + SAMPLES_PER_BIT

        if bit == "0":
            current_level = -current_level  # transición al inicio del bit

        signal[start:mid] = current_level

        current_level = -current_level  # transición de reloj (mitad del bit)
        signal[mid:end] = current_level

    return _time_axis(n), signal


def encode_multilevel(bits: str):
    """Codificación multinivel tipo Bipolar AMI (Alternate Mark Inversion).

    Reglas:
        - bit '0' -> nivel 0 (sin pulso).
        - bit '1' -> pulso que alterna de polaridad en cada '1'
          sucesivo (+1, -1, +1, -1, ...).

    Es un esquema de tres niveles (-1, 0, +1), típico de sistemas de
    telefonía digital (T1/E1).
    """
    n = len(bits)
    signal = np.zeros(n * SAMPLES_PER_BIT)

    last_pulse = -1  # así el primer '1' que aparezca será +1
    for i, bit in enumerate(bits):
        start = i * SAMPLES_PER_BIT
        end = start + SAMPLES_PER_BIT
        if bit == "1":
            last_pulse = -last_pulse
            signal[start:end] = last_pulse
        else:
            signal[start:end] = 0

    return _time_axis(n), signal


# Registro de codificadores disponibles. Agregar un nuevo método de
# codificación de línea solo requiere escribir la función y añadirla
# aquí (junto con su decodificador correspondiente en decoding.py).
ENCODERS = {
    "Manchester": encode_manchester,
    "Manchester Diferencial": encode_differential_manchester,
    "Multinivel (AMI)": encode_multilevel,
}