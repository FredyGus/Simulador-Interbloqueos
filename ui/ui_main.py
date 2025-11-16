import subprocess
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox

class MainApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Simulador de interbloqueos")
        self.geometry("1100x650")
        self.resizable(False, False)

        # Marco principal con el sidebar a la izquierda
        self.columnconfigure(0, weight=0) # Sidebar
        self.columnconfigure(1, weight=1) # Contenido 
        self.rowconfigure(0, weight=1)

        # Crea el sidebar
        self.sidebar = ttk.Frame(self, padding=10)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.configure(bootstyle="dark")

        # Crea el panel de contenido principal
        self.content_frame = ttk.Frame(self, padding=20)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Etiqueta de titulo
        self.title_label = ttk.Label(
            self.content_frame, 
            text="Simulador de interbloqueos\nSistema Operativo", 
            font=("Segoe UI", 18, "bold"), 
            anchor="center"
        )
        self.title_label.pack(pady=50)

        self.desc_label = ttk.Label(
            self.content_frame,
            text=("Explora como se producen y manejan los interbloqueos\n"
                  "Mediante las politicas de Prevencion, Deteccion, Evitacion e Ignorar."
            ),
            font=("Segoe UI", 12),
            anchor="center",
            justify="center"
        )
        self.desc_label.pack(pady=20)

        # Crear botones del sidebar
        self.create_sidebar_buttons()
        self.active_button = None
        self.activate_button(self.show_menu, "Menu") # Boton por defecto


    def create_sidebar_buttons(self):
        self.buttons = {}

        buttons = [
            ("Menu", self.show_menu),
            ("Prevencion", lambda: self.show_policy("Prevencion")),
            ("Deteccion", lambda: self.show_policy("Deteccion")),
            ("Evitacion", lambda: self.show_policy("Evitacion")),
            ("Ignorar", lambda: self.show_policy("Ignorar")),
            ("Salir", self.exit_app),
        ]

        for text, command in buttons:
            b = ttk.Button(
                self.sidebar,
                text=text,
                command=lambda cmd=command, btn_text=text: self.activate_button(cmd, btn_text),
                bootstyle="secondary-outline, toolbutton",
                width=20,
            )
            b.pack(pady=5, fill="x")
            self.buttons[text] = b # Guardamos cada boton

    def activate_button(self, command, button_text):
        # Marca el boton activo y ejecuta el comando
        # Resetea todos los botones al estilo normal
        for name, button in self.buttons.items():
            button.configure(bootstyle="secondary-outline")
        
        # Activa el boton actual
        self.buttons[button_text].configure(bootstyle="success-outline")

        # Guardar referencia del boton activo
        self.active_button = button_text

        # Ejecuta el comando (Mostrar vista)
        command()
    
    def clear_content(self):
        # Limpia el area central antes de mostrar otra vista
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_menu(self):
        # Muestra la pantalla de introduccion
        self.clear_content()
        self.title_label = ttk.Label(
            self.content_frame,
            text="Simulador de interbloqueos\nSistema Operativo",
            font=("Segoe UI", 18, "bold"),
            anchor="center",
        )
        self.title_label.pack(pady=50)

        self.desc_label = ttk.Label(
            self.content_frame,
            text=("Un interbloqueo ocurre cuando dos o mas procesos esperan\n"
                  "recursos que nunca seran liberados, generando una espera circular."
            ),
            font=("Segoe UI", 12),
            anchor="center",
            justify="center"
        )
        self.desc_label.pack(pady=10)

    def show_policy(self, policy_name):
        # Muestra el contenido segun politica seleccionada
        self.clear_content()

        title = ttk.Label(
            self.content_frame,
            text=f"Politica: {policy_name}",
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(pady=20)

        desc = ttk.Label(
            self.content_frame,
            text="Haz click en el boton para iniciar la simulacion.",
            font=("Segoe UI", 12),
        )
        desc.pack(pady=10)

        if policy_name == "Deteccion":
            start_button = ttk.Button(
                self.content_frame,
                text="▶ Iniciar Simulacion de Deteccion",
                bootstyle="success",
                command=self.launch_deteccion_window,
            )
        elif policy_name == "Prevencion":
            start_button = ttk.Button(
                self.content_frame,
                text="▶ Iniciar Simulacion de Prevencion",
                bootstyle="success",
                command=self.launch_prevencion_window,
            )
        elif policy_name == "Evitacion":
            start_button = ttk.Button(
                self.content_frame,
                text="▶ Iniciar Simulacion de Evitacion",
                bootstyle="success",
                command=self.launch_evitacion_window,
            )
        else: 
            start_button = ttk.Button(
                self.content_frame,
                text="▶ Iniciar simulación",
                bootstyle="secondary",
                command=lambda: messagebox.showinfo(
                "Simulación",
                f"La simulación de '{policy_name}' aún no está implementada."
                ),
            )
        start_button.pack(pady=30)

    def launch_deteccion_window(self):
        # Abre el simulador de deteccion en una ventana independiente
        try:
            # Ruta del archivo 
            script_path = os.path.join(os.getcwd(), "simuladores", "simulador_deadlock.py")

            # Ejecutar en una nueva ventana del sistema
            subprocess.Popen(["python", script_path])

            self.activate_button(lambda: None, "Deteccion") # Mantener el boton activo

            messagebox.showinfo(
                "Simulador de Deteccion",
                "Se ha abierto el simulador de Deteccion en una ventana nueva.\n"
                "Puedes cerrarla cuando finalice la simulacion."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el simulador de Deteccion.\nError: {e}"
            )
            
    def launch_prevencion_window(self):
        # Abre el simulador de prevencion en una ventana independiente
        try:
            # Ruta del archivo 
            script_path = os.path.join(os.getcwd(), "simuladores", "simulador_prevencion.py")

            # Ejecutar en una nueva ventana del sistema
            subprocess.Popen(["python", script_path])

            self.activate_button(lambda: None, "Prevencion") # Mantener el boton activo

            messagebox.showinfo(
                "Simulador de Prevencion",
                "Se ha abierto el simulador de Prevencion en una ventana nueva.\n"
                "Puedes cerrarla cuando finalice la simulacion."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el simulador de Prevencion.\nError: {e}"
            )
    
    def launch_evitacion_window(self):
        # Abre el simulador de evitacion en una ventana independiente
        try:
            # Ruta del archivo
            script_path = os.path.join(os.getcwd(), "simuladores", "simulador_banquero.py")
            
            # Ejecutar en una nueva ventana del sistema
            subprocess.Popen(["python", script_path])
            
            self.activate_button(lambda: None, "Evitacion") # Mantener el boton activo
            messagebox.showinfo(
                "Simulador de Evitacion",
                "Se ha abierto el simulador de Evitacion en una ventana nueva.\n"
                "Puedes cerrarla cuando finalice la simulacion."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el simulador de Evitacion.\nError: {e}"
            )

    def exit_app(self):
        # Confirma antes de cerrar
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()