import tkinter as tk
from tkinter import ttk, messagebox
import random

# ============================================
#  MODELO: Algoritmo del Banquero (Evitación)
# ============================================

class ModeloBanquero:
    """
    Implementación del Algoritmo del Banquero para EVITACIÓN de interbloqueos.

    - asignacion[i][j]: recursos del tipo j asignados al proceso i
    - demanda_maxima[i][j]: demanda máxima del proceso i
    - disponibles[j]: recursos libres del tipo j en el sistema
    """
    def __init__(self, asignacion, demanda_maxima, disponibles,
                 nombres_procesos=None, nombres_recursos=None):

        # Copias de trabajo
        self.asignacion = [fila[:] for fila in asignacion]
        self.demanda_maxima = [fila[:] for fila in demanda_maxima]
        self.disponibles = disponibles[:]

        # Cantidades
        self.num_procesos = len(asignacion)
        self.num_recursos = len(disponibles)

        # Nombres que se muestran en la interfaz
        self.nombres_procesos = (
            nombres_procesos or [f"P{i}" for i in range(self.num_procesos)]
        )
        self.nombres_recursos = (
            nombres_recursos or [chr(ord("A") + i) for i in range(self.num_recursos)]
        )

        # Calculamos la matriz de necesidad: NECESIDAD = DEMANDA_MAX - ASIGNACIÓN
        self._calcular_necesidad()

    def _calcular_necesidad(self):
        """Calcula la matriz NECESIDAD = DEMANDA_MAX - ASIGNACIÓN."""
        self.necesidad = []
        for i in range(self.num_procesos):
            fila = []
            for j in range(self.num_recursos):
                faltante = self.demanda_maxima[i][j] - self.asignacion[i][j]
                fila.append(faltante)
            self.necesidad.append(fila)

    def es_estado_seguro(self):
        """
        Verifica si el estado actual del sistema es SEGURO.

        Devuelve:
            (True, secuencia_segura)  -> si existe una secuencia donde
                                         todos los procesos pueden terminar.
            (False, secuencia_parcial) -> secuencia de los que sí pudieron
                                          terminar antes de quedar bloqueados.
        """
        trabajo = self.disponibles[:]          # work
        terminado = [False] * self.num_procesos  # finish
        secuencia_segura = []

        while len(secuencia_segura) < self.num_procesos:
            encontrado = False

            for i in range(self.num_procesos):
                if not terminado[i]:
                    # ¿Este proceso puede continuar con los recursos actuales?
                    if all(self.necesidad[i][j] <= trabajo[j]
                           for j in range(self.num_recursos)):
                        # Se “ejecuta” el proceso y libera sus recursos
                        for j in range(self.num_recursos):
                            trabajo[j] += self.asignacion[i][j]
                        terminado[i] = True
                        secuencia_segura.append(i)
                        encontrado = True

            if not encontrado:
                break

        es_seguro = len(secuencia_segura) == self.num_procesos
        return es_seguro, secuencia_segura

    def solicitar_recursos(self, id_proceso, solicitud):
        """
        Intenta conceder una solicitud de recursos de un proceso.

        Parámetros:
            - id_proceso: índice del proceso que solicita (0, 1, 2, ...)
            - solicitud: lista con los recursos que pide [r0, r1, r2, ...]

        Devuelve:
            - (True, secuencia_segura)  si la asignación es segura
            - (False, mensaje_error)    si NO se puede conceder
        """
        if len(solicitud) != self.num_recursos:
            return False, "Solicitud inválida: cantidad de tipos de recurso incorrecta."

        # 1) La solicitud no puede exceder lo que le falta (NECESIDAD)
        if any(solicitud[j] > self.necesidad[id_proceso][j]
               for j in range(self.num_recursos)):
            return False, "La solicitud excede la NECESIDAD restante del proceso."

        # 2) La solicitud no puede exceder los recursos disponibles
        if any(solicitud[j] > self.disponibles[j]
               for j in range(self.num_recursos)):
            return False, "No hay suficientes recursos DISPONIBLES para la solicitud."

        # Guardamos copias por si tenemos que hacer rollback
        copia_disponibles = self.disponibles[:]
        copia_asignacion = [fila[:] for fila in self.asignacion]
        copia_necesidad = [fila[:] for fila in self.necesidad]

        # Asignación TENTATIVA
        for j in range(self.num_recursos):
            self.disponibles[j] -= solicitud[j]
            self.asignacion[id_proceso][j] += solicitud[j]
            self.necesidad[id_proceso][j] -= solicitud[j]

        # Comprobamos si con esta asignación el estado sigue siendo seguro
        es_seguro, secuencia = self.es_estado_seguro()

        if es_seguro:
            # Dejamos los cambios, devolvemos la secuencia segura
            return True, secuencia
        else:
            # Hacemos rollback (deshacemos la asignación tentativa)
            self.disponibles = copia_disponibles
            self.asignacion = copia_asignacion
            self.necesidad = copia_necesidad
            return False, (
                "La asignación dejaría al sistema en un estado INSEGURO.\n"
                "Esto significa que podría aparecer un interbloqueo,\n"
                "por lo que el sistema RECHAZA esta solicitud."
            )

    def reiniciar(self, asignacion, demanda_maxima, disponibles):
        """Reinicia el modelo con nuevos datos de matrices y recursos."""
        self.__init__(asignacion, demanda_maxima, disponibles,
                      self.nombres_procesos, self.nombres_recursos)


