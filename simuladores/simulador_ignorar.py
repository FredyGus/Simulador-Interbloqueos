import os
import random
import time
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import scrolledtext, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# --- CONFIGURACIÓN DE SIMULACIÓN ---
USE_FIXED_SEED = True
FIXED_SEED_VALUE = 7  # Mantiene el comportamiento fijo en cada ejecución
if USE_FIXED_SEED:
    random.seed(FIXED_SEED_VALUE)

# --- ARCHIVOS DE SALIDA ---
DATA_DIR = os.path.join("data", "logs_ignorar")
os.makedirs(DATA_DIR, exist_ok=True)
LOG_FILE = os.path.join(DATA_DIR, "simulacion_ignorar_log.txt")
METRICS_FILE = os.path.join(DATA_DIR, "simulacion_ignorar_metrics.txt")


# --- CLASE PROCESO ---
class Proceso:
    def __init__(self, pid):
        self.id = f"P{pid}"
        self.asignados = set()
        self.solicitando = None
        self.estado = "Listo"
        self.tiempo_inicio = time.time()
        self.solicitudes_realizadas = 0
        self.max_solicitudes = random.randint(3, 7)
        self.finalizado = False


# --- CLASE PRINCIPAL ---
class SimuladorIgnorar:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador — Política de Ignorar Interbloqueos")
        self.root.geometry("1400x800")
        self.style = tb.Style("darkly")

        # Colores base
        self.bg_panel = "#27343e"
        self.text_color = "#f1f5f9"

        # Configuración
        self.NUM_PROCESOS = 10
        self.NUM_RECURSOS = 10
        self.recursos = {f"R{i}": None for i in range(self.NUM_RECURSOS)}
        self.procesos = [Proceso(i) for i in range(self.NUM_PROCESOS)]
        self.G = nx.DiGraph()
        self.deadlock_detectado = False

        # Estadísticas
        self.solicitudes_totales = 0
        self.solicitudes_aceptadas = 0
        self.solicitudes_bloqueadas = 0
        self.tiempo_inicio = time.time()
        self.pasos_totales = 0
        self.simulacion_activa = True

        self.crear_interfaz()
        self.log_evento("💤 Simulación iniciada bajo política de IGNORAR (sin prevención ni resolución).")
        self.iniciar_simulacion()

    # === INTERFAZ ===
    def crear_interfaz(self):
        main_frame = tb.Frame(self.root, bootstyle="dark", padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Layout principal
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        right_frame = tb.Labelframe(main_frame, text="Registro de Eventos (Log)", bootstyle="secondary")
        right_frame.pack(side=RIGHT, fill=Y)

        # === Grafo ===
        graph_frame = tb.Labelframe(left_frame, text="Grafo — Política de Ignorar", bootstyle="info", padding=10)
        graph_frame.pack(fill=BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.ax.set_facecolor(self.bg_panel)
        self.fig.patch.set_facecolor(self.bg_panel)
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        # === Zona inferior ===
        bottom_frame = tb.Frame(left_frame)
        bottom_frame.pack(fill=X, pady=(10, 0))

        estado_frame = tb.Labelframe(bottom_frame, text="Estado de Procesos", bootstyle="secondary")
        estado_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        condiciones_frame = tb.Labelframe(bottom_frame, text="Condiciones del Interbloqueo", bootstyle="secondary")
        condiciones_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Estado de procesos
        self.estado_text = tk.Text(
            estado_frame,
            height=15,
            bg=self.bg_panel,
            fg=self.text_color,
            insertbackground="white",
            font=("Consolas", 10),
            relief="flat"
        )
        self.estado_text.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Checkboxes (todas activas)
        self.condiciones = {
            "Exclusión mutua": tk.BooleanVar(value=True),
            "Retener y esperar": tk.BooleanVar(value=True),
            "No expropiación": tk.BooleanVar(value=True),
            "Espera circular": tk.BooleanVar(value=True),
        }

        for cond, var in self.condiciones.items():
            chk = tb.Checkbutton(
                condiciones_frame,
                text=cond,
                variable=var,
                bootstyle=("danger", "round-toggle"),
                state=DISABLED,
            )
            chk.pack(anchor="w", padx=10, pady=5)

        # Log
        self.log_text = scrolledtext.ScrolledText(
            right_frame,
            width=100,
            height=35,
            bg=self.bg_panel,
            fg=self.text_color,
            font=("Consolas", 10),
            relief="flat",
            wrap=tk.WORD,
        )
        self.log_text.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.log_file = open(LOG_FILE, "w", encoding="utf-8")

    # === LOG ===
    def log_evento(self, mensaje):
        timestamp = datetime.now().strftime("%H:%M:%S")
        texto = f"[{timestamp}] {mensaje}"
        self.log_text.insert(tk.END, texto + "\n")
        self.log_text.see(tk.END)
        self.log_file.write(texto + "\n")

    # === SIMULACIÓN ===
    def iniciar_simulacion(self):
        if self.simulacion_activa:
            self.simular_paso()
            self.root.after(700, self.iniciar_simulacion)

    def simular_paso(self):
        if self.deadlock_detectado:
            return

        self.pasos_totales += 1
        if self.pasos_totales > 3000:
            self.log_evento("⚠️ Límite de pasos alcanzado. Fin de simulación.")
            self.finalizar_simulacion()
            return

        if all(p.finalizado for p in self.procesos):
            self.finalizar_simulacion()
            return

        proceso = random.choice([p for p in self.procesos if not p.finalizado])
        recurso = random.choice(list(self.recursos.keys()))
        self.solicitudes_totales += 1

        # Asignar si está libre
        if self.recursos[recurso] is None:
            self.recursos[recurso] = proceso.id
            proceso.asignados.add(recurso)
            proceso.estado = "Ejecutando"
            self.solicitudes_aceptadas += 1
            proceso.solicitudes_realizadas += 1
            self.log_evento(f"✅ {proceso.id} obtuvo {recurso}. [{proceso.solicitudes_realizadas}/{proceso.max_solicitudes}]")

            # Si terminó, libera recursos
            if proceso.solicitudes_realizadas >= proceso.max_solicitudes:
                for r in list(proceso.asignados):
                    self.recursos[r] = None
                proceso.asignados.clear()
                proceso.estado = "Terminado"
                proceso.finalizado = True
                self.log_evento(f"🏁 {proceso.id} completó todas sus solicitudes y liberó sus recursos.")
        else:
            # Espera (posible bloqueo)
            proceso.estado = "Bloqueado"
            proceso.solicitando = recurso
            self.solicitudes_bloqueadas += 1
            self.log_evento(f"⏳ {proceso.id} espera {recurso} (retenido por {self.recursos[recurso]}).")

        self.detectar_interbloqueo()
        self.dibujar_grafo()

    # === DETECCIÓN VISUAL DE INTERBLOQUEO ===
    def detectar_interbloqueo(self):
        G = nx.DiGraph()

        for p in self.procesos:
            if p.solicitando:
                r = p.solicitando
                dueño = self.recursos.get(r)
                if dueño and dueño != p.id:
                    G.add_edge(p.id, dueño)

        try:
            ciclo = nx.find_cycle(G, orientation="original")
            procesos_ciclo = sorted(set([u for u, v, _ in ciclo] + [v for u, v, _ in ciclo]))
            self.deadlock_detectado = True
            self.simulacion_activa = False
            self.log_evento(f"💥 INTERBLOQUEO DETECTADO: {' - '.join(procesos_ciclo)}")
            messagebox.showwarning("💥 Interbloqueo Detectado", f"Procesos involucrados: {', '.join(procesos_ciclo)}\n\nSimulación detenida.")
        except nx.NetworkXNoCycle:
            pass

    # === GRAFO ===
    def dibujar_grafo(self):
        self.G.clear()
        procesos = [p.id for p in self.procesos]
        recursos = list(self.recursos.keys())

        pos = {p: (0, -i) for i, p in enumerate(procesos)}
        pos.update({r: (1, -i) for i, r in enumerate(recursos)})

        for p in self.procesos:
            self.G.add_node(p.id, tipo="P", estado=p.estado)
        for r in recursos:
            self.G.add_node(r, tipo="R")

        for p in self.procesos:
            for rec in p.asignados:
                self.G.add_edge(p.id, rec, tipo="posee")
            if p.solicitando:
                self.G.add_edge(p.id, p.solicitando, tipo="solicita")

        self.ax.clear()
        node_colors = []
        for n in self.G.nodes():
            if self.G.nodes[n]["tipo"] == "P":
                estado = self.G.nodes[n]["estado"]
                if estado == "Bloqueado":
                    node_colors.append("#e74c3c")  # rojo fuerte
                elif estado == "Ejecutando":
                    node_colors.append("#3498db")
                elif estado == "Terminado":
                    node_colors.append("#2ecc71")
                else:
                    node_colors.append("#95a5a6")
            else:
                node_colors.append("#2ecc71")

        edge_colors = []
        styles = []
        for _, _, data in self.G.edges(data=True):
            if data["tipo"] == "posee":
                edge_colors.append("#2ecc71"); styles.append("solid")
            elif data["tipo"] == "solicita":
                edge_colors.append("#f1c40f"); styles.append("dashed")

        nx.draw_networkx(
            self.G,
            pos,
            node_color=node_colors,
            node_shape="o",
            node_size=1000,
            font_color="white",
            font_size=9,
            edge_color=edge_colors,
            style=styles,
            ax=self.ax,
        )

        completados = sum(p.finalizado for p in self.procesos)
        self.ax.set_title(
            f"Grafo de Asignación y Solicitud ({completados}/{self.NUM_PROCESOS} Completados)",
            color=self.text_color
        )
        self.canvas.draw()
        self.actualizar_estado_procesos()

    # === ESTADO ===
    def actualizar_estado_procesos(self):
        self.estado_text.delete("1.0", tk.END)
        texto = "--- ESTADO DE PROCESOS ---\n"
        for p in self.procesos:
            linea = f"[{p.estado}] {p.id}"
            if p.asignados:
                linea += f" (Posee: {', '.join(sorted(p.asignados))})"
            if p.solicitando:
                linea += f" (Pide: {p.solicitando})"
            texto += linea + "\n"
        self.estado_text.insert(tk.END, texto)

    # === FINALIZACIÓN ===
    def finalizar_simulacion(self):
        self.simulacion_activa = False
        tiempo_total = time.time() - self.tiempo_inicio

        metricas = {
            "Solicitudes totales": self.solicitudes_totales,
            "Solicitudes aceptadas": self.solicitudes_aceptadas,
            "Solicitudes bloqueadas": self.solicitudes_bloqueadas,
            "Procesos completados": sum(p.finalizado for p in self.procesos),
            "Duración total (s)": round(tiempo_total, 2),
        }

        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            f.write("--- MÉTRICAS DE SIMULACIÓN DE IGNORAR ---\n")
            for k, v in metricas.items():
                f.write(f"{k}: {v}\n")

        self.log_evento("✅ Simulación finalizada.")
        self.log_evento(f"📊 Métricas guardadas en {METRICS_FILE}")
        self.log_file.close()


# --- MAIN ---
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = SimuladorIgnorar(root)
    root.mainloop()
