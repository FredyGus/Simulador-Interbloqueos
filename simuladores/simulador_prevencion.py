import os
import random
import time
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import scrolledtext
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# --- CONFIGURACION DE SIMULACION ---
USE_FIXED_SEED = True
FIXED_SEED_VALUE = 7
if USE_FIXED_SEED:
    random.seed(FIXED_SEED_VALUE)

# --- CONFIGURACIÓN DE ARCHIVOS ---
DATA_DIR = os.path.join("data", "logs_prevencion")
os.makedirs(DATA_DIR, exist_ok=True)
LOG_FILE = os.path.join(DATA_DIR, "simulacion_prevencion_log.txt")
METRICS_FILE = os.path.join(DATA_DIR, "simulacion_prevencion_metrics.txt")


# --- CLASE PROCESO ---
class Proceso:
    def __init__(self, pid):
        self.id = f"P{pid}"
        self.asignados = set()
        self.solicitando = None
        self.estado = "Listo"
        self.orden = random.sample([f"R{i}" for i in range(10)], 10)
        self.tiempo_inicio = time.time()
        self.tiempo_espera_total = 0
        self.solicitudes_realizadas = 0
        self.max_solicitudes = random.randint(3, 7)
        self.finalizado = False
        self.intentos_fallidos = 0
        self.reinicios = 0


