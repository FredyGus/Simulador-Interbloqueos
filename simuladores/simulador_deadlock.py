import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
from datetime import datetime
import os

DATA_DIR = os.path.join("data", "logs_deteccion")

# --- 1. CONFIGURACIÓN INICIAL ---
NUM_PROCESOS = 10
LOG_FILENAME = os.path.join(DATA_DIR, "simulacion_deadlock_log.txt")
METRICS_FILENAME = os.path.join(DATA_DIR, "simulacion_deadlock_metrics.txt")

# --- 2. CLASES DEL SISTEMA ---

class Proceso:
    def __init__(self, pid):
        self.id = f"P{pid}"
        self.asignados = set()
        self.solicitando = None
        self.tiempo_inicio = time.time()
        self.tiempo_espera_total = 0
        self.tiempo_bloqueo_inicio = None
        self.estado = "Listo" # Listo, Ejecutando, Bloqueado, Terminado

    def __repr__(self):
        return f"Proceso({self.id}, Estado: {self.estado})"

class SimuladorDeadlock:
    def __init__(self, root):
        self.root = root
        
        self.recursos = {} 

        # Lista que contiene los 10 procesos iniciales (P0-P9)
        self.procesos = [Proceso(i) for i in range(NUM_PROCESOS)]
        
        self.procesos_terminados_exitosamente = set()
        self.after_id = None
        self.indice_proceso_actual = 0 
        self.deadlock_cycle = None
        
        # Estadísticas
        self.solicitudes_totales = 0
        self.solicitudes_satisfechas = 0
        self.bloqueos_temporales = 0
        self.interbloqueos_detectados = 0
        self.procesos_victimas = 0
        self.tiempo_simulacion_inicio = time.time()
        
        self.patron_interbloqueo = self.generar_multiples_patrones_deadlock()
        
        self.setup_gui() 
            
        try:
            self.log_file = open(LOG_FILENAME, "w", encoding="utf-8")
        except Exception as e:
            print(f"Advertencia: No se pudo abrir el archivo de log con UTF-8: {e}")
            self.log_file = None 
            
        self.log_event("Simulación Iniciada (Múltiples Interbloqueos Forzados).")
        
        self.ciclo_simulacion()

    def generar_multiples_patrones_deadlock(self):
        """
        Genera múltiples patrones de interbloqueo de dos vías y define el pool de recursos.
        """
        pattern = {}
        
        deadlock_pairs = [
            ("P0", "P1", "R0", "R1"),
            ("P2", "P6", "R2", "R3"),
            ("P4", "P8", "R4", "R5"),
        ]
        
        recursos_utilizados = set()
        procesos_ocupados = set()
        
        for p_a, p_b, r_x, r_y in deadlock_pairs:
            procesos_ocupados.add(p_a)
            procesos_ocupados.add(p_b)
            recursos_utilizados.add(r_x)
            recursos_utilizados.add(r_y)
            
            pattern[p_a] = (r_x, r_y) 
            pattern[p_b] = (r_y, r_x) 

        # Patrón simple para el resto de procesos
        next_free_resource_index = 6
        for i in range(NUM_PROCESOS):
            pid = f"P{i}"
            if pid not in procesos_ocupados:
                # Usamos recursos R6, R7, R8, R9
                r_simple = f"R{next_free_resource_index}"
                pattern[pid] = (r_simple, r_simple) 
                recursos_utilizados.add(r_simple)
                next_free_resource_index += 1
                
        self.recursos = {r_id: None for r_id in sorted(list(recursos_utilizados))}
        
        return pattern

    # --- 3. GESTIÓN DEL SISTEMA ---

    def solicitar_recurso(self, proceso, recurso_id):
        self.solicitudes_totales += 1
        proceso.solicitando = recurso_id
        
        if self.recursos.get(recurso_id) is None:
            self.recursos[recurso_id] = proceso.id
            proceso.asignados.add(recurso_id)
            proceso.solicitando = None
            proceso.estado = "Ejecutando"
            self.solicitudes_satisfechas += 1
            self.log_event(f"ASIGNADO: {proceso.id} a {recurso_id}. Estado: {proceso.estado}")
            return True
        else:
            proceso.estado = "Bloqueado"
            self.bloqueos_temporales += 1
            if proceso.tiempo_bloqueo_inicio is None:
                proceso.tiempo_bloqueo_inicio = time.time()
            self.log_event(f"BLOQUEO: {proceso.id} solicita {recurso_id}, retenido por {self.recursos[recurso_id]}.")
            return False

    def liberar_recursos(self, proceso):
        for rec in list(proceso.asignados):
            if self.recursos.get(rec) == proceso.id:
                 self.recursos[rec] = None
            proceso.asignados.remove(rec)
            self.log_event(f"LIBERADO: {proceso.id} liberó el recurso {rec}.")
            
        if proceso.tiempo_bloqueo_inicio is not None:
            proceso.tiempo_espera_total += (time.time() - proceso.tiempo_bloqueo_inicio)
            proceso.tiempo_bloqueo_inicio = None
        
        proceso.estado = "Listo"
        self.despertar_bloqueados()

    # --- 4. DETECCIÓN Y RECUPERACIÓN ---

    def detectar_interbloqueo(self):
        G = nx.DiGraph()
        
        # 1. Construir el Grafo de Espera (Edges P -> P)
        for p in self.procesos:
            if p.solicitando:
                recurso_solicitado = p.solicitando
                proceso_dueno_id = self.recursos.get(recurso_solicitado)
                # Arista P_solicitante -> P_dueno
                if proceso_dueno_id and proceso_dueno_id != p.id:
                    G.add_edge(p.id, proceso_dueno_id)
        
        # 2. Buscar Ciclos
        try:
            cycle_edges = nx.find_cycle(G, orientation='original')
            
            cycle_pids = set()
            for u, v, data in cycle_edges:
                cycle_pids.add(u)
                cycle_pids.add(v)
                
            self.interbloqueos_detectados += 1
            self.deadlock_cycle = sorted(list(cycle_pids)) 
            self.log_event(f"!!! INTERBLOQUEO DETECTADO !!! Ciclo: {self.deadlock_cycle}.")
            
            return True
        except nx.NetworkXNoCycle:
            self.deadlock_cycle = None
            return False

    def notificar_y_resolver(self):
        
        self.dibujar_grafo() 
        self.actualizar_indicadores_deadlock(is_deadlock_detected=True) # Actualizar indicadores a Verde Total
        
        if self.after_id:
            self.root.after_cancel(self.after_id)

        procesos_ciclo_str = ", ".join(self.deadlock_cycle)
            
        messagebox.showwarning("🚨 Interbloqueo Detectado", 
                               "Se ha detectado un Interbloqueo (Deadlock). El sistema está estancado.\n\n" \
                               f"**Procesos involucrados:** {procesos_ciclo_str}\n\n"
                               "Aplicando medidas correctivas en 3 segundos...")
        
        self.root.after(3000, self._resolver_interbloqueo_paso_2)

    def _resolver_interbloqueo_paso_2(self):
        
        if not self.deadlock_cycle:
            self.log_event("ADVERTENCIA: Intento de resolución sin ciclo detectado. Continuando simulación.")
            self.actualizar_indicadores_deadlock()
            self.ciclo_simulacion()
            return
            
        # 1. Identificar procesos en el ciclo
        procesos_en_ciclo = [p for p in self.procesos if p.id in self.deadlock_cycle]
        
        if not procesos_en_ciclo:
            self.log_event("ADVERTENCIA: Ciclo detectado pero procesos no encontrados. Continuando simulación.")
            self.deadlock_cycle = None
            self.actualizar_indicadores_deadlock()
            self.ciclo_simulacion()
            return

        # 2. Seleccionar la VÍCTIMA (criterio de menor cantidad de recursos, desempatando por más antiguo)
        
        def criterio_victima(proceso):
            # Tupla: (cantidad_recursos_asignados, -tiempo_inicio)
            return (len(proceso.asignados), -proceso.tiempo_inicio)
        
        victima = min(procesos_en_ciclo, key=criterio_victima)
        
        # Matar al proceso víctima
        self.log_event(f"💀 RESOLVIENDO: Matando a la víctima {victima.id} del ciclo {self.deadlock_cycle} (Posee {len(victima.asignados)} recursos).")
        self.procesos_victimas += 1
        
        # 3. Liberar y reiniciar
        self.liberar_recursos(victima)
        self.reiniciar_proceso(victima) 
        
        self.deadlock_cycle = None 
        
        messagebox.showinfo("✅ Medidas Correctivas Aplicadas", 
                             f"Medidas correctivas aplicadas.\n"
                             f"Proceso **{victima.id}** finalizado (reiniciado) para romper el ciclo.")
        
        self.actualizar_indicadores_deadlock() # Los indicadores vuelven a rojo (al romperse el ciclo)
        self.ciclo_simulacion()

    def reiniciar_proceso(self, proceso_victima):
        proceso_victima.asignados.clear()
        proceso_victima.solicitando = None
        proceso_victima.tiempo_espera_total = 0 
        proceso_victima.tiempo_bloqueo_inicio = None
        proceso_victima.estado = "Listo"
        self.log_event(f"Proceso {proceso_victima.id} Reiniciado y puesto en la cola de listos.")

    def despertar_bloqueados(self):
        for p in [p for p in self.procesos if p.estado == "Bloqueado"]:
            if p.solicitando and self.recursos.get(p.solicitando) is None:
                self.log_event(f"Despertando a {p.id}. Recurso {p.solicitando} liberado.")
                self.solicitar_recurso(p, p.solicitando)

    # --- INDICADORES DE DEADLOCK (NUEVA FUNCIÓN) ---
    
    def _get_deadlock_conditions_state(self):
        """
        Evalúa las 4 condiciones de interbloqueo.
        Retorna un diccionario de booleanos: {condicion: cumple}
        """
        
        # 1. Exclusión Mutua 
        # Todos los recursos en esta simulación son no compartibles (una sola instancia).
        mutua_exclusiva = True 
        
        # 2. Retención y Espera 
        # ¿Existe al menos un proceso que tiene un recurso y está esperando otro?
        retencion_y_espera = any(len(p.asignados) > 0 and p.solicitando is not None for p in self.procesos)
        
        # 3. No Expropiación 
        # Los recursos no pueden ser tomados a la fuerza (solo se liberan voluntariamente por el proceso al terminar o al ser víctima).
        no_expropiación = True 
        
        # 4. Espera Circular 
        # ¿Se ha detectado un ciclo en el Grafo de Espera?
        espera_circular = self.deadlock_cycle is not None
        
        return {
            "Exclusión Mutua": mutua_exclusiva,
            "Retención y Espera": retencion_y_espera,
            "No Expropiación": no_expropiación,
            "Espera Circular": espera_circular
        }

    def actualizar_indicadores_deadlock(self, is_deadlock_detected=False):
        """Actualiza los colores de los indicadores LED en la GUI."""
        
        conditions = self._get_deadlock_conditions_state()
        
        # Forzar todos a verde si la detección de ciclo es True
        if is_deadlock_detected:
            color_em = color_re = color_np = color_ec = 'green'
        else:
            color_em = 'green' if conditions["Exclusión Mutua"] else 'red'
            color_re = 'green' if conditions["Retención y Espera"] else 'red'
            color_np = 'green' if conditions["No Expropiación"] else 'red'
            color_ec = 'green' if conditions["Espera Circular"] else 'red' # Se pondrá en verde justo cuando se detecta el ciclo

        self.led_em.config(bg=color_em)
        self.led_re.config(bg=color_re)
        self.led_np.config(bg=color_np)
        self.led_ec.config(bg=color_ec)


    # --- 5. LOG Y GRÁFICOS ---

    def log_event(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if self.log_file is not None: 
            try:
                self.log_file.write(log_entry + "\n")
            except ValueError:
                pass 
        
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)

    def dibujar_grafo(self):
        self.G.clear()
        
        # Crear la lista de procesos (P0-P9) y recursos (R0, R1...)
        procs_list = sorted([p.id for p in self.procesos])
        res_list = sorted(list(self.recursos.keys()))
        
        pos = {}
        # Posición de Procesos (Columna 0)
        for i, p_id in enumerate(procs_list):
            proceso = next(p for p in self.procesos if p.id == p_id)
            self.G.add_node(p_id, type='P', estado=proceso.estado)
            pos[p_id] = (0, -i * 1.5) 
            
        # Posición de Recursos (Columna 1)
        for i, r_id in enumerate(res_list):
            self.G.add_node(r_id, type='R')
            pos[r_id] = (1, -i * 1.5) 
            
        # Añadir aristas (Asignación y Solicitud)
        for p in self.procesos:
            for rec in p.asignados:
                self.G.add_edge(rec, p.id, type='asignacion') 
        
        for p in self.procesos:
            if p.solicitando:
                self.G.add_edge(p.id, p.solicitando, type='solicitud')
        
        self.ax.clear() 
        
        node_colors = []
        for n in self.G.nodes():
            if self.G.nodes[n]['type'] == 'P':
                estado = self.G.nodes[n]['estado']
                if estado == 'Bloqueado':
                    node_colors.append('orange')
                elif estado == 'Terminado Exitosamente':
                    node_colors.append('yellow')
                else:
                    node_colors.append('lightblue')
            else:
                node_colors.append('lightgreen')
        
        edge_colors = []
        edge_styles = []
        for u, v, data in self.G.edges(data=True):
            if data['type'] == 'asignacion':
                edge_colors.append('green')
                edge_styles.append('solid')
            elif data['type'] == 'solicitud':
                edge_colors.append('red')
                edge_styles.append('dashed')
            
        nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, node_shape='s', node_size=1200, ax=self.ax)
        nx.draw_networkx_labels(self.G, pos, ax=self.ax)
        nx.draw_networkx_edges(self.G, pos, edge_color=edge_colors, style=edge_styles, ax=self.ax, arrowsize=20, width=2)
        
        self.ax.set_title(f"Grafo de Asignación y Solicitud ({len(self.procesos_terminados_exitosamente)}/{NUM_PROCESOS} Completados)", y=0.95) 
        self.ax.axis('off') 
        self.canvas.draw()
        
        text_info = f"--- ESTADO DE PROCESOS ---\n"
        for p in self.procesos:
            info = f"[{p.estado}] {p.id}"
            if p.asignados:
                info += f" (Posee: {', '.join(p.asignados)})"
            if p.solicitando:
                info += f" (Pide: {p.solicitando})"
            text_info += info + "\n"
            
        self.graph_info_label.config(text=text_info, justify=tk.LEFT)

    def setup_gui(self):
        self.root.title("Simulador de Interbloqueos (Deadlock)")
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)

        graph_frame = ttk.LabelFrame(main_frame, text="Grafo de Asignación y Solicitud", padding="5")
        graph_frame.pack(side="left", fill="both", expand=True)
        graph_frame.grid_columnconfigure(0, weight=1)
        graph_frame.grid_rowconfigure(0, weight=1)
        
        self.G = nx.DiGraph()
        self.fig, self.ax = plt.subplots(figsize=(6, 8)) 
        self.fig.tight_layout() 
        
        self.ax.set_title("Grafo de Asignación de Recursos")
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew") 

        self.graph_info_label = tk.Label(graph_frame, text="Información del Grafo", justify=tk.LEFT, anchor="nw", bg='white', font=('Consolas', 10))
        self.graph_info_label.grid(row=1, column=0, sticky="ew", pady=5) 
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="y", padx=10)

        # --- NUEVO: Panel de Indicadores de Deadlock ---
        deadlock_conditions_frame = ttk.LabelFrame(right_panel, text="Condiciones de Deadlock", padding="5")
        deadlock_conditions_frame.pack(fill="x", pady=5)

        condiciones = ["Exclusión Mutua", "Retención y Espera", "No Preemptividad", "Espera Circular"]
        self.leds = []
        
        for i, cond in enumerate(condiciones):
            ttk.Label(deadlock_conditions_frame, text=f"{cond}:", anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Etiqueta LED (círculo)
            led = tk.Label(deadlock_conditions_frame, text="●", font=('Arial', 16), fg='black', bg='red', width=2)
            led.grid(row=i, column=1, sticky="e", padx=5, pady=2)
            self.leds.append(led)

        # Asignar a variables de instancia para poder actualizarlos
        self.led_em, self.led_re, self.led_np, self.led_ec = self.leds
        # --- FIN: Panel de Indicadores de Deadlock ---

        log_frame = ttk.LabelFrame(right_panel, text="Registro de Eventos (Log)", padding="5")
        log_frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=60, height=25, wrap=tk.WORD) # Altura reducida
        self.log_text.pack(fill="y", expand=True)
        
        self.actualizar_indicadores_deadlock() # Estado inicial

    def calcular_metricas(self):
        tiempo_perdido = sum(p.tiempo_espera_total for p in self.procesos)
        tiempo_simulado = time.time() - self.tiempo_simulacion_inicio
        
        metricas = {
            "Total de Solicitudes": self.solicitudes_totales,
            "% de Solicitudes Satisfechas sin Bloqueos": (self.solicitudes_satisfechas / self.solicitudes_totales) * 100 if self.solicitudes_totales else 0,
            "% de Bloqueos Temporales": (self.bloqueos_temporales / self.solicitudes_totales) * 100 if self.solicitudes_totales else 0,
            "% de Interbloqueos Detectados": (self.interbloqueos_detectados / max(1, self.solicitudes_totales)) * 100,
            "Procesos Víctimas (reiniciados)": self.procesos_victimas,
            "Procesos Terminados Exitosamente": len(self.procesos_terminados_exitosamente),
            "Tiempo Perdido Total (s)": tiempo_perdido,
            "Tiempo Promedio de Espera por Proceso (s)": tiempo_perdido / NUM_PROCESOS if NUM_PROCESOS else 0
        }
        
        # Escribir las métricas en el archivo METRICS_FILENAME
        with open(METRICS_FILENAME, "w", encoding="utf-8") as f:
            f.write("--- MÉTRICAS DE LA SIMULACIÓN ---\n")
            for key, value in metricas.items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.2f}\n")
                else:
                    f.write(f"{key}: {value}\n")

        # 1. Registrar los eventos de finalización en el log
        self.log_event(f"Métricas generadas en {METRICS_FILENAME}")
        self.log_event(f"Simulación Finalizada. Tiempo total: {tiempo_simulado:.2f} segundos.")
        
        if self.log_file:
            self.log_file.close()
            self.log_file = None 
            
    # --- 6. CICLO DE EJECUCIÓN ---

    def get_next_proceso(self):
        for i in range(NUM_PROCESOS):
            idx = (self.indice_proceso_actual + i) % NUM_PROCESOS
            if self.procesos[idx].estado != "Terminado Exitosamente":
                return self.procesos[idx]
        return None

    def ciclo_simulacion(self):
        
        if len(self.procesos_terminados_exitosamente) == NUM_PROCESOS:
            self.log_event("✅ OBJETIVO CUMPLIDO: Todos los procesos han terminado exitosamente.")
            self.calcular_metricas()
            return

        proceso_actual = self.get_next_proceso()
        
        if not proceso_actual:
            self.calcular_metricas()
            return

        r1, r2 = self.patron_interbloqueo[proceso_actual.id]
        
        # 1. Ejecución Exitosa (Si ya tiene ambos)
        if r1 in proceso_actual.asignados and r2 in proceso_actual.asignados:
            if random.random() < 0.60: 
                self.log_event(f"🌟 TERMINACIÓN: {proceso_actual.id} completó su tarea con {r1} y {r2}.")
                self.liberar_recursos(proceso_actual)
                proceso_actual.estado = "Terminado Exitosamente"
                self.procesos_terminados_exitosamente.add(proceso_actual.id)
                
                self.dibujar_grafo()
                self.actualizar_indicadores_deadlock()
                current_pid_num = int(proceso_actual.id.split('P')[1])
                self.indice_proceso_actual = (current_pid_num + 1) % NUM_PROCESOS
                
                self.after_id = self.root.after(500, self.ciclo_simulacion) 
                return
            
        # 2. Lógica de Solicitud 
        
        if proceso_actual.estado != "Bloqueado":
            if r1 == r2:
                if not r1 in proceso_actual.asignados:
                     self.solicitar_recurso(proceso_actual, r1)
            
            # Lógica del interbloqueo (P0-P1, P2-P6, P4-P8)
            else:
                if not r1 in proceso_actual.asignados:
                    self.solicitar_recurso(proceso_actual, r1)
                
                elif r1 in proceso_actual.asignados and not r2 in proceso_actual.asignados:
                    self.solicitar_recurso(proceso_actual, r2)
        
        # 3. Detección y Resolución
        if self.detectar_interbloqueo():
            self.notificar_y_resolver()
            return 
        
        # 4. Avanzar el índice y Continuar
        current_pid_num = int(proceso_actual.id.split('P')[1])
        self.indice_proceso_actual = (current_pid_num + 1) % NUM_PROCESOS
        
        self.dibujar_grafo()
        self.actualizar_indicadores_deadlock() # Actualiza después de la acción de solicitud/bloqueo
        self.after_id = self.root.after(500, self.ciclo_simulacion) 
        
# --- MAIN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorDeadlock(root)
    
    def cerrar_simulador():
        app.calcular_metricas() 
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", cerrar_simulador)
    root.mainloop()