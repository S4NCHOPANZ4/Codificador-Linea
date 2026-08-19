"""

python -m venv .venv
.venv\Scripts\activate.bat



main.py
-------
Simulador de Codificación y Decodificación de Línea.

Laboratorio virtual de comunicaciones digitales que permite:
    1. Ingresar un mensaje de texto.
    2. Convertirlo a bits.
    3. Seleccionar un método de codificación de línea
       (Manchester, Manchester Diferencial o Multinivel/AMI).
    4. Visualizar gráficamente la señal generada.
    5. Decodificar la señal y recuperar el mensaje.
    6. Verificar que la transmisión fue exitosa.

Módulos utilizados:
    - message_utils.py -> conversión texto <-> bits
    - encoding.py       -> codificadores de línea
    - decoding.py       -> decodificadores de línea
    - main.py (este)    -> interfaz gráfica (Tkinter + Matplotlib)

Ejecutar con:
    python3 main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Activitites.decoder.message_utils import text_to_bits, bits_to_text
from Activitites.decoder.encoding import ENCODERS
from Activitites.decoder.decoding import DECODERS


class LineCoderApp(tk.Tk):
    """Ventana principal del simulador."""

    def __init__(self):
        super().__init__()
        self.title("Codificador de Línea — Laboratorio de Comunicaciones Digitales")
        self.geometry("760x680")
        self.minsize(620, 560)
        self.configure(bg="#f5f5f7")

        self._build_style()
        self._build_widgets()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#f5f5f7"
        style.configure(".", background=bg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Result.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=10,
        )
        style.configure("TCombobox", font=("Segoe UI", 11))
        style.configure("TEntry", font=("Segoe UI", 12))

    def _build_widgets(self):
        container = ttk.Frame(self, padding=24)
        container.pack(fill="both", expand=True)

        # --- Título -----------------------------------------------------
        ttk.Label(
            container, text="CODIFICADOR DE LÍNEA", style="Title.TLabel", anchor="center"
        ).pack(fill="x", pady=(0, 18))

        # --- Mensaje ------------------------------------------------------
        ttk.Label(container, text="Mensaje:", style="Section.TLabel").pack(anchor="w")
        self.message_entry = ttk.Entry(container, font=("Segoe UI", 12))
        self.message_entry.pack(fill="x", pady=(4, 14), ipady=4)
        self.message_entry.insert(0, "Test")
        self.message_entry.bind("<Return>", lambda _e: self.run_process())

        # --- Selector de codificación -------------------------------------
        ttk.Label(container, text="Codificación:", style="Section.TLabel").pack(anchor="w")
        self.encoding_var = tk.StringVar(value=list(ENCODERS.keys())[0])
        self.encoding_combo = ttk.Combobox(
            container,
            textvariable=self.encoding_var,
            values=list(ENCODERS.keys()),
            state="readonly",
            font=("Segoe UI", 11),
        )
        self.encoding_combo.pack(fill="x", pady=(4, 18), ipady=3)

        # --- Botón --------------------------------------------------------
        button_row = ttk.Frame(container)
        button_row.pack(pady=(0, 18))
        self.encode_button = ttk.Button(
            button_row, text="CODIFICAR", style="Accent.TButton", command=self.run_process
        )
        self.encode_button.pack()

        # --- Gráfica de la señal -------------------------------------------
        ttk.Label(container, text="Señal:", style="Section.TLabel").pack(anchor="w")
        plot_frame = ttk.Frame(container, relief="solid", borderwidth=1)
        plot_frame.pack(fill="both", expand=True, pady=(4, 16))

        self.figure = Figure(figsize=(6, 2.6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.08, right=0.98, top=0.85, bottom=0.22)

        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._draw_empty_plot()

        # --- Mensaje recuperado ---------------------------------------------
        result_row = ttk.Frame(container)
        result_row.pack(fill="x", pady=(0, 8))
        ttk.Label(result_row, text="Mensaje recibido:", style="Section.TLabel").pack(side="left")
        self.received_var = tk.StringVar(value="—")
        ttk.Label(result_row, textvariable=self.received_var, style="Result.TLabel").pack(
            side="left", padx=8
        )

        # --- Indicador de verificación ---------------------------------------
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(
            container, textvariable=self.status_var, font=("Segoe UI", 13, "bold"), anchor="center"
        )
        self.status_label.pack(fill="x", pady=(6, 0))

    # ------------------------------------------------------------------
    # Utilidades de dibujo
    # ------------------------------------------------------------------
    def _draw_empty_plot(self):
        self.ax.clear()
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_xlabel("Tiempo (bits)", fontsize=9)
        self.ax.set_ylabel("Nivel", fontsize=9)
        self.ax.grid(True, alpha=0.3)
        self.ax.tick_params(labelsize=8)
        self.canvas.draw()

    def _plot_signal(self, t, signal, encoding_name, bits):
        self.ax.clear()
        self.ax.step(t, signal, where="post", linewidth=1.8, color="#2f6feb")
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_xlabel("Tiempo (bits)", fontsize=9)
        self.ax.set_ylabel("Nivel", fontsize=9)
        self.ax.set_title(f"Señal codificada — {encoding_name}", fontsize=10)
        self.ax.grid(True, alpha=0.3)
        self.ax.tick_params(labelsize=8)

        # Si hay pocos bits, mostrar la secuencia de bits sobre el eje X
        if len(bits) <= 32:
            self.ax.set_xticks(range(len(bits) + 1))

        self.canvas.draw()

    # ------------------------------------------------------------------
    # Lógica principal: Mensaje -> Bits -> Codificación -> Gráfica ->
    #                   Decodificación -> Mensaje recuperado -> Verificación
    # ------------------------------------------------------------------
    def run_process(self):
        text = self.message_entry.get()
        if not text:
            messagebox.showwarning("Aviso", "Por favor ingresa un mensaje de texto.")
            return

        encoding_name = self.encoding_var.get()
        encoder = ENCODERS[encoding_name]
        decoder = DECODERS[encoding_name]

        # 1-2. Mensaje de texto -> bits
        bits = text_to_bits(text)

        # 3-4. Selección de codificador -> codificación de línea
        t, signal = encoder(bits)

        # 5. Representación gráfica de la señal
        self._plot_signal(t, signal, encoding_name, bits)

        # 6. Decodificación
        decoded_bits = decoder(signal)

        # 7. Recuperación del mensaje
        received_text = bits_to_text(decoded_bits)
        self.received_var.set(received_text)

        # 8. Verificación
        if received_text == text:
            self.status_var.set("Exito")
            self.status_label.configure(foreground="#1a7f37")
        else:
            self.status_var.set("✗ Error en la transmisión")
            self.status_label.configure(foreground="#c62828")


if __name__ == "__main__":
    app = LineCoderApp()
    app.mainloop()