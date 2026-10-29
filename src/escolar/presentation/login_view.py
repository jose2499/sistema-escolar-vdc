import tkinter as tk
from tkinter import messagebox

from escolar.infrastructure.repositorios_memoria import RepositorioUsuariosMemoria
from escolar.presentation.dashboard_view import DashboardView
from escolar.use_cases.autenticar import AutenticarUsuario, ErrorAutenticacion


class LoginView:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Escolar VDC - Inicio de Sesión")
        self.root.geometry("420x400")
        self.root.resizable(False, False)

        self.repo_usuarios = RepositorioUsuariosMemoria()
        self.use_case_autenticar = AutenticarUsuario(self.repo_usuarios)

        self._crear_interfaz()

    def _crear_interfaz(self):
        label_titulo = tk.Label(
            self.root,
            text="I.E. N° 51037 Virgen del Carmen",
            font=("Arial", 14, "bold"),
            fg="#2B579A",
        )
        label_titulo.pack(pady=(25, 5))

        label_subtitulo = tk.Label(
            self.root,
            text="Sistema de Gestión Escolar",
            font=("Arial", 10, "italic"),
            fg="#555555",
        )
        label_subtitulo.pack(pady=(0, 20))

        lbl_dni = tk.Label(self.root, text="DNI (8 dígitos):", font=("Arial", 10))
        lbl_dni.pack(anchor="w", padx=50)

        self.entry_dni = tk.Entry(self.root, font=("Arial", 11), width=28)
        self.entry_dni.pack(padx=50, pady=(2, 12))
        self.entry_dni.focus_set()

        lbl_clave = tk.Label(self.root, text="Contraseña:", font=("Arial", 10))
        lbl_clave.pack(anchor="w", padx=50)

        frame_clave = tk.Frame(self.root)
        frame_clave.pack(padx=50, pady=(2, 20))

        self.entry_clave = tk.Entry(frame_clave, show="*", font=("Arial", 11), width=22)
        self.entry_clave.pack(side="left")

        self.btn_ver = tk.Button(
            frame_clave,
            text="👁",
            font=("Arial", 8),
            command=self._toggle_clave,
            width=3,
        )
        self.btn_ver.pack(side="left", padx=(5, 0))

        self.root.bind("<Return>", lambda event: self._iniciar_sesion())

        btn_ingresar = tk.Button(
            self.root,
            text="INICIAR SESIÓN",
            bg="#2B579A",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            command=self._iniciar_sesion,
        )
        btn_ingresar.pack(ipady=5, ipadx=15)

    def _toggle_clave(self):
        if self.entry_clave.cget("show") == "*":
            self.entry_clave.config(show="")
        else:
            self.entry_clave.config(show="*")

    def _iniciar_sesion(self):
        dni = self.entry_dni.get().strip()
        clave = self.entry_clave.get().strip()

        if not dni or not clave:
            messagebox.showwarning("Atención", "Por favor ingrese su DNI y contraseña.")
            return

        try:
            usuario = self.use_case_autenticar.ejecutar(dni, clave)
            self.root.unbind("<Return>")
            self.root.destroy()

            root_dashboard = tk.Tk()
            root_dashboard.eval("tk::PlaceWindow . center")
            DashboardView(root_dashboard, usuario)
            root_dashboard.mainloop()

        except ErrorAutenticacion as error:
            messagebox.showerror("Error de Acceso", str(error))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
