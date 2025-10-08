# Ley_de_Coulomb_python

# Electric Force Visualizer (1D/2D/3D) — Tkinter + Matplotlib

**Author:** Carlos Delgado
**Python:** 3.9+
**GUI:** Tkinter + Matplotlib (embedded)



## English Documentation

### 1) Overview

This project computes and visualizes the net electric force acting on a reference charge produced by a set of point charges in 1D, 2D, or 3D space. It provides a clean, futuristic GUI in blue and white built with Tkinter and embeds Matplotlib plots for interactive visualization.

Key idea: you enter several charges; the first charge becomes the reference (point at which the resulting force is computed). The program applies Coulomb’s law and vector superposition to compute the force vector and displays it as an arrow anchored at the reference charge.

### 2) Features

* Dimensionality: switch between 1D / 2D / 3D.
* Robust input: numeric value plus SI prefix from a dropdown (—, p, n, u, m, k, M, G).
* Coordinates UI: inputs (î, ĵ, k̂) adapt to the selected dimension.
* Immediate visualization: charge positions plus a scaled force arrow (anchored at the reference).
* Readable results: vector components and magnitude in scientific notation.
* Safe checks: avoids division by zero when two charges share identical coordinates.
* Quality of life:

  * Value and coordinate fields auto-clear after adding a charge.
  * High-contrast button text for legibility.
  * Single clean main window (no hidden/empty Tk root windows).

### 3) Physics Background (no formulas)

* Implements Coulomb’s law and vector superposition.
* The code sums each contributing charge’s effect at the reference location, then scales by the Coulomb constant and the reference charge to get the net force vector.
* The force arrow is drawn at the reference position with automatic visual scaling relative to the plotted scene.

### 4) UX / UI Design

* Palette: deep blue sidebar, light blue controls, white plotting canvas, blue accents.
* Layout:

  * Left: controls (dimension, value + SI prefix, coordinates), charge table, results, action buttons.
  * Right: Matplotlib figure (2D axes for 1D/2D; 3D projection for 3D).
* Force arrow scaling: arrow length uses a fraction of the data extents so it remains visible and comparable across scenarios (tuned separately for 2D and 3D).

### 5) Installation

```bash
# Recommended: use a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install matplotlib
# Tkinter usually ships with Python; on some Linux distros:
# Debian/Ubuntu example:
# sudo apt-get install python3-tk
```

### 6) Running the App

```bash
python cargas_gui.py
```

### 7) How to Use

1. Select dimension (1, 2, or 3).
2. Enter the charge value (numeric) and choose an SI prefix (— = no prefix).

   * Example: value `5`, prefix `m` → 5e-3 C
3. Enter coordinates according to the chosen dimension.
4. Click “Agregar carga”:

   * The first charge becomes the reference.
   * Value and coordinate inputs are cleared automatically.
5. Add more charges.
6. Click “Calcular y graficar” to compute and display:

   * |F| (magnitude) and F (components) in scientific notation.
   * A plot with all charge positions and the force arrow at the reference.

### 8) Data Model & SI Prefixes

* Charge object:

  ```python
  {
    "valor_C": <float in Coulombs>,
    "coordenadas": (<x>[, <y>[, <z>]])
  }
  ```
* SI prefixes:

  | Symbol | Factor | Example value=5 | Result (C) |
  | ------ | ------ | --------------- | ---------- |
  | —      | 1      | 5 —             | 5          |
  | p      | 1e-12  | 5 p             | 5e-12      |
  | n      | 1e-9   | 5 n             | 5e-9       |
  | u      | 1e-6   | 5 u             | 5e-6       |
  | m      | 1e-3   | 5 m             | 5e-3       |
  | k      | 1e3    | 5 k             | 5e3        |
  | M      | 1e6    | 5 M             | 5e6        |
  | G      | 1e9    | 5 G             | 5e9        |

### 9) Algorithms & Scaling Notes

* Zero-distance guard: if two charges share identical coordinates, that contribution is skipped and a warning is emitted.
* Arrow scaling: maps the physical magnitude to a visually meaningful length using a fraction of the plot extents.
* Deterministic ordering: charges are processed as Carga1, Carga2, …

