import re
import math
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ------------------------------- Estilo/Paleta -------------------------------
COLOR_BG_DARK = "#0B1E3F"   # sidebar (azul profundo)
COLOR_BG_LIGHT = "#E6F3FF"  # panel claro
COLOR_ACCENT   = "#1E88E5"  # azul medio (botones/acentos)
COLOR_TEXT     = "#FFFFFF"
COLOR_TEXT_DK  = "#0B1E3F"
COLOR_WHITE    = "#FFFFFF"
COLOR_BLACK    = "#000000"

# -------------------------- Constantes físicas/útiles -------------------------
K_COULOMB = 8.9875517923e9  # N·m²/C²

# Prefijos SI (nota: '—' = sin prefijo)
PREFIXES = {
    '—': 1.0,   # sin prefijo
    'p': 1e-12, # pico
    'n': 1e-9,  # nano
    'u': 1e-6,  # micro
    'm': 1e-3,  # mili
    'k': 1e3,   # kilo
    'M': 1e6,   # Mega
    'G': 1e9,   # Giga
}

def calcular_sumatoria(cargas: dict, dimension: int):
    """
    Calcula la fuerza resultante sobre la PRIMERA carga (referencia):
    1) Suma tipo campo: Σ q_i * (r/|r|^3) en la posición de la referencia.
    2) Multiplica por K * q_ref para obtener fuerza (Coulomb).
    Retorna [Fx] o [Fx, Fy] o [Fx, Fy, Fz] según 'dimension'.
    """
    if len(cargas) == 0:
        return [0.0] * dimension

    items = sorted(cargas.items(), key=lambda x: x[0])
    ref_id, ref_data = items[0]
    q_ref = ref_data["valor_C"]
    r_ref = ref_data["coordenadas"]

    acc = [0.0] * dimension  # acumulador del "campo" sin K

    for carga_id, data in items[1:]:
        q = data["valor_C"]
        r = data["coordenadas"]
        r_vec = [r_ref[i] - r[i] for i in range(dimension)]
        mag = math.sqrt(sum(c*c for c in r_vec))

        if mag == 0:
            print(f"Advertencia: '{ref_id}' y '{carga_id}' comparten la misma posición.")
            continue

        mag3 = mag ** 3
        for i in range(dimension):
            acc[i] += q * (r_vec[i] / mag3)

    F = [K_COULOMB * q_ref * comp for comp in acc]
    return F

def magnitud_vector(vec) -> float:
    """Magnitud euclídea de un vector (1D/2D/3D)."""
    return math.sqrt(sum(v*v for v in vec))

