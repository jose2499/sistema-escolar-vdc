import tkinter as tk
from tkinter import messagebox


class DashboardView:

    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title(f"Sistema Escolar VDC - Panel Principal ({self.usuario.rol.value.upper()})")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self._crear_interfaz()

    def _crear_interfaz(self):
        # Header
        frame_header = tk.Frame(self.root, bg="#2B579A")
        frame_header.pack(fill="x")

        lbl_bienvenida = tk.Label(
            frame_header,
            text=f"Bienvenido(a), {self.usuario.nombre_completo}",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#2B579A",
        )
        lbl_bienvenida.pack(side="left", padx=15, pady=12)

        btn_salir = tk.Button(
            frame_header,
            text="Cerrar Sesión",
            bg="#D9534F",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            command=self._cerrar_sesion,
        )
        btn_salir.pack(side="right", padx=15, pady=12)

        # Contenido por Rol
        frame_contenido = tk.Frame(self.root, padx=20, pady=20)
        frame_contenido.pack(fill="both", expand=True)

        rol = self.usuario.rol.value
        if rol == "docente":
            self._construir_panel_docente(frame_contenido)
        elif rol == "administrador":
            self._construir_panel_admin(frame_contenido)
        else:
            self._construir_panel_apoderado(frame_contenido)

    def _construir_panel_docente(self, parent):
        lbl_titulo = tk.Label(
            parent,
            text="Módulo Docente - Gestión Académica",
            font=("Arial", 12, "bold"),
            fg="#2B579A",
        )
        lbl_titulo.pack(anchor="w", pady=(0, 15))

        grid_frame = tk.Frame(parent)
        grid_frame.pack(fill="x")

        # Botones con diseño estilo Card
        btn_calificaciones = tk.Button(
            grid_frame,
            text="📝 Registrar Calificaciones",
            font=("Arial", 10, "bold"),
            bg="#F8F9FA",
            fg="#2B579A",
            relief="groove",
            width=25,
            height=3,
            cursor="hand2",
            command=lambda: messagebox.showinfo("Módulo", "Función: Registrar Calificaciones"),
        )
        btn_calificaciones.grid(row=0, column=0, padx=10, pady=10)

        btn_alumnos = tk.Button(
            grid_frame,
            text="👥 Lista de Alumnos",
            font=("Arial", 10, "bold"),
            bg="#F8F9FA",
            fg="#2B579A",
            relief="groove",
            width=25,
            height=3,
            cursor="hand2",
            command=lambda: messagebox.showinfo("Módulo", "Función: Ver Lista de Alumnos"),
        )
        btn_alumnos.grid(row=0, column=1, padx=10, pady=10)

        btn_asistencia = tk.Button(
            grid_frame,
            text="📅 Control de Asistencia",
            font=("Arial", 10, "bold"),
            bg="#F8F9FA",
            fg="#2B579A",
            relief="groove",
            width=25,
            height=3,
            cursor="hand2",
            command=lambda: messagebox.showinfo("Módulo", "Función: Control de Asistencia"),
        )
        btn_asistencia.grid(row=1, column=0, padx=10, pady=10)

    def _construir_panel_admin(self, parent):
        tk.Label(parent, text="Panel de Administración General", font=("Arial", 12, "bold")).pack()

    def _construir_panel_apoderado(self, parent):
        tk.Label(parent, text="Portal de Apoderados y Consultas", font=("Arial", 12, "bold")).pack()

    def _cerrar_sesion(self):
        if messagebox.askyesno("Confirmar", "¿Desea cerrar sesión?"):
            self.root.destroy()
            from escolar.presentation.app import main
            main()