# ============================================
#  VISTA / CONTROLADOR: Interfaz Tkinter
# ============================================

class AplicacionEvitacionInterbloqueos(tk.Tk):
    """
    Simulador gráfico de EVITACIÓN de interbloqueos con el Algoritmo del Banquero.
    """
    def __init__(self):
        super().__init__()

        self.title("🛡️ Simulador de Evitación de Interbloqueos — Algoritmo del Banquero")
        self.geometry("1150x700")
        self.minsize(1000, 650)
        self.configure(bg="#020617")  # fondo oscuro

        # Cantidad de procesos y recursos
        self.num_procesos = 5
        self.num_recursos = 3
        nombres_procesos = [f"P{i}" for i in range(self.num_procesos)]
        nombres_recursos = ["A", "B", "C"]

        # Generamos una instancia ALEATORIA garantizando que sea segura
        asignacion, demanda_maxima, disponibles = self._generar_instancia_aleatoria(
            self.num_procesos, self.num_recursos
        )

        self.modelo = ModeloBanquero(asignacion, demanda_maxima, disponibles,
                                     nombres_procesos, nombres_recursos)

        # Elementos de dibujo
        self.rectangulos_filas = {"asignacion": [], "max": [], "necesidad": []}
        self.id_texto_secuencia_segura = None

        # Listas de ejemplos
        self.lista_ejemplos_ok = None
        self.lista_ejemplos_bad = None

        self._construir_interfaz()
        self._dibujar_tablas()
        self._animar_introduccion()

    # --------- GENERADOR ALEATORIO ---------
    def _generar_instancia_aleatoria(self, num_procesos, num_recursos):
        """
        Genera aleatoriamente:
        - disponibles (recursos libres)
        - asignacion
        - demanda_maxima

        De forma que exista al menos una secuencia segura P0 → P1 → ... → Pn.
        """
        # Recursos iniciales disponibles (entre 1 y 5 por tipo)
        disponibles_base = [random.randint(1, 5) for _ in range(num_recursos)]
        trabajo = disponibles_base[:]  # usado para garantizar necesidad <= trabajo

        asignacion = []
        demanda_maxima = []

        for _ in range(num_procesos):
            # Necesidad inicial: siempre ≤ trabajo para asegurar seguridad
            necesidad_i = [random.randint(0, trabajo[j]) for j in range(num_recursos)]
            # Asignación: valores pequeños para que se entienda visualmente
            asignacion_i = [random.randint(0, 3) for _ in range(num_recursos)]
            demanda_max_i = [necesidad_i[j] + asignacion_i[j] for j in range(num_recursos)]

            asignacion.append(asignacion_i)
            demanda_maxima.append(demanda_max_i)

            # Simulamos que el proceso se ejecuta y libera recursos
            for j in range(num_recursos):
                trabajo[j] += asignacion_i[j]

        return asignacion, demanda_maxima, disponibles_base

    # ----------------------------------------
    # Construcción de la interfaz
    # ----------------------------------------
    def _construir_interfaz(self):
        # HUD superior
        contenedor_superior = tk.Frame(self, bg="#020617", pady=10)
        contenedor_superior.pack(fill="x", side="top")

        self.etiqueta_titulo = tk.Label(
            contenedor_superior,
            text="Simulador de Evitación de Interbloqueos",
            font=("Segoe UI", 20, "bold"),
            fg="#e5e7eb",
            bg="#020617"
        )
        self.etiqueta_titulo.pack(side="left", padx=20)

        self.etiqueta_estado = tk.Label(
            contenedor_superior,
            text="Estado: Desconocido",
            font=("Segoe UI", 11, "bold"),
            fg="#111827",
            bg="#fbbf24",
            padx=10,
            pady=4
        )
        self.etiqueta_estado.pack(side="right", padx=20)

        # Contenedor principal
        contenedor_principal = tk.Frame(self, bg="#020617")
        contenedor_principal.pack(fill="both", expand=True, padx=16, pady=10)

        panel_izquierdo = tk.Frame(contenedor_principal, bg="#020617")
        panel_izquierdo.pack(side="left", fill="y", padx=(0, 12))

        panel_derecho = tk.Frame(contenedor_principal, bg="#020617")
        panel_derecho.pack(side="right", fill="both", expand=True)

        # ---------- Panel de controles ----------
        tarjeta_controles = tk.Frame(panel_izquierdo, bg="#020617", highlightthickness=0)
        tarjeta_controles.pack(fill="x", pady=6)

        borde_controles = tk.Frame(tarjeta_controles, bg="#1f2937")
        borde_controles.pack(fill="both", expand=True)

        interior_controles = tk.Frame(borde_controles, bg="#0b1120", padx=12, pady=12)
        interior_controles.pack(fill="both", expand=True, padx=1, pady=1)

        titulo_controles = tk.Label(
            interior_controles,
            text="🎮 Controles de simulación",
            font=("Segoe UI", 12, "bold"),
            fg="#e5e7eb",
            bg="#0b1120",
        )
        titulo_controles.pack(anchor="w", pady=(0, 8))

        # Selección de proceso
        fila_proceso = tk.Frame(interior_controles, bg="#0b1120")
        fila_proceso.pack(fill="x", pady=(0, 6))

        tk.Label(
            fila_proceso, text="Proceso (P):", font=("Segoe UI", 10),
            fg="#e5e7eb", bg="#0b1120"
        ).pack(side="left")

        self.valor_proceso = tk.StringVar(value=self.modelo.nombres_procesos[0])
        lista_procesos = ttk.Combobox(
            fila_proceso, textvariable=self.valor_proceso,
            values=self.modelo.nombres_procesos, state="readonly", width=5
        )
        lista_procesos.pack(side="left", padx=(6, 0))

        # Solicitud de recursos
        tk.Label(
            interior_controles,
            text="Solicitud de recursos (vector que pide el proceso):",
            font=("Segoe UI", 10),
            fg="#9ca3af",
            bg="#0b1120"
        ).pack(anchor="w", pady=(4, 2))

        self.entradas_solicitud = []
        fila_solicitud = tk.Frame(interior_controles, bg="#0b1120")
        fila_solicitud.pack(anchor="w")

        for nombre_recurso in self.modelo.nombres_recursos:
            cont = tk.Frame(fila_solicitud, bg="#0b1120")
            cont.pack(side="left", padx=(0, 8))
            tk.Label(
                cont, text=f"{nombre_recurso}:", font=("Segoe UI", 10),
                fg="#e5e7eb", bg="#0b1120"
            ).pack(anchor="w")
            entrada = tk.Entry(
                cont, width=4, justify="center",
                bg="#020617", fg="#e5e7eb",
                insertbackground="#e5e7eb",
                relief="flat"
            )
            entrada.pack(anchor="w")
            entrada.insert(0, "0")
            self.entradas_solicitud.append(entrada)

        # Botones de acciones
        marco_botones = tk.Frame(interior_controles, bg="#0b1120")
        marco_botones.pack(fill="x", pady=(10, 0))

        tk.Button(
            marco_botones, text="1) Simular solicitud",
            command=self._evento_simular_solicitud,
            font=("Segoe UI", 10, "bold"),
            fg="#e5e7eb", bg="#22c55e",
            activebackground="#16a34a",
            activeforeground="#e5e7eb",
            relief="flat", padx=10, pady=4,
            cursor="hand2"
        ).pack(fill="x")

        tk.Button(
            interior_controles, text="2) Comprobar estado seguro",
            command=self._evento_comprobar_seguridad,
            font=("Segoe UI", 9, "bold"),
            fg="#e5e7eb", bg="#3b82f6",
            activebackground="#1d4ed8",
            activeforeground="#e5e7eb",
            relief="flat", padx=8, pady=3,
            cursor="hand2"
        ).pack(fill="x", pady=(8, 0))

        tk.Button(
            interior_controles, text="Reiniciar ejemplo (nuevo aleatorio)",
            command=self._evento_reiniciar_ejemplo,
            font=("Segoe UI", 9),
            fg="#e5e7eb", bg="#374151",
            activebackground="#111827",
            activeforeground="#e5e7eb",
            relief="flat", padx=8, pady=3,
            cursor="hand2"
        ).pack(fill="x", pady=(6, 0))

        # Cómo usar
        marco_pasos = tk.LabelFrame(
            interior_controles,
            text=" ¿Cómo usar el simulador? ",
            fg="#e5e7eb", bg="#0b1120"
        )
        marco_pasos.config(font=("Segoe UI", 9, "bold"))
        marco_pasos.pack(fill="x", pady=(10, 0))

        tk.Label(
            marco_pasos,
            text=(
                "1. Elige un PROCESO (P0–P4).\n"
                "2. Escribe cuántos recursos A, B y C está pidiendo.\n"
                "3. Pulsa «Simular solicitud».\n"
                "   → El sistema decide si es seguro CONCEDER o NO.\n"
                "4. «Reiniciar ejemplo» genera NUEVOS datos aleatorios.\n"
            ),
            justify="left",
            fg="#d1d5db",
            bg="#0b1120",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=4, pady=4)

        # ======= Panel de ejemplos automáticos =======
        marco_ejemplos = tk.LabelFrame(
            interior_controles,
            text=" Ejemplos automáticos ",
            fg="#e5e7eb", bg="#0b1120"
        )
        marco_ejemplos.config(font=("Segoe UI", 9, "bold"))
        marco_ejemplos.pack(fill="both", expand=True, pady=(10, 0))

        tk.Label(
            marco_ejemplos,
            text=(
                "Prueba varias solicitudes sobre el ESTADO ACTUAL y las\n"
                "separa en CONCEDIDAS (seguras) y RECHAZADAS (inseguras)."
            ),
            justify="left",
            fg="#d1d5db",
            bg="#0b1120",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=4, pady=(4, 2))

        tk.Button(
            marco_ejemplos, text="Generar ejemplos",
            command=self._evento_generar_ejemplos,
            font=("Segoe UI", 9, "bold"),
            fg="#e5e7eb", bg="#6d28d9",
            activebackground="#5b21b6",
            activeforeground="#e5e7eb",
            relief="flat", padx=6, pady=3,
            cursor="hand2"
        ).pack(fill="x", padx=4, pady=(0, 4))

        columnas_ejemplos = tk.Frame(marco_ejemplos, bg="#0b1120")
        columnas_ejemplos.pack(fill="both", expand=True, padx=2, pady=(2, 4))

        col_izq = tk.Frame(columnas_ejemplos, bg="#0b1120")
        col_izq.pack(side="left", fill="both", expand=True, padx=(0, 3))

        col_der = tk.Frame(columnas_ejemplos, bg="#0b1120")
        col_der.pack(side="left", fill="both", expand=True, padx=(3, 0))

        tk.Label(
            col_izq, text="✅ Se CONCEDEN:",
            fg="#22c55e", bg="#0b1120",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        self.lista_ejemplos_ok = tk.Listbox(
            col_izq, height=6,
            bg="#020617", fg="#e5e7eb",
            font=("Consolas", 8),
            highlightthickness=0, selectbackground="#15803d"
        )
        self.lista_ejemplos_ok.pack(fill="both", expand=True, pady=(2, 0))

        tk.Label(
            col_der, text="❌ Se RECHAZAN:",
            fg="#f97316", bg="#0b1120",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        self.lista_ejemplos_bad = tk.Listbox(
            col_der, height=6,
            bg="#020617", fg="#e5e7eb",
            font=("Consolas", 8),
            highlightthickness=0, selectbackground="#b91c1c"
        )
        self.lista_ejemplos_bad.pack(fill="both", expand=True, pady=(2, 0))

        # ======= FIN ejemplos =======

        # Canvas central para las tablas
        tarjeta_canvas = tk.Frame(panel_derecho, bg="#020617")
        tarjeta_canvas.pack(fill="both", expand=True)

        borde_canvas = tk.Frame(tarjeta_canvas, bg="#1f2937")
        borde_canvas.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            borde_canvas, bg="#020617",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)

        # Log de eventos
        tarjeta_log = tk.Frame(panel_derecho, bg="#020617")
        tarjeta_log.pack(fill="x", pady=(8, 0))

        borde_log = tk.Frame(tarjeta_log, bg="#1f2937")
        borde_log.pack(fill="both", expand=True)

        interior_log = tk.Frame(borde_log, bg="#020617", padx=8, pady=4)
        interior_log.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(
            interior_log,
            text="📜 Log de eventos (lo que va pasando paso a paso)",
            font=("Segoe UI", 10, "bold"),
            fg="#e5e7eb", bg="#020617"
        ).pack(anchor="w")

        self.texto_log = tk.Text(
            interior_log, height=6, bg="#020617",
            fg="#d1d5db", insertbackground="#e5e7eb",
            font=("Consolas", 9),
            relief="flat"
        )
        self.texto_log.pack(fill="both", expand=True, pady=(2, 0))
        self._agregar_log("Simulador iniciado con datos aleatorios. Usa los pasos del panel izquierdo.")

        self.canvas.bind("<Configure>", lambda e: self._dibujar_tablas())

    # ----------------------------------------
    # Dibujo de tablas
    # ----------------------------------------
    def _dibujar_tablas(self):
        self.canvas.delete("all")
        self.rectangulos_filas = {"asignacion": [], "max": [], "necesidad": []}
        self.id_texto_secuencia_segura = None

        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()

        if ancho < 100 or alto < 100:
            return

        margen = 20
        ancho_columna = (ancho - 2 * margen) / 4
        x_inicial = margen

        self._dibujar_seccion_disponibles(x_inicial, margen, ancho_columna, alto - 80)
        x_inicial += ancho_columna
        self._dibujar_seccion_matriz(
            "Asignación actual", "asignacion",
            "Lo que YA tiene cada proceso.",
            x_inicial, margen, ancho_columna, alto - 80
        )
        x_inicial += ancho_columna
        self._dibujar_seccion_matriz(
            "Demanda máxima", "max",
            "Lo máximo que PODRÍA pedir cada proceso.",
            x_inicial, margen, ancho_columna, alto - 80
        )
        x_inicial += ancho_columna
        self._dibujar_seccion_matriz(
            "Necesidad restante", "necesidad",
            "Lo que LE FALTA a cada proceso para terminar.",
            x_inicial, margen, ancho_columna, alto - 80
        )

        es_seguro, secuencia = self.modelo.es_estado_seguro()
        if es_seguro:
            self._actualizar_estado_hud("SEGURO", "#22c55e")
            texto = f"Secuencia segura posible: {self._secuencia_a_cadena(secuencia)}"
            self.id_texto_secuencia_segura = self.canvas.create_text(
                ancho / 2, alto - 30,
                text=texto,
                font=("Segoe UI", 11, "bold"),
                fill="#4ade80"
            )
            self._agregar_log(f"Estado actual SEGURO. {texto}")
        else:
            self._actualizar_estado_hud("INSEGURO", "#ef4444")
            self.id_texto_secuencia_segura = self.canvas.create_text(
                ancho / 2, alto - 30,
                text="Estado INSEGURO: no existe una secuencia que ejecute a todos los procesos.",
                font=("Segoe UI", 11, "bold"),
                fill="#f87171"
            )
            self._agregar_log("Estado actual INSEGURO: no existe una secuencia segura.")

    def _dibujar_seccion_disponibles(self, x, y, ancho, alto):
        titulo = "Disponibles"
        self._dibujar_titulo_panel(x, y, ancho, 30, titulo, "#38bdf8")

        y_caja = y + 40

        self.canvas.create_text(
            x + ancho / 2, y_caja,
            text="Recursos libres que el sistema puede entregar:",
            font=("Segoe UI", 10, "bold"),
            fill="#e5e7eb"
        )

        y_valores = y_caja + 24
        espacio = ancho / (len(self.modelo.nombres_recursos) + 1)
        for j, nombre_recurso in enumerate(self.modelo.nombres_recursos):
            cx = x + espacio * (j + 1)
            self.canvas.create_text(
                cx, y_valores,
                text=f"{nombre_recurso}: {self.modelo.disponibles[j]}",
                font=("Segoe UI", 10, "bold"),
                fill="#a5b4fc"
            )

        self.canvas.create_text(
            x + ancho / 2, y_valores + 40,
            text="Si un proceso pide más que esto,\n"
                 "la solicitud se RECHAZA inmediatamente.",
            font=("Segoe UI", 9),
            fill="#9ca3af"
        )

    def _dibujar_titulo_panel(self, x, y, ancho, alto, texto, color_resaltado="#3b82f6"):
        self.canvas.create_rectangle(
            x, y + 5, x + 4, y + alto - 5,
            fill=color_resaltado, outline=""
        )
        self.canvas.create_text(
            x + ancho / 2, y + alto / 2,
            text=texto,
            font=("Segoe UI", 11, "bold"),
            fill="#e5e7eb"
        )

    def _dibujar_seccion_matriz(self, titulo, clave, subtitulo, x, y, ancho, alto):
        mapa_colores = {
            "asignacion": "#22c55e",
            "max": "#f97316",
            "necesidad": "#eab308",
        }
        color = mapa_colores.get(clave, "#3b82f6")
        self._dibujar_titulo_panel(x, y, ancho, 30, titulo, color)

        parte_superior = y + 40
        izquierda = x + 10
        alto_fila = 28
        ancho_columna = (ancho - 20) / (self.modelo.num_recursos + 1)

        self.canvas.create_text(
            x + ancho / 2, parte_superior,
            text=subtitulo,
            font=("Segoe UI", 9),
            fill="#9ca3af"
        )
        parte_superior += 18

        self.canvas.create_text(
            izquierda + ancho_columna / 2, parte_superior,
            text="P",
            font=("Segoe UI", 10, "bold"),
            fill="#9ca3af"
        )
        for j, nombre_recurso in enumerate(self.modelo.nombres_recursos):
            self.canvas.create_text(
                izquierda + ancho_columna * (j + 1) + ancho_columna / 2,
                parte_superior,
                text=nombre_recurso,
                font=("Segoe UI", 10, "bold"),
                fill="#9ca3af"
            )

        if clave == "asignacion":
            matriz = self.modelo.asignacion
        elif clave == "max":
            matriz = self.modelo.demanda_maxima
        else:
            matriz = self.modelo.necesidad

        lista_rectangulos = []
        for i, nombre_proceso in enumerate(self.modelo.nombres_procesos):
            y_fila = parte_superior + (i + 1) * alto_fila

            self.canvas.create_text(
                izquierda + ancho_columna / 2, y_fila,
                text=nombre_proceso,
                font=("Segoe UI", 10),
                fill="#e5e7eb"
            )

            rectangulos_proceso = []
            for j in range(self.modelo.num_recursos):
                cx = izquierda + ancho_columna * (j + 1) + ancho_columna / 2
                x0 = cx - ancho_columna / 2 + 3
                y0 = y_fila - alto_fila / 2 + 3
                x1 = cx + ancho_columna / 2 - 3
                y1 = y_fila + alto_fila / 2 - 3

                rect = self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill="#020617", outline="#1f2937"
                )
                rectangulos_proceso.append(rect)
                self.canvas.create_text(
                    cx, y_fila,
                    text=str(matriz[i][j]),
                    font=("Segoe UI", 10),
                    fill="#e5e7eb"
                )
            lista_rectangulos.append(rectangulos_proceso)

        self.rectangulos_filas[clave] = lista_rectangulos

    # ----------------------------------------
    # Animaciones / HUD / Log
    # ----------------------------------------
    def _actualizar_estado_hud(self, texto_estado, color_fondo):
        self.etiqueta_estado.config(
            text=f"Estado: {texto_estado}",
            bg=color_fondo
        )

    def _agregar_log(self, mensaje):
        self.texto_log.insert("end", mensaje + "\n")
        self.texto_log.see("end")

    def _secuencia_a_cadena(self, secuencia):
        return " → ".join(self.modelo.nombres_procesos[i] for i in secuencia)

    def _animar_introduccion(self):
        colores = ["#38bdf8", "#e5e7eb", "#38bdf8"]
        def paso(i=0):
            self.etiqueta_titulo.config(fg=colores[i % 3])
            if i < 5:
                self.after(200, paso, i + 1)
            else:
                self.etiqueta_titulo.config(fg="#e5e7eb")
        paso()

    def _animar_secuencia_segura(self, secuencia):
        retardo = 450
        color_resaltado = "#047857"
        color_normal = "#020617"

        def resaltar_paso(k):
            # Restaurar colores
            for clave in ["asignacion", "max", "necesidad"]:
                for rects_fila in self.rectangulos_filas.get(clave, []):
                    for rect in rects_fila:
                        self.canvas.itemconfig(rect, fill=color_normal)

            if k < len(secuencia):
                id_proceso = secuencia[k]
                for clave in ["asignacion", "max", "necesidad"]:
                    matriz_rects = self.rectangulos_filas.get(clave, [])
                    if 0 <= id_proceso < len(matriz_rects):
                        for rect in matriz_rects[id_proceso]:
                            self.canvas.itemconfig(rect, fill=color_resaltado)
                self._agregar_log(
                    f"✔ Proceso {self.modelo.nombres_procesos[id_proceso]} puede ejecutarse y liberar recursos."
                )
                self.after(retardo, resaltar_paso, k + 1)
            else:
                # Limpieza final
                self.after(retardo, lambda: [
                    self.canvas.itemconfig(rect, fill=color_normal)
                    for clave in ["asignacion", "max", "necesidad"]
                    for rects_fila in self.rectangulos_filas.get(clave, [])
                    for rect in rects_fila
                ])
                self._agregar_log("Secuencia segura completada.")

        if secuencia:
            self._agregar_log("Animando la secuencia segura encontrada...")
            resaltar_paso(0)

    def _parpadear_estado(self, color1, color2, repeticiones=4):
        def paso(i=0):
            self.etiqueta_estado.config(bg=color1 if i % 2 == 0 else color2)
            if i < repeticiones:
                self.after(150, paso, i + 1)
        paso()

    # ----------------------------------------
    # Eventos de botones
    # ----------------------------------------
    def _evento_comprobar_seguridad(self):
        es_seguro, secuencia = self.modelo.es_estado_seguro()
        if es_seguro:
            self._actualizar_estado_hud("SEGURO", "#22c55e")
            self._parpadear_estado("#22c55e", "#16a34a")
            mensaje = (
                "El sistema está en ESTADO SEGURO.\n\n"
                "Existe un orden en el que todos los procesos\n"
                "pueden terminar sin quedar bloqueados.\n\n"
                f"Ejemplo de secuencia segura:\n{self._secuencia_a_cadena(secuencia)}"
            )
            messagebox.showinfo("Estado SEGURO", mensaje)
            self._agregar_log(mensaje.replace("\n", " "))
            self._dibujar_tablas()
            self._animar_secuencia_segura(secuencia)
        else:
            self._actualizar_estado_hud("INSEGURO", "#ef4444")
            self._parpadear_estado("#ef4444", "#b91c1c")
            mensaje = (
                "El sistema está en ESTADO INSEGURO.\n\n"
                "No se encuentra ninguna secuencia que permita que\n"
                "todos los procesos terminen. Podría aparecer un interbloqueo."
            )
            messagebox.showwarning("Estado INSEGURO", mensaje)
            self._agregar_log(mensaje.replace("\n", " "))
            self._dibujar_tablas()

    def _evento_simular_solicitud(self):
        nombre_proceso = self.valor_proceso.get()
        try:
            id_proceso = self.modelo.nombres_procesos.index(nombre_proceso)
        except ValueError:
            messagebox.showerror("Error", "Proceso seleccionado inválido.")
            return

        try:
            solicitud = [int(e.get()) for e in self.entradas_solicitud]
            if any(v < 0 for v in solicitud):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Solicitud inválida",
                "Todos los valores de la solicitud deben ser enteros mayores o iguales a 0."
            )
            return

        self._agregar_log(f"Solicitud recibida: {nombre_proceso} pide {solicitud}.")

        exito, resultado = self.modelo.solicitar_recursos(id_proceso, solicitud)
        if exito:
            secuencia = resultado
            self._actualizar_estado_hud("SEGURO", "#22c55e")
            self._parpadear_estado("#22c55e", "#16a34a")
            mensaje = (
                "La solicitud PUEDE ser CONCEDIDA sin volver inseguro el sistema.\n\n"
                "Después de asignar estos recursos, el Algoritmo del Banquero\n"
                "encontró una secuencia segura donde todos terminan.\n\n"
                f"Secuencia segura resultante:\n{self._secuencia_a_cadena(secuencia)}"
            )
            messagebox.showinfo("Solicitud concedida", mensaje)
            self._agregar_log(mensaje.replace("\n", " "))
            self._dibujar_tablas()
            self._animar_secuencia_segura(secuencia)
        else:
            mensaje_error = resultado
            self._actualizar_estado_hud("INSEGURO", "#ef4444")
            self._parpadear_estado("#ef4444", "#b91c1c")
            messagebox.showwarning("Solicitud rechazada", mensaje_error)
            self._agregar_log("Solicitud rechazada: " + mensaje_error)

    def _evento_reiniciar_ejemplo(self):
        asignacion, demanda_maxima, disponibles = self._generar_instancia_aleatoria(
            self.num_procesos, self.num_recursos
        )
        self.modelo.reiniciar(asignacion, demanda_maxima, disponibles)
        self._dibujar_tablas()
        self._agregar_log("Ejemplo reiniciado con nuevos datos ALEATORIOS.")

        for entrada in self.entradas_solicitud:
            entrada.delete(0, "end")
            entrada.insert(0, "0")

        if self.lista_ejemplos_ok is not None:
            self.lista_ejemplos_ok.delete(0, "end")
        if self.lista_ejemplos_bad is not None:
            self.lista_ejemplos_bad.delete(0, "end")

    # -------- Ejemplos automáticos --------
    def _evento_generar_ejemplos(self):
        if self.lista_ejemplos_ok is None or self.lista_ejemplos_bad is None:
            return

        self.lista_ejemplos_ok.delete(0, "end")
        self.lista_ejemplos_bad.delete(0, "end")

        ya_vistos = set()

        for id_proceso in range(self.modelo.num_procesos):
            fila_necesidad = self.modelo.necesidad[id_proceso]

            # Ejemplo 1: pedir exactamente lo que le falta (necesidad)
            if any(fila_necesidad):
                solicitud_1 = fila_necesidad[:]
                self._evaluar_ejemplo(id_proceso, solicitud_1, ya_vistos)

            # Ejemplo 2: pedir 1 unidad de cada recurso que todavía necesita
            solicitud_2 = [1 if n > 0 else 0 for n in fila_necesidad]
            if any(solicitud_2):
                self._evaluar_ejemplo(id_proceso, solicitud_2, ya_vistos)

            # Ejemplo 3: pasarme un poco de lo que necesita (seguro se rechaza por NECESIDAD)
            solicitud_3 = [n + 1 if n > 0 else 1 for n in fila_necesidad]
            self._evaluar_ejemplo(id_proceso, solicitud_3, ya_vistos)

        self._agregar_log("Ejemplos generados automáticamente para el estado actual.")

    def _evaluar_ejemplo(self, id_proceso, solicitud, ya_vistos):
        clave = (id_proceso, tuple(solicitud))
        if clave in ya_vistos:
            return
        ya_vistos.add(clave)

        # Modelo temporal (para no modificar el original)
        modelo_temporal = ModeloBanquero(
            [fila[:] for fila in self.modelo.asignacion],
            [fila[:] for fila in self.modelo.demanda_maxima],
            self.modelo.disponibles[:],
            self.modelo.nombres_procesos,
            self.modelo.nombres_recursos
        )

        exito, resultado = modelo_temporal.solicitar_recursos(id_proceso, solicitud)
        nombre_proceso = self.modelo.nombres_procesos[id_proceso]

        if exito:
            secuencia = resultado
            texto = (f"{nombre_proceso} pide {solicitud} → CONCEDIDA. "
                     f"Secuencia: {self._secuencia_a_cadena(secuencia)}")
            self.lista_ejemplos_ok.insert("end", texto)
        else:
            mensaje = resultado.split("\n")[0]
            if len(mensaje) > 70:
                mensaje = mensaje[:67] + "..."
            texto = f"{nombre_proceso} pide {solicitud} → RECHAZADA. {mensaje}"
            self.lista_ejemplos_bad.insert("end", texto)


# ============================================
#  EJECUCIÓN
# ============================================

if __name__ == "__main__":
    app = AplicacionEvitacionInterbloqueos()
    app.mainloop()