class App(tk.Tk):
    """
    Ventana principal:
    • Izquierda (sidebar): controles, lista de cargas y resultados.
    • Derecha: gráfica Matplotlib (1D/2D/3D).
    """
    def __init__(self):
        super().__init__()
        self.title("Fuerza eléctrica resultante — Hecho por Carlos Delgado")
        self.geometry("1100x640")
        self.minsize(980, 560)
        self.configure(bg=COLOR_BG_DARK)

        # Estado
        self.dimension = tk.IntVar(value=2)
        self.cargas = {}    # {'Carga1': {'valor_C': float, 'coordenadas': tuple}}
        self._next_idx = 1

        # Nuevos campos: número + prefijo
        self.prefix_var = tk.StringVar(value='—')  # '—' = sin prefijo

        self._build_layout()
        self._build_plot()

    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=COLOR_BG_DARK, width=360)
        self.sidebar.pack(side="left", fill="y")

        title = tk.Label(
            self.sidebar, text="Cargas eléctricas - Hecho por Carlos Delgado",
            bg=COLOR_BG_DARK, fg=COLOR_WHITE,
            font=("SF Pro Display", 18, "bold")
        )
        title.pack(padx=18, pady=(18, 4), anchor="w")

        subtitle = tk.Label(
            self.sidebar,
            text="Primera carga = referencia (punto donde se calcula F⃗)",
            bg=COLOR_BG_DARK, fg="#94B9FF",
            font=("SF Pro Display", 10)
        )
        subtitle.pack(padx=18, pady=(0, 12), anchor="w")

        # Panel de controles (claro)
        ctrl = tk.Frame(self.sidebar, bg=COLOR_BG_LIGHT, bd=0, highlightthickness=0)
        ctrl.pack(padx=18, pady=10, fill="x")

        # Dimensión
        row = tk.Frame(ctrl, bg=COLOR_BG_LIGHT)
        row.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(row, text="Dimensión", bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_DK).pack(side="left")
        cb = ttk.Combobox(row, state="readonly", width=6, values=[1, 2, 3])
        cb.set(self.dimension.get())
        cb.pack(side="right")
        cb.bind("<<ComboboxSelected>>", lambda e: self._on_dim_change(int(cb.get())))

        # >>> NUEVO: valor numérico + prefijo SI (en lugar de texto con prefijo mezclado)
        # Valor numérico
        row_val = tk.Frame(ctrl, bg=COLOR_BG_LIGHT)
        row_val.pack(fill="x", padx=12, pady=6)
        tk.Label(row_val, text="Valor", bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_DK).pack(side="left")
        self.entry_valor = ttk.Entry(row_val)
        self.entry_valor.insert(0, "5")  # placeholder
        self.entry_valor.pack(side="right", fill="x", expand=True)

        # Prefijo SI
        row_pref = tk.Frame(ctrl, bg=COLOR_BG_LIGHT)
        row_pref.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(row_pref, text="Prefijo SI", bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_DK).pack(side="left")
        self.combo_prefijo = ttk.Combobox(
            row_pref, state="readonly", width=6,
            values=list(PREFIXES.keys()), textvariable=self.prefix_var
        )
        self.combo_prefijo.pack(side="right")

        # Coordenadas (dinámico según dimensión)
        self.coords_frame = tk.Frame(ctrl, bg=COLOR_BG_LIGHT)
        self.coords_frame.pack(fill="x", padx=12, pady=(6, 12))
        self.coord_entries = []
        self._render_coord_inputs()  # primera vez

        # Botones acción — TEXTO NEGRO (legibilidad)
        btns = tk.Frame(ctrl, bg=COLOR_BG_LIGHT)
        btns.pack(fill="x", padx=12, pady=(0, 12))

        self.btn_add = tk.Button(
            btns, text="Agregar carga", command=self._add_charge,
            bg=COLOR_ACCENT, fg=COLOR_BLACK, bd=0, relief="flat",
            activebackground="#1565C0", activeforeground=COLOR_BLACK
        )
        self.btn_add.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_clear = tk.Button(
            btns, text="Limpiar", command=self._clear_all,
            bg="#5C6BC0", fg=COLOR_BLACK, bd=0, relief="flat",
            activebackground="#3F51B5", activeforeground=COLOR_BLACK
        )
        self.btn_clear.pack(side="left", expand=True, fill="x", padx=(6, 0))

        # Tabla de cargas
        table_box = tk.Frame(self.sidebar, bg=COLOR_BG_DARK)
        table_box.pack(fill="both", expand=True, padx=18, pady=(6, 12))

        cols = ("id", "qC", "x", "y", "z")
        self.table = ttk.Treeview(table_box, columns=cols, show="headings", height=7)
        for c, w in zip(cols, (70, 120, 70, 70, 70)):
            self.table.heading(c, text=c.upper())
            self.table.column(c, width=w, anchor="center")
        self.table.pack(fill="both", expand=True)

        # Resultados
        res = tk.Frame(self.sidebar, bg=COLOR_BG_DARK)
        res.pack(fill="x", padx=18, pady=(0, 12))

        self.lbl_mag = tk.Label(res, text="‣ |F| = —", fg=COLOR_WHITE, bg=COLOR_BG_DARK, font=("SF Pro Display", 12, "bold"))
        self.lbl_vec = tk.Label(res, text="‣ F⃗  = (—)", fg="#94B9FF", bg=COLOR_BG_DARK, font=("SF Pro Display", 11))
        self.lbl_mag.pack(anchor="w")
        self.lbl_vec.pack(anchor="w", pady=(2, 8))

        self.btn_calc = tk.Button(
            res, text="Calcular y graficar", command=self._compute_and_plot,
            bg=COLOR_ACCENT, fg=COLOR_BLACK, bd=0, relief="flat",
            activebackground="#1565C0", activeforeground=COLOR_BLACK
        )
        self.btn_calc.pack(fill="x")

    def _build_plot(self):
        self.plot_panel = tk.Frame(self, bg=COLOR_WHITE)
        self.plot_panel.pack(side="right", fill="both", expand=True)

        self.fig = Figure(figsize=(6, 5), facecolor=COLOR_WHITE)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._draw_placeholder()

    # --------------------------- Callbacks/acciones ---------------------------
    def _on_dim_change(self, dim: int):
        self.dimension.set(dim)
        self._render_coord_inputs()

    def _render_coord_inputs(self):
        """
        (FIX) Antes solo destruía los Entry y dejaba labels/contenedores,
        lo que acumulaba filas al cambiar de dimensión. Ahora:
        • Limpio TODO el contenido de 'coords_frame'.
        • Creo desde cero las filas para î/ĵ/k̂ según dimensión.
        """
        for w in self.coords_frame.winfo_children():
            w.destroy()
        self.coord_entries.clear()

        dim = self.dimension.get()
        labels = ["î (x)"] if dim == 1 else (["î (x)", "ĵ (y)"] if dim == 2 else ["î (x)", "ĵ (y)", "k̂ (z)"])

        for lab in labels:
            row = tk.Frame(self.coords_frame, bg=COLOR_BG_LIGHT)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=lab, bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_DK).pack(side="left")
            e = ttk.Entry(row)
            e.insert(0, "0")
            e.pack(side="right", fill="x", expand=True)
            self.coord_entries.append(e)

    def _add_charge(self):
        """
        Obtiene:
        • valor numérico (float)
        • prefijo SI (combobox)
        • coordenadas (según dimensión)
        Calcula q = valor * factor(prefijo) y agrega a la tabla/diccionario.
        Luego limpia campos de valor y coordenadas para la siguiente carga.
        """
        val_str = self.entry_valor.get().strip()
        if val_str == "":
            messagebox.showerror("Error en carga", "Ingresa un valor numérico para la carga.")
            return
        try:
            valor = float(val_str)
        except ValueError:
            messagebox.showerror("Error en carga", "El valor debe ser numérico (puede tener decimales).")
            return

        pref = self.prefix_var.get()
        factor = PREFIXES.get(pref, None)
        if factor is None:
            messagebox.showerror("Error en prefijo", "Selecciona un prefijo SI válido.")
            return

        q = valor * factor

        try:
            coords = tuple(float(e.get()) for e in self.coord_entries)
        except ValueError:
            messagebox.showerror("Error en coordenadas", "Usa números reales en las coordenadas.")
            return

        cid = f"Carga{self._next_idx}"
        self.cargas[cid] = {"valor_C": q, "coordenadas": coords}
        self._next_idx += 1

        x = f"{coords[0]:.3g}" if len(coords) > 0 else "—"
        y = f"{coords[1]:.3g}" if len(coords) > 1 else "—"
        z = f"{coords[2]:.3g}" if len(coords) > 2 else "—"
        self.table.insert("", "end", values=(cid, f"{q:.2e}", x, y, z))

        # Limpieza: valor y coordenadas
        self.entry_valor.delete(0, "end")
        for e in self.coord_entries:
            e.delete(0, "end")  # dejar vacío para que el usuario escriba lo correcto

        self._draw_placeholder()


    def _clear_all(self):
        self.cargas.clear()
        self._next_idx = 1
        for r in self.table.get_children():
            self.table.delete(r)
        self.lbl_mag.config(text="‣ |F| = —")
        self.lbl_vec.config(text="‣ F⃗  = (—)")
        self._draw_placeholder()

    def _compute_and_plot(self):
        if not self.cargas:
            messagebox.showinfo("Sin datos", "Agrega al menos una carga.")
            return

        dim = self.dimension.get()
        F = calcular_sumatoria(self.cargas, dim)
        mag = magnitud_vector(F)

        if dim == 1:
            self.lbl_vec.config(text=f"‣ F⃗  = ({F[0]:+.2e} î) N")
        elif dim == 2:
            self.lbl_vec.config(text=f"‣ F⃗  = ({F[0]:+.2e} î, {F[1]:+.2e} ĵ) N")
        else:
            self.lbl_vec.config(text=f"‣ F⃗  = ({F[0]:+.2e} î, {F[1]:+.2e} ĵ, {F[2]:+.2e} k̂) N")
        self.lbl_mag.config(text=f"‣ |F| = {mag:.2e} N")

        self._draw_plot(F, mag)

    # -------------------------------- Dibujo ---------------------------------
    def _draw_placeholder(self):
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(COLOR_WHITE)
        ax.axis("off")
        ax.text(0.5, 0.5, "Agrega cargas para visualizar\ny calcular la fuerza",
                ha="center", va="center", fontsize=14, color=COLOR_BG_DARK)
        self.canvas.draw_idle()

    def _draw_plot(self, F, mag):
        dim = self.dimension.get()
        items = sorted(self.cargas.items(), key=lambda x: x[0])
        ref_id, ref_data = items[0]
        r_ref = ref_data["coordenadas"]

        self.fig.clf()

        if dim in (1, 2):
            ax = self.fig.add_subplot(111)
            ax.set_facecolor(COLOR_WHITE)

            x_vals = [d["coordenadas"][0] for _, d in items]
            y_vals = [ (d["coordenadas"][1] if dim == 2 else 0.0) for _, d in items]

            ax.scatter(x_vals, y_vals, s=50, marker='o',
                       edgecolors=COLOR_BG_DARK, facecolors="#B3D4FF")

            for (cid, d) in items:
                x = d["coordenadas"][0]
                y = d["coordenadas"][1] if dim == 2 else 0.0
                ax.annotate(f"{cid}\n{d['valor_C']:.2e} C", (x, y),
                            xytext=(6, 8), textcoords="offset points",
                            color=COLOR_BG_DARK)

            min_x, max_x = min(x_vals), max(x_vals)
            min_y, max_y = (min(y_vals), max(y_vals)) if dim == 2 else (0, 0)
            if min_x == max_x: min_x, max_x = min_x - 1, max_x + 1
            if dim == 2 and min_y == max_y: min_y, max_y = min_y - 1, max_y + 1

            extent_x = max_x - min_x
            extent_y = (max_y - min_y) if dim == 2 else extent_x
            max_dim = max(extent_x, extent_y, 1e-9)

            desired_length = 0.22 * max_dim
            scale = 0 if mag == 0 else desired_length / mag
            Fx, Fy = (F[0]*scale, (F[1]*scale if dim == 2 else 0))

            ax.arrow(r_ref[0], (r_ref[1] if dim == 2 else 0),
                     Fx, Fy,
                     head_width=0.03*max_dim, length_includes_head=True,
                     linewidth=2.0, color=COLOR_ACCENT)

            margin = 0.25 * max_dim
            ax.set_xlim(min_x - margin, max_x + margin)
            if dim == 2:
                ax.set_ylim(min_y - margin, max_y + margin)
                ax.set_aspect("equal", "box")

            ax.set_xlabel("X (m)", color=COLOR_BG_DARK)
            if dim == 2:
                ax.set_ylabel("Y (m)", color=COLOR_BG_DARK)
            ax.set_title("Posición de cargas y F⃗ (2D)" if dim == 2 else "Posición de cargas y F⃗ (1D)",
                         color=COLOR_BG_DARK, pad=12)

        else:
            ax = self.fig.add_subplot(111, projection="3d")
            ax.set_facecolor(COLOR_WHITE)

            x_vals = [d["coordenadas"][0] for _, d in items]
            y_vals = [d["coordenadas"][1] for _, d in items]
            z_vals = [d["coordenadas"][2] for _, d in items]

            ax.scatter(x_vals, y_vals, z_vals, s=40, marker='o',
                       edgecolors=COLOR_BG_DARK, facecolors="#B3D4FF")

            for (cid, d) in items:
                x, y, z = d["coordenadas"]
                ax.text(x, y, z, f"{cid}\n{d['valor_C']:.2e} C", color=COLOR_BG_DARK)

            min_x, max_x = min(x_vals), max(x_vals)
            min_y, max_y = min(y_vals), max(y_vals)
            min_z, max_z = min(z_vals), max(z_vals)
            if min_x == max_x: min_x, max_x = min_x - 1, max_x + 1
            if min_y == max_y: min_y, max_y = min_y - 1, max_y + 1
            if min_z == max_z: min_z, max_z = min_z - 1, max_z + 1

            ext_x = max_x - min_x
            ext_y = max_y - min_y
            ext_z = max_z - min_z
            max_dim = max(ext_x, ext_y, ext_z, 1e-9)

            desired_length = 0.6 * max_dim
            scale = 0 if mag == 0 else desired_length / mag
            Fx, Fy, Fz = F[0]*scale, F[1]*scale, F[2]*scale

            ax.quiver(r_ref[0], r_ref[1], r_ref[2], Fx, Fy, Fz,
                      color=COLOR_ACCENT, arrow_length_ratio=0.1, linewidth=2.0)

            margin = 0.25 * max_dim
            ax.set_xlim(min_x - margin, max_x + margin)
            ax.set_ylim(min_y - margin, max_y + margin)
            ax.set_zlim(min_z - margin, max_z + margin)
            ax.set_box_aspect((1, 1, 1))
            ax.set_xlabel("X (m)", color=COLOR_BG_DARK)
            ax.set_ylabel("Y (m)", color=COLOR_BG_DARK)
            ax.set_zlabel("Z (m)", color=COLOR_BG_DARK)
            ax.set_title("Posición de cargas y F⃗ (3D)", color=COLOR_BG_DARK, pad=12)

        self.canvas.draw_idle()

if __name__ == "__main__":
    app = App()
    try:
        from tkinter import font as tkfont
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Treeview", background=COLOR_WHITE, fieldbackground=COLOR_WHITE, foreground=COLOR_BG_DARK)
        style.configure("TCombobox", fieldbackground=COLOR_WHITE, foreground=COLOR_BG_DARK)
    except Exception:
        pass

    app.mainloop()
