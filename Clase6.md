# Técnicas de Multiplexión y Capa de Enlace de Datos

---

## 1. Técnicas de Multiplexión

La multiplexión permite que varias señales compartan un mismo medio de transmisión. Las dos técnicas clásicas son **TDM** y **FDM**.

*(Aquí va tu imagen comparativa original — `image.png`)*

### 1.1 TDM (Time Division Multiplexing / Multiplexión por División de Tiempo)

- Todas las señales usan la **misma frecuencia**, pero se turnan en el tiempo.
- Cada señal recibe **turnos (slots) de tiempo muy rápidos**, de forma que parece que transmiten simultáneamente.
- Ideal para **datos digitales modernos** (voz digitalizada, datos, video).
- Requiere una **señal de reloj (sincronización)** para que emisor y receptor coincidan en qué turno le corresponde a cada canal.

### 1.2 FDM (Frequency Division Multiplexing / Multiplexión por División de Frecuencia)

- Cada usuario/señal ocupa una **frecuencia (banda) distinta**.
- Todas las señales se transmiten **al mismo tiempo**, pero separadas en el espectro.
- Típica de **señales analógicas o tecnologías más antiguas** (radio, TV analógica).
- Se dejan **bandas de guarda** (espacio libre entre frecuencias) para evitar interferencia entre canales.
- Limitación: el espectro disponible es finito → **a mayor número de usuarios, mayor degradación de la señal** por canal.

### 1.3 OFDM — Acceso Múltiple por División de Frecuencia Ortogonal



- Es la técnica utilizada actualmente (Wi-Fi, LTE/4G, 5G, DSL).
- Divide el canal en muchas subportadoras **ortogonales entre sí**, lo que permite aprovechar mejor el espectro y reducir interferencia comparado con el FDM clásico.

| Técnica | Divide por... | Transmisión | Uso típico |
|---|---|---|---|
| TDM | Tiempo | Turnos secuenciales | Digital moderno |
| FDM | Frecuencia | Simultánea | Analógico / legado |
| OFDM | Frecuencias ortogonales | Simultánea, eficiente | Redes actuales (Wi-Fi, LTE, 5G) |

---

## 2. Topología Física tipo Bus

*(Aquí va tu imagen `image-1.png`)*

- En una topología de **bus**, todos los dispositivos comparten **un único medio físico de transmisión**.
- Los **dominios de frecuencia** (o de colisión) se analizan en las **capas 2 y 3** del modelo OSI.

### 2.1 Dominios de Colisión

*(Aquí va tu imagen `image-2.png`)*

- Un **dominio de colisión** es la porción de red donde, si dos dispositivos transmiten al mismo tiempo, sus señales pueden **chocar (colisionar)**.
- **Lógica del bus:** al existir un solo medio compartido, si dos o más equipos envían paquetes simultáneamente, se produce una colisión y ambas transmisiones se pierden/corrompen.

**Nota sobre dispositivos:**
- **Hub (concentrador):** dispositivo de **capa 1**, no segmenta dominios de colisión — todos los puertos comparten el mismo dominio (a veces referido como **DSS**, dispositivo de un solo segmento).
- **Switch:** dispositivo de **capa 2**, sí segmenta dominios de colisión — cada puerto es su propio dominio de colisión (referido aquí como **DCS**).



### 2.2 Tarea (pendiente de investigar/realizar)

1. En **Cisco Packet Tracer** y usando **GNS3**: verificar si es posible visualizar una colisión en GNS3 por medio de **Wireshark**.
2. Investigar cómo el uso de la **capa 2** resuelve el reenvío masivo de información para alcanzar el destino (ej. tablas MAC, switching).
3. Investigar el estándar **G.6** / **"OMA"** (verificar nombre exacto — podría referirse a un estándar de la UIT-T; conviene confirmar la sigla completa antes de investigar).
4. Diferencias entre la **subcapa LLC** (Logical Link Control) y la **subcapa MAC** (Media Access Control) dentro de la capa de enlace de datos.

---

## 3. Interconexión de Terminales: DTE – DCE / DTE – DTE

- **DTE** (Data Terminal Equipment / Equipo Terminal de Datos): ej. una computadora, router configurado como terminal.
- **DCE** (Data Circuit-terminating Equipment / Equipo de Comunicación de Datos): ej. módem, CSU/DSU — es quien genera la señal de reloj en un enlace serial.

### 3.1 Conexión DTE – DTE (medio incompatible / requiere cable cruzado)

Cuando dos DTE se conectan directamente, el **TX de uno debe ir al RX del otro**:

```
DTE                                    DTE
TX ---------------------------------> RX
RX <--------------------------------- TX
```

### 3.2 Conexión DTE – DCE – DCE – DTE (cable directo)

Aquí el DCE actúa de intermediario, por lo que cada tramo respeta TX→TX y RX→RX en el cable físico:

```
DTE            DCE            DCE            DTE
TX -----------> RX            TX -----------> RX
RX <----------- TX            RX <----------- TX
```

*(Aquí va tu imagen `image-3.png`)*

> **Regla práctica:** DTE–DTE normalmente necesita **cable cruzado**; DTE–DCE normalmente usa **cable directo**, porque el DCE ya invierte la señal internamente.

---

## 4. Capa de Enlace de Datos (Capa 2)

### 4.1 Identificadores por Capa — Modelo OSI

| Capa OSI | Identificador |
|---|---|
| Capa 2 – Enlace de Datos | **Dirección MAC** |
| Capa 3 – Red | **Dirección IP** |
| Capa 4 – Transporte | **Número de Puerto** |
| Capa 7 – Aplicación | **Identificador específico de aplicación** (ej. socket, URL) |

*(Aquí va tu imagen `image-4.png`)*

> Ajusté la última fila: "específico de capa 4" no es estándar — el identificador de capa 4 es el **puerto**; lo "específico de aplicación" pertenece más bien a capa 7. Revísalo con el material de tu profesor para confirmar si así lo definió en clase.

### 4.2 Tecnología de Capa 2

- Una **tecnología de capa 2** es aquella que define cómo se **da forma/estructura a una red a nivel de enlace de datos**: direccionamiento MAC, control de acceso al medio, formación de tramas, switching. Ejemplo principal: **Ethernet (IEEE 802.3)**.

---

## 5. Formato de Trama IEEE 802.3 (Ethernet)

*(Sección que quedó incompleta en tus apuntes — aquí tienes la estructura estándar para completarla)*

| Campo | Tamaño | Descripción |
|---|---|---|
| Preámbulo | 7 bytes | Sincronización entre emisor y receptor |
| SFD (Start Frame Delimiter) | 1 byte | Indica el inicio de la trama |
| Dirección MAC de destino | 6 bytes | Identifica al receptor |
| Dirección MAC de origen | 6 bytes | Identifica al emisor |
| Longitud/Tipo (Length/Type) | 2 bytes | Longitud de los datos o tipo de protocolo superior |
| Datos y relleno (Data/Pad) | 46–1500 bytes | Carga útil (payload); se rellena si es menor al mínimo |
| FCS (Frame Check Sequence) | 4 bytes | CRC para detección de errores |

**Tamaño mínimo de trama:** 64 bytes — **Tamaño máximo (sin jumbo frames):** 1518 bytes.

---

