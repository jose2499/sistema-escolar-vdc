import tkinter as tk
from tkinter import messagebox


class DashboardView:

    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title(f"Sistema Escolar VDC - Panel Principal ({self.usuario.rol.value.upper()})")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self._crear_interfaz()

    def _crear_interfaz(self):
        frame_header = tk.Frame(self.root, bg="#2B579A")
        frame_header.pack(fill="x")

        lbl_bienvenida = tk.Label(
            frame_header,
            text=f"Bienvenido(a), {self.usuario.nombre_completo}",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#2B579A",
        )
        lbl_bienvenida.pack(side="left", padx=15, pady=10)

        btn_salir = tk.Button(
            frame_header,
            text="Cerrar Sesion",
            bg="#D9534F",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self._cerrar_sesion,
        )
        btn_salir.pack(side="right", padx=15, pady=10)

        lbl_rol = tk.Label(
            self.root,
            text=f"Rol asignado: {self.usuario.rol.value.capitalize()}",
            font=("Arial", 12, "italic"),
            fg="#333333",
        )
        lbl_rol.pack(pady=20)

        frame_acciones = tk.Frame(self.root)
        frame_acciones.pack(pady=10)

        rol = self.usuario.rol.value
        if rol == "administrador":
            tk.Button(frame_acciones, text="Gestionar Usuarios", width=25, height=2).pack(pady=5)
            tk.Button(frame_acciones, text="Configuracion del Sistema", width=25, height=2).pack(pady=5)
        elif rol == "docente":
            tk.Button(frame_acciones, text="Registrar Calificaciones", width=25, height=2).pack(pady=5)
            tk.Button(frame_acciones, text="Ver Lista de Alumnos", width=25, height=2).pack(pady=5)
        elif rol == "apoderado":
            tk.Button(frame_acciones, text="Ver Notas de Estudiante", width=25, height=2).pack(pady=5)
            tk.Button(frame_acciones, text="Consultar Asistencia", width=25, height=2).pack(pady=5)

    def _cerrar_sesion(self):
        if messagebox.askyesno("Confirmar", "¿Desea cerrar sesion?"):
            self.root.destroy()