### 10) Code Structure (suggested)

```
cargas_gui.py
README.md
LICENSE
```

* `App` class encapsulates GUI and plotting.
* Pure functions:

  * `calcular_sumatoria(cargas, dimension)`
  * `magnitud_vector(vec)`

### 11) Error Handling & Validation

* Numeric validation for values and coordinates.
* SI prefix constrained by dropdown (prevents malformed inputs).
* Single Tk root window; style initialization happens after creating the main app.

### 12) Known Limitations

* The first charge is always the reference (not selectable yet).
* No edit/delete rows in the table (can be added).
* No CSV/JSON import/export (can be added).

### 13) Roadmap (Nice-to-Have)

* Row context menu: Edit / Delete / Set as Reference.
* Import/Export charge sets (CSV/JSON).
* Unit tests for physics routines.
* Grid/axes toggles, zoom/pan helpers.
* Optional dark mode.

### 14) Changelog (Highlights)

* GUI overhaul (blue/white, simple and futuristic).
* Separated numeric value and SI prefix (dropdown).
* Coordinates auto-clear after adding a charge.
* Fixed duplicate coordinate rows when switching dimensions.
* Button text set to black for better contrast.
* Prevented hidden “tkinter” window by initializing styles after root creation.

### 15) Troubleshooting

* No window or Tk errors: ensure `tkinter` is installed (Linux may require `python3-tk`).
* Plot not updating: check console warnings about overlapping coordinates.
* Arrow size looks odd: depends on spatial extents; try increasing separation between charges.

### Acknowledgments

* Original console algorithm: Carlos Delgado (2025-01-22).
* GUI refactor, input hardening, and documentation: derived from subsequent requirements.
* ChatGPT assisted as a software implementer under direction; design, logic, execution, and testing were led by the author.



## Documentación en Español

### 1) Descripción General

Este proyecto calcula y visualiza la fuerza eléctrica neta que actúa sobre una carga de referencia, producida por un conjunto de cargas puntuales en 1D, 2D o 3D. Incluye una interfaz gráfica limpia y futurista en azul y blanco con Tkinter y gráficos de Matplotlib embebidos.

Idea clave: ingresas varias cargas; la primera que agregas es la referencia (punto donde se calcula la fuerza resultante). El programa aplica la ley de Coulomb y la superposición vectorial, y muestra la flecha de fuerza anclada en la carga de referencia.

### 2) Funcionalidades

* Dimensión seleccionable: 1D / 2D / 3D.
* Entrada robusta: valor numérico + prefijo SI desde lista (—, p, n, u, m, k, M, G).
* Coordenadas según dimensión: campos î, ĵ, k̂ que se adaptan automáticamente.
* Visualización inmediata: posiciones de las cargas + flecha de fuerza escalada.
* Resultados claros: componentes del vector y magnitud en notación científica.
* Controles de seguridad: evita división por cero en posiciones coincidentes.
* Calidad de uso:

  * Limpieza automática de valor y coordenadas al agregar una carga.
  * Botones con alto contraste.
  * Ventana principal única (sin ventanas Tk vacías).

### 3) Fundamento Físico (sin fórmulas)

* Implementa la ley de Coulomb y la superposición vectorial.
* Se suma el efecto de cada carga en la ubicación de la referencia y luego se escala por la constante de Coulomb y la carga de referencia.
* La flecha de fuerza se dibuja en la posición de referencia con escalado visual automático.

### 4) Diseño UX / UI

* Paleta: azul profundo en barra lateral, azul claro en controles, lienzo blanco, acentos azules.
* Distribución:

  * Izquierda: controles (dimensión, valor + prefijo, coordenadas), tabla de cargas, resultados, botones.
  * Derecha: figura de Matplotlib (2D o 3D según corresponda).
* Escalado de flecha: longitud proporcional a la extensión del sistema para legibilidad consistente (ajustada para 2D y 3D).

### 5) Instalación