# --- CLASE PRINCIPAL ---
class SimuladorPrevencion:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Prevención de Interbloqueos — SO")
        self.root.geometry("1400x800")
        self.style = tb.Style("darkly")

        # Colores base
        self.bg_main = "#1e2a33"
        self.bg_panel = "#27343e"
        self.text_color = "#f1f5f9"

        # Configuración general
        self.NUM_PROCESOS = 10
        self.NUM_RECURSOS = 10
        self.recursos = {f"R{i}": None for i in range(self.NUM_RECURSOS)}
        self.procesos = [Proceso(i) for i in range(self.NUM_PROCESOS)]

        # Estadísticas
        self.solicitudes_totales = 0
        self.solicitudes_denegadas = 0
        self.solicitudes_aceptadas = 0
        self.tiempo_inicio_simulacion = time.time()
        self.simulacion_activa = True
        self.pasos_totales = 0

        self.crear_interfaz()
        self.log_evento("🧠 Simulación de PREVENCIÓN iniciada.")
        self.iniciar_simulacion()

    # === INTERFAZ ===
    def crear_interfaz(self):
        main_frame = tb.Frame(self.root, bootstyle="dark", padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Estructura general
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        right_frame = tb.Labelframe(main_frame, text="Registro de Eventos (Log)", bootstyle="secondary")
        right_frame.pack(side=RIGHT, fill=Y)

        # === Grafo ===
        graph_frame = tb.Labelframe(left_frame, text="Grafo — Política de Prevención", bootstyle="info", padding=10)
        graph_frame.pack(fill=BOTH, expand=True)

        self.G = nx.DiGraph()
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.ax.set_facecolor(self.bg_panel)
        self.fig.patch.set_facecolor(self.bg_panel)
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=BOTH, expand=True)

        # === Zona inferior ===
        bottom_frame = tb.Frame(left_frame)
        bottom_frame.pack(fill=X, pady=(10, 0), ipady=10)

        estado_frame = tb.Labelframe(bottom_frame, text="Estado de Procesos", bootstyle="secondary")
        estado_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        condiciones_frame = tb.Labelframe(bottom_frame, text="Condiciones del Interbloqueo", bootstyle="secondary")
        condiciones_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Textbox estado procesos
        self.estado_text = tk.Text(
            estado_frame,
            height=15,
            bg=self.bg_panel,
            fg=self.text_color,
            insertbackground="white",
            font=("Consolas", 10),
            relief="flat",
        )
        self.estado_text.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Checkboxes de condiciones
        self.condiciones = {
            "Exclusión mutua": tk.BooleanVar(value=False),
            "Retener y esperar": tk.BooleanVar(value=False),
            "No expropiación": tk.BooleanVar(value=False),
            "Espera circular": tk.BooleanVar(value=False),
        }

        for cond, var in self.condiciones.items():
            chk = tb.Checkbutton(
                condiciones_frame,
                text=cond,
                variable=var,
                bootstyle=("success" if not var.get() else "danger", "round-toggle"),
                state=DISABLED,
            )
            chk.pack(anchor="w", padx=10, pady=5)

        # === Log (derecha) ===
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
        self.pasos_totales += 1

        # Límite de seguridad (previene loops infinitos)
        if self.pasos_totales > 3000:
            self.log_evento("⚠️ Simulación detenida automáticamente (límite de iteraciones alcanzado).")
            self.finalizar_simulacion()
            return

        # Si todos los procesos han terminado → detener simulación
        if all(p.finalizado for p in self.procesos):
            self.finalizar_simulacion()
            return

        proceso = random.choice([p for p in self.procesos if not p.finalizado])
        recurso = random.choice(list(self.recursos.keys()))
        self.solicitudes_totales += 1

        # Política de prevención: mantener orden ascendente
        if proceso.asignados:
            mayor_asignado = max(proceso.asignados, key=lambda r: proceso.orden.index(r))
            if proceso.orden.index(recurso) < proceso.orden.index(mayor_asignado):
                self.solicitudes_denegadas += 1
                proceso.estado = "Esperando"
                proceso.intentos_fallidos += 1
                self.log_evento(
                    f"⚠️ PREVENCIÓN: {proceso.id} intentó pedir {recurso} fuera de orden. Solicitud denegada."
                )

                # Reinicio inteligente si falla muchas veces
                if proceso.intentos_fallidos > 5:
                    for r in list(proceso.asignados):
                        self.recursos[r] = None
                        proceso.asignados.remove(r)
                    proceso.intentos_fallidos = 0
                    proceso.reinicios += 1
                    self.log_evento(
                        f"🔁 {proceso.id} reinicia su ciclo de solicitudes para evitar espera circular."
                    )
                self.dibujar_grafo(recurso_denegado=(proceso.id, recurso))
                return

        # Asignación de recurso si libre
        if self.recursos[recurso] is None:
            self.recursos[recurso] = proceso.id
            proceso.asignados.add(recurso)
            proceso.estado = "Ejecutando"
            self.solicitudes_aceptadas += 1
            proceso.solicitudes_realizadas += 1
            proceso.intentos_fallidos = 0
            self.log_evento(f"✅ {proceso.id} obtuvo {recurso}. [{proceso.solicitudes_realizadas}/{proceso.max_solicitudes}]")

            # Finalización de proceso cuando llega a su máximo
            if proceso.solicitudes_realizadas >= proceso.max_solicitudes:
                # Liberar todos los recursos que posee
                for r in list(proceso.asignados):
                    self.recursos[r] = None
                proceso.asignados.clear()

                # Reset total del proceso
                proceso.solicitando = None
                proceso.estado = "Terminado"
                proceso.finalizado = True

                self.log_evento(f"🏁 {proceso.id} ha completado todas sus solicitudes y liberó sus recursos.")
        else:
            proceso.estado = "Bloqueado"
            proceso.solicitando = recurso
            proceso.intentos_fallidos += 1
            self.log_evento(f"⏳ {proceso.id} espera {recurso} (retenido por {self.recursos[recurso]}).")

        self.dibujar_grafo()

    # === DIBUJAR GRAFO ===
    def dibujar_grafo(self, recurso_denegado=None):
        self.G.clear()
        pos = {}
        procesos = [p.id for p in self.procesos]
        recursos = [r for r in self.recursos.keys()]

        for i, p in enumerate(procesos):
            pos[p] = (0, -i)
        for i, r in enumerate(recursos):
            pos[r] = (1, -i)

        for p in self.procesos:
            self.G.add_node(p.id, tipo="P", estado=p.estado)
        for r in recursos:
            self.G.add_node(r, tipo="R")

        for p in self.procesos:
            for rec in p.asignados:
                self.G.add_edge(p.id, rec, tipo="posee")
            if p.solicitando:
                self.G.add_edge(p.id, p.solicitando, tipo="solicita")

        if recurso_denegado:
            self.G.add_edge(recurso_denegado[0], recurso_denegado[1], tipo="denegado")

        self.ax.clear()
        node_colors = []
        for n in self.G.nodes():
            if self.G.nodes[n]["tipo"] == "P":
                estado = self.G.nodes[n]["estado"]
                if estado == "Bloqueado":
                    node_colors.append("#e67e22")
                elif estado == "Ejecutando":
                    node_colors.append("#3498db")
                elif estado == "Terminado":
                    node_colors.append("#2ecc71")
                elif estado == "Esperando":
                    node_colors.append("#9b59b6")
                else:
                    node_colors.append("#95a5a6")
            else:
                node_colors.append("#2ecc71")

        edge_colors, styles = [], []
        for _, _, data in self.G.edges(data=True):
            if data["tipo"] == "posee":
                edge_colors.append("#2ecc71"); styles.append("solid")
            elif data["tipo"] == "solicita":
                edge_colors.append("#f1c40f"); styles.append("dashed")
            elif data["tipo"] == "denegado":
                edge_colors.append("#e74c3c"); styles.append("dashed")

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
        self.ax.axis("off")
        self.canvas.draw()
        self.actualizar_estado_procesos()

    # === ESTADO DE PROCESOS ===
    def actualizar_estado_procesos(self):
        self.estado_text.delete("1.0", tk.END)
        texto = "--- ESTADO DE PROCESOS ---\n"
        for p in self.procesos:
            linea = f"[{p.estado}] {p.id}"
            if p.asignados:
                linea += f" (Posee: {', '.join(sorted(p.asignados))})"
            if p.solicitando:
                linea += f" (Pide: {p.solicitando})"
            if p.reinicios > 0:
                linea += f" | Reinicios: {p.reinicios}"
            texto += linea + "\n"
        self.estado_text.insert(tk.END, texto)

    # === FINALIZACIÓN Y MÉTRICAS ===
    def finalizar_simulacion(self):
        self.simulacion_activa = False
        tiempo_total = time.time() - self.tiempo_inicio_simulacion

        metricas = {
            "Solicitudes totales": self.solicitudes_totales,
            "Solicitudes aceptadas": self.solicitudes_aceptadas,
            "Solicitudes denegadas": self.solicitudes_denegadas,
            "Procesos completados": sum(p.finalizado for p in self.procesos),
            "Duración total (s)": round(tiempo_total, 2),
            "Duración promedio por proceso (s)": round(tiempo_total / self.NUM_PROCESOS, 2),
        }

        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            f.write("--- MÉTRICAS DE SIMULACIÓN DE PREVENCIÓN ---\n")
            for k, v in metricas.items():
                f.write(f"{k}: {v}\n")

        self.log_evento("✅ Simulación finalizada — todos los procesos completaron sus solicitudes.")
        self.log_evento(f"📊 Métricas guardadas en: {METRICS_FILE}")
        self.log_file.close()


# --- MAIN ---
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = SimuladorPrevencion(root)
    root.mainloop()