```bash
# Recomendado: entorno virtual
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install matplotlib
# En algunas distribuciones Linux:
# sudo apt-get install python3-tk
```

### 6) Ejecución

```bash
python cargas_gui.py
```

### 7) Uso

1. Selecciona la dimensión (1, 2 o 3).
2. Ingresa el valor numérico y elige el prefijo SI (— = sin prefijo).

   * Ejemplo: valor `5`, prefijo `m` → 5e-3 C
3. Escribe las coordenadas de acuerdo con la dimensión.
4. Pulsa “Agregar carga”:

   * La primera carga será la referencia.
   * Se limpian los campos de valor y coordenadas.
5. Agrega el resto de cargas.
6. Pulsa “Calcular y graficar” para obtener:

   * |F| (magnitud) y F (componentes).
   * Gráfico con posiciones y flecha de fuerza en la referencia.

### 8) Modelo de Datos y Prefijos SI

* Estructura de carga:

  ```python
  {
    "valor_C": <float en Coulombs>,
    "coordenadas": (<x>[, <y>[, <z>]])
  }
  ```
* Prefijos SI:

  | Símbolo | Factor | Ejemplo valor=5 | Resultado (C) |
  | ------- | ------ | --------------- | ------------- |
  | —       | 1      | 5 —             | 5             |
  | p       | 1e-12  | 5 p             | 5e-12         |
  | n       | 1e-9   | 5 n             | 5e-9          |
  | u       | 1e-6   | 5 u             | 5e-6          |
  | m       | 1e-3   | 5 m             | 5e-3          |
  | k       | 1e3    | 5 k             | 5e3           |
  | M       | 1e6    | 5 M             | 5e6           |
  | G       | 1e9    | 5 G             | 5e9           |

### 9) Algoritmos y Escalado

* Control de distancia cero: si dos cargas comparten coordenadas, se omite esa contribución y se advierte en consola.
* Escalado de flecha: mapea la magnitud física a una longitud visual usando una fracción de la extensión gráfica.
* Orden determinista: Carga1, Carga2, …

### 10) Estructura del Código (sugerida)

```
cargas_gui.py
README.md
LICENSE
```

* `App`: clase principal de GUI y gráficos.
* Funciones puras:

  * `calcular_sumatoria(cargas, dimension)`
  * `magnitud_vector(vec)`

### 11) Manejo de Errores y Validaciones

* Validación numérica en valores y coordenadas.
* Prefijo SI restringido al desplegable.
* Ventana única; estilos inicializados tras crear la app.

### 12) Limitaciones Conocidas

* La primera carga es la referencia (no seleccionable por ahora).
* No hay edición/eliminación de filas en la tabla.
* No hay importación/exportación (CSV/JSON).

### 13) Hoja de Ruta (Opcional)

* Menú contextual: Editar / Eliminar / Definir como referencia.
* Importar/Exportar conjuntos de cargas (CSV/JSON).
* Pruebas unitarias.
* Controles de rejilla/ejes, zoom/pan.
* Modo oscuro opcional.

### 14) Cambios Realizados (Resumen)

* Nueva GUI (azul/blanco, simple y futurista).
* Separación de valor numérico y prefijo SI (lista desplegable).
* Limpieza automática de coordenadas tras agregar carga.
* Corrección de duplicación de campos al cambiar dimensión.
* Texto de botones en negro para mejor contraste.
* Evitar ventana Tk vacía (estilos después de crear la raíz).

### 15) Solución de Problemas

* La ventana no aparece o hay errores de Tk: instalar `tkinter` (Linux: `python3-tk`).
* El gráfico no cambia: revisar advertencias por posiciones coincidentes.
* Flecha muy grande/pequeña: depende de la escala del sistema; separa más las cargas.

### Reconocimientos

* Algoritmo de consola original: Carlos Delgado (2025-01-22).
* Refactor de GUI, robustecimiento de entrada y documentación: derivados de requisitos posteriores.
* ChatGPT apoyó como implementador bajo dirección del autor; el diseño, la lógica, la ejecución y las pruebas pertenecen al autor.

