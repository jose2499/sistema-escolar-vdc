from datetime import date

import customtkinter as ctk
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from escolar.domain.entities import (
    Asistencia,
    Calificacion,
    Curso,
    EstadoAsistencia,
    Estudiante,
    Rol,
    Usuario,
)
from escolar.domain.errors import ErrorDeDominio
from escolar.domain.seguridad import hash_password
from escolar.infrastructure.models import Base, EstudianteModel
from escolar.infrastructure.repositorios_memoria import (
    RepositorioAsistenciaMemoria,
    RepositorioCursosMemoria,
    RepositorioEstudiantesMemoria,
    RepositorioUsuariosMemoria,
)
from escolar.infrastructure.repositorios_sqlalchemy import RepositorioCalificacionesSQLAlchemy
from escolar.use_cases.autenticar import AutenticarUsuario
from escolar.use_cases.consultar_asistencia import ConsultarAsistencia
from escolar.use_cases.consultar_calificaciones import ConsultarCalificaciones
from escolar.use_cases.registrar_asistencia import RegistrarAsistencia
from escolar.use_cases.registrar_calificacion import RegistrarCalificacion

# =========================================================
# CONFIGURACIÓN VISUAL
# =========================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR = {
    "sidebar": "#101D35",
    "sidebar_secondary": "#192B49",
    "sidebar_hover": "#263D60",
    "primary": "#4263EB",
    "primary_hover": "#3451C6",
    "accent": "#16B8A6",
    "accent_hover": "#109887",
    "background": "#F4F7FC",
    "surface": "#FFFFFF",
    "surface_alt": "#F8FAFD",
    "text": "#17233B",
    "muted": "#718096",
    "border": "#E5EAF2",
    "success": "#159B72",
    "success_bg": "#E7F7F0",
    "danger": "#DC4C64",
    "danger_bg": "#FDECEF",
    "warning": "#D99527",
    "warning_bg": "#FFF5DF",
    "info": "#3975D7",
}

FONT = "Segoe UI"


# =========================================================
# SERVICIOS DE DEMOSTRACIÓN
# =========================================================

URL_BD = "sqlite:///escolar.db"


def crear_sesion_bd(url=URL_BD):
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def sembrar_si_vacia(session, estudiantes):
    if session.scalar(select(func.count()).select_from(EstudianteModel)):
        return
    for numero, estudiante in enumerate(estudiantes, start=1):
        session.add(
            EstudianteModel(
                codigo=estudiante.id,
                nombre=estudiante.nombre,
                dni=str(90000000 + numero),
            )
        )
    session.commit()
    repo = RepositorioCalificacionesSQLAlchemy(session)
    for estudiante in estudiantes:
        repo.guardar(Calificacion(estudiante.id, "C1", 1, 14, "U2"))
        repo.guardar(Calificacion(estudiante.id, "C2", 1, 16, "U3"))


def crear_servicios_demo():
    clave = hash_password("clave123", iteraciones=1000)

    usuarios = [
        Usuario("U1", "11111111", "Ana Admin", Rol.ADMIN, clave),
        Usuario("U2", "22222222", "Diego Docente", Rol.DOCENTE, clave),
        Usuario("U3", "55555555", "Dora Docente", Rol.DOCENTE, clave),
        Usuario("U4", "33333333", "Ada Apoderada", Rol.APODERADO, clave),
        Usuario("U5", "66666666", "Aldo Apoderado", Rol.APODERADO, clave),
        Usuario("U6", "77777777", "Eli Estudiante", Rol.ESTUDIANTE, clave),
    ]

    estudiantes = [
        Estudiante("E1", "Luis Quispe", "5to", "A", "U4"),
        Estudiante("E2", "Mia Ccori", "5to", "A", "U5"),
        Estudiante("E3", "Eli Estudiante", "4to", "B", "U5", "U6"),
    ]

    cursos = [
        Curso("C1", "Matemática", "U2"),
        Curso("C2", "Comunicación", "U3"),
    ]

    repo_usuarios = RepositorioUsuariosMemoria(usuarios)
    repo_estudiantes = RepositorioEstudiantesMemoria(estudiantes)
    repo_cursos = RepositorioCursosMemoria(cursos)
    session = crear_sesion_bd()
    sembrar_si_vacia(session, estudiantes)
    repo_calificaciones = RepositorioCalificacionesSQLAlchemy(session)
    repo_asistencias = RepositorioAsistenciaMemoria()

    return {
        "autenticar": AutenticarUsuario(repo_usuarios),
        "usuarios": repo_usuarios,
        "estudiantes": repo_estudiantes,
        "cursos": repo_cursos,
        "lista_usuarios": usuarios,
        "lista_estudiantes": estudiantes,
        "lista_cursos": cursos,
        "calificaciones": repo_calificaciones,
        "asistencias": repo_asistencias,
        "registrar_calificacion": RegistrarCalificacion(
            repo_estudiantes,
            repo_cursos,
            repo_calificaciones,
        ),
        "consultar_calificaciones": ConsultarCalificaciones(
            repo_estudiantes,
            repo_cursos,
            repo_calificaciones,
        ),
        "registrar_asistencia": RegistrarAsistencia(
            repo_estudiantes,
            repo_asistencias,
        ),
        "consultar_asistencia": ConsultarAsistencia(
            repo_estudiantes,
            repo_asistencias,
        ),
    }


# =========================================================
# COMPONENTE DE ALERTAS
# =========================================================


class Alerta(ctk.CTkToplevel):
    def __init__(self, padre, tipo, titulo, mensaje):
        super().__init__(padre)

        estilos = {
            "exito": {
                "color": COLOR["success"],
                "fondo": COLOR["success_bg"],
                "icono": "✓",
            },
            "error": {
                "color": COLOR["danger"],
                "fondo": COLOR["danger_bg"],
                "icono": "!",
            },
            "info": {
                "color": COLOR["info"],
                "fondo": "#EAF1FE",
                "icono": "i",
            },
            "aviso": {
                "color": COLOR["warning"],
                "fondo": COLOR["warning_bg"],
                "icono": "!",
            },
        }

        estilo = estilos.get(tipo, estilos["info"])

        self.title(titulo)
        self.geometry("440x270")
        self.resizable(False, False)
        self.configure(fg_color=COLOR["surface"])
        self.transient(padre)
        self.grab_set()

        self.update_idletasks()

        x = padre.winfo_rootx() + (padre.winfo_width() - 440) // 2

        y = padre.winfo_rooty() + (padre.winfo_height() - 270) // 2

        self.geometry(f"440x270+{x}+{y}")

        ctk.CTkFrame(
            self,
            height=5,
            corner_radius=0,
            fg_color=estilo["color"],
        ).pack(fill="x")

        ctk.CTkLabel(
            self,
            text=estilo["icono"],
            width=62,
            height=62,
            corner_radius=31,
            fg_color=estilo["fondo"],
            text_color=estilo["color"],
            font=(FONT, 30, "bold"),
        ).pack(pady=(23, 10))

        ctk.CTkLabel(
            self,
            text=titulo,
            font=(FONT, 19, "bold"),
            text_color=COLOR["text"],
        ).pack(pady=3)

        ctk.CTkLabel(
            self,
            text=mensaje,
            font=(FONT, 12),
            text_color=COLOR["muted"],
            wraplength=370,
            justify="center",
        ).pack(padx=25, pady=10)

        ctk.CTkButton(
            self,
            text="ENTENDIDO",
            width=145,
            height=38,
            corner_radius=10,
            fg_color=estilo["color"],
            hover_color=estilo["color"],
            command=self.destroy,
        ).pack(pady=(5, 15))

        self.bind("<Return>", lambda _: self.destroy())
        self.bind("<Escape>", lambda _: self.destroy())


# =========================================================
# APLICACIÓN
# =========================================================


class AplicacionEscolar(ctk.CTk):
    NOMBRES = {
        "inicio": "Panel principal",
        "usuarios": "Gestión de usuarios",
        "estudiantes": "Estudiantes",
        "docentes": "Docentes",
        "cursos": "Cursos",
        "calificaciones": "Calificaciones",
        "asistencia": "Asistencia",
        "avisos": "Avisos",
        "calendario": "Calendario",
    }

    ICONOS = {
        "inicio": "⌂",
        "usuarios": "US",
        "estudiantes": "ES",
        "docentes": "DO",
        "cursos": "CU",
        "calificaciones": "CA",
        "asistencia": "AS",
        "avisos": "AV",
        "calendario": "CL",
    }

    def __init__(self):
        super().__init__()

        self.title("Sistema Escolar VDC")
        self.geometry("1320x830")
        self.minsize(1050, 700)
        self.configure(fg_color=COLOR["background"])

        self.servicios = crear_servicios_demo()

        self.sesion = None
        self.modulo_actual = "inicio"
        self.mostrar_password = False

        self.sidebar = None
        self.contenido = None
        self.encabezado_titulo = None
        self.botones_menu = {}

        self.mostrar_login()

    # =====================================================
    # FUNCIONES GENERALES
    # =====================================================

    def alerta(self, tipo, titulo, mensaje):
        Alerta(self, tipo, titulo, mensaje)

    def limpiar_ventana(self):
        for widget in self.winfo_children():
            widget.destroy()

    def limpiar_contenido(self):
        if self.contenido is not None:
            for widget in self.contenido.winfo_children():
                widget.destroy()

    def crear_boton(
        self,
        padre,
        texto,
        comando,
        color=None,
        ancho=180,
        alto=40,
    ):
        return ctk.CTkButton(
            padre,
            text=texto,
            command=comando,
            width=ancho,
            height=alto,
            corner_radius=10,
            fg_color=color or COLOR["primary"],
            hover_color=COLOR["primary_hover"],
            text_color="white",
            font=(FONT, 12, "bold"),
            cursor="hand2",
        )

    def crear_tarjeta(self, padre, titulo, valor, detalle=""):
        tarjeta = ctk.CTkFrame(
            padre,
            fg_color=COLOR["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLOR["border"],
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo.upper(),
            font=(FONT, 10, "bold"),
            text_color=COLOR["muted"],
        ).pack(anchor="w", padx=20, pady=(17, 5))

        ctk.CTkLabel(
            tarjeta,
            text=str(valor),
            font=(FONT, 29, "bold"),
            text_color=COLOR["primary"],
        ).pack(anchor="w", padx=20)

        if detalle:
            ctk.CTkLabel(
                tarjeta,
                text=detalle,
                font=(FONT, 10),
                text_color=COLOR["muted"],
            ).pack(anchor="w", padx=20, pady=(4, 16))
        else:
            ctk.CTkLabel(tarjeta, text="").pack(pady=8)

        return tarjeta

    def titulo_seccion(self, padre, titulo, descripcion=""):
        ctk.CTkLabel(
            padre,
            text=titulo,
            font=(FONT, 27, "bold"),
            text_color=COLOR["text"],
        ).pack(anchor="w", padx=30, pady=(25, 4))

        if descripcion:
            ctk.CTkLabel(
                padre,
                text=descripcion,
                font=(FONT, 12),
                text_color=COLOR["muted"],
            ).pack(anchor="w", padx=30, pady=(0, 18))

    def crear_panel(self, padre, titulo=None):
        panel = ctk.CTkFrame(
            padre,
            fg_color=COLOR["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLOR["border"],
        )

        if titulo:
            ctk.CTkLabel(
                panel,
                text=titulo,
                font=(FONT, 15, "bold"),
                text_color=COLOR["text"],
            ).pack(anchor="w", padx=20, pady=(17, 10))

        return panel

    # =====================================================
    # LOGIN
    # =====================================================

    def mostrar_login(self):
        self.limpiar_ventana()

        self.sidebar = None
        self.contenido = None
        self.botones_menu = {}

        fondo = ctk.CTkFrame(
            self,
            fg_color=COLOR["background"],
            corner_radius=0,
        )
        fondo.pack(fill="both", expand=True)

        decoracion = ctk.CTkFrame(
            fondo,
            fg_color=COLOR["sidebar"],
            corner_radius=0,
            width=470,
        )
        decoracion.pack(side="left", fill="y")
        decoracion.pack_propagate(False)

        ctk.CTkLabel(
            decoracion,
            text="VDC",
            font=(FONT, 55, "bold"),
            text_color="white",
        ).pack(anchor="w", padx=55, pady=(150, 5))

        ctk.CTkLabel(
            decoracion,
            text="VIRGEN DEL CARMEN",
            font=(FONT, 17, "bold"),
            text_color="#AFC6E8",
        ).pack(anchor="w", padx=60)

        ctk.CTkFrame(
            decoracion,
            width=70,
            height=4,
            fg_color=COLOR["accent"],
            corner_radius=5,
        ).pack(anchor="w", padx=60, pady=25)

        ctk.CTkLabel(
            decoracion,
            text="Sistema de gestión\nacadémica escolar",
            font=(FONT, 24, "bold"),
            text_color="white",
            justify="left",
        ).pack(anchor="w", padx=60, pady=5)

        ctk.CTkLabel(
            decoracion,
            text=(
                "Una plataforma para conectar la comunidad educativa "
                "y facilitar la gestión académica."
            ),
            font=(FONT, 12),
            text_color="#B8C8DD",
            wraplength=320,
            justify="left",
        ).pack(anchor="w", padx=60, pady=12)

        ctk.CTkLabel(
            decoracion,
            text="PLATAFORMA INSTITUCIONAL · VDC",
            font=(FONT, 9, "bold"),
            text_color="#8FA8C8",
        ).pack(side="bottom", anchor="w", padx=60, pady=30)

        zona_login = ctk.CTkFrame(
            fondo,
            fg_color="transparent",
        )
        zona_login.pack(
            side="left",
            fill="both",
            expand=True,
        )

        tarjeta = ctk.CTkFrame(
            zona_login,
            width=430,
            height=510,
            fg_color=COLOR["surface"],
            corner_radius=22,
            border_width=1,
            border_color=COLOR["border"],
        )
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")
        tarjeta.pack_propagate(False)

        ctk.CTkLabel(
            tarjeta,
            text="Bienvenido",
            font=(FONT, 28, "bold"),
            text_color=COLOR["text"],
        ).pack(anchor="w", padx=38, pady=(42, 3))

        ctk.CTkLabel(
            tarjeta,
            text="Ingresa tus credenciales institucionales.",
            font=(FONT, 12),
            text_color=COLOR["muted"],
        ).pack(anchor="w", padx=38, pady=(0, 28))

        ctk.CTkLabel(
            tarjeta,
            text="DOCUMENTO DE IDENTIDAD",
            font=(FONT, 10, "bold"),
            text_color=COLOR["text"],
        ).pack(anchor="w", padx=40, pady=(0, 6))

        self.dni = ctk.CTkEntry(
            tarjeta,
            height=46,
            corner_radius=10,
            border_color=COLOR["border"],
            placeholder_text="Ingresa tu DNI",
            font=(FONT, 13),
        )
        self.dni.pack(fill="x", padx=38)

        ctk.CTkLabel(
            tarjeta,
            text="CONTRASEÑA",
            font=(FONT, 10, "bold"),
            text_color=COLOR["text"],
        ).pack(anchor="w", padx=40, pady=(20, 6))

        fila_password = ctk.CTkFrame(
            tarjeta,
            fg_color="transparent",
        )
        fila_password.pack(fill="x", padx=38)

        self.password = ctk.CTkEntry(
            fila_password,
            height=46,
            corner_radius=10,
            border_color=COLOR["border"],
            placeholder_text="Ingresa tu contraseña",
            show="*",
            font=(FONT, 13),
        )
        self.password.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 7),
        )

        self.boton_ver = ctk.CTkButton(
            fila_password,
            text="Ver",
            width=58,
            height=46,
            corner_radius=10,
            fg_color=COLOR["surface_alt"],
            hover_color=COLOR["border"],
            text_color=COLOR["text"],
            command=self.alternar_password,
        )
        self.boton_ver.pack(side="left")

        self.crear_boton(
            tarjeta,
            "INICIAR SESIÓN",
            self.iniciar_sesion,
            ancho=350,
            alto=46,
        ).pack(fill="x", padx=38, pady=(28, 13))

        ctk.CTkLabel(
            tarjeta,
            text="Cuenta de demostración: clave123",
            font=(FONT, 10),
            text_color=COLOR["muted"],
        ).pack(pady=5)

        self.dni.bind(
            "<Return>",
            lambda _: self.password.focus(),
        )

        self.password.bind(
            "<Return>",
            lambda _: self.iniciar_sesion(),
        )

        self.dni.focus()

    def alternar_password(self):
        self.mostrar_password = not self.mostrar_password

        self.password.configure(show="" if self.mostrar_password else "*")

        self.boton_ver.configure(text="Ocultar" if self.mostrar_password else "Ver")

    def iniciar_sesion(self):
        dni = self.dni.get().strip()
        password = self.password.get()

        if not dni or not password:
            self.alerta(
                "error",
                "Datos incompletos",
                "Ingresa tu DNI y contraseña.",
            )
            return

        if len(dni) != 8 or not dni.isdigit():
            self.alerta(
                "error",
                "DNI inválido",
                "El DNI debe contener exactamente 8 dígitos.",
            )
            return

        try:
            self.sesion = self.servicios["autenticar"].ejecutar(
                dni,
                password,
            )

            self.modulo_actual = "inicio"
            self.construir_estructura()
            self.mostrar_panel()

        except ErrorDeDominio as error:
            self.alerta(
                "error",
                "Acceso denegado",
                str(error),
            )

    # =====================================================
    # ESTRUCTURA PRINCIPAL
    # =====================================================

    def construir_estructura(self):
        self.limpiar_ventana()

        principal = ctk.CTkFrame(
            self,
            fg_color=COLOR["background"],
            corner_radius=0,
        )
        principal.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkFrame(
            principal,
            width=245,
            fg_color=COLOR["sidebar"],
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="VDC",
            font=(FONT, 30, "bold"),
            text_color="white",
        ).pack(anchor="w", padx=25, pady=(28, 0))

        ctk.CTkLabel(
            self.sidebar,
            text="SISTEMA ESCOLAR",
            font=(FONT, 10, "bold"),
            text_color="#9EB4D0",
        ).pack(anchor="w", padx=27, pady=(0, 24))

        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color="#344967",
        ).pack(fill="x", padx=18, pady=4)

        ctk.CTkLabel(
            self.sidebar,
            text="NAVEGACIÓN",
            font=(FONT, 9, "bold"),
            text_color="#91A9C7",
        ).pack(anchor="w", padx=23, pady=(22, 10))

        self.botones_menu = {}

        opciones = [("inicio", "Inicio")]

        for permiso in self.sesion.permisos:
            opciones.append(
                (
                    permiso,
                    self.NOMBRES.get(permiso, permiso.title()),
                )
            )

        for modulo, nombre in opciones:
            boton = ctk.CTkButton(
                self.sidebar,
                text=f"{self.ICONOS.get(modulo, 'MD')}     {nombre}",
                height=43,
                corner_radius=10,
                anchor="w",
                fg_color="transparent",
                hover_color=COLOR["sidebar_hover"],
                text_color="#DCE6F4",
                font=(FONT, 12),
                command=lambda m=modulo: self.navegar(m),
            )

            boton.pack(fill="x", padx=12, pady=3)
            self.botones_menu[modulo] = boton

        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color="#344967",
        ).pack(fill="x", padx=18, pady=(20, 12))

        usuario = self.sesion.usuario

        ctk.CTkLabel(
            self.sidebar,
            text="SESIÓN ACTIVA",
            font=(FONT, 9, "bold"),
            text_color="#91A9C7",
        ).pack(anchor="w", padx=22, pady=(5, 6))

        ctk.CTkLabel(
            self.sidebar,
            text=usuario.nombre,
            font=(FONT, 12, "bold"),
            text_color="white",
            wraplength=195,
        ).pack(anchor="w", padx=22, pady=3)

        ctk.CTkLabel(
            self.sidebar,
            text=usuario.rol.value.upper(),
            font=(FONT, 9, "bold"),
            text_color="#A7C0DD",
        ).pack(anchor="w", padx=22, pady=(0, 12))

        ctk.CTkButton(
            self.sidebar,
            text="Cerrar sesión",
            height=40,
            corner_radius=10,
            fg_color="#963C50",
            hover_color="#B4475F",
            text_color="white",
            font=(FONT, 11, "bold"),
            command=self.cerrar_sesion,
        ).pack(side="bottom", fill="x", padx=15, pady=20)

        zona = ctk.CTkFrame(
            principal,
            fg_color=COLOR["background"],
            corner_radius=0,
        )
        zona.pack(side="left", fill="both", expand=True)

        encabezado = ctk.CTkFrame(
            zona,
            height=72,
            fg_color=COLOR["surface"],
            corner_radius=0,
        )
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        self.encabezado_titulo = ctk.CTkLabel(
            encabezado,
            text="Panel principal",
            font=(FONT, 17, "bold"),
            text_color=COLOR["text"],
        )
        self.encabezado_titulo.pack(side="left", padx=30)

        ctk.CTkLabel(
            encabezado,
            text=date.today().strftime("%d/%m/%Y"),
            font=(FONT, 11),
            text_color=COLOR["muted"],
        ).pack(side="right", padx=30)

        self.contenido = ctk.CTkScrollableFrame(
            zona,
            fg_color=COLOR["background"],
            corner_radius=0,
        )
        self.contenido.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=0,
        )

        self.actualizar_menu("inicio")

    def actualizar_menu(self, modulo):
        for nombre, boton in self.botones_menu.items():
            activo = nombre == modulo

            boton.configure(
                fg_color=(COLOR["sidebar_hover"] if activo else "transparent"),
                text_color="white" if activo else "#DCE6F4",
                font=(
                    FONT,
                    12,
                    "bold" if activo else "normal",
                ),
            )

    # =====================================================
    # NAVEGACIÓN SIN RECONSTRUIR LA VENTANA
    # =====================================================

    def navegar(self, modulo):
        if self.sesion is None:
            return

        if modulo != "inicio" and modulo not in self.sesion.permisos:
            self.alerta(
                "error",
                "Acceso restringido",
                "Tu perfil no tiene permiso para acceder a este módulo.",
            )
            return

        self.modulo_actual = modulo

        self.actualizar_menu(modulo)

        titulo = self.NOMBRES.get(
            modulo,
            modulo.title(),
        )

        self.encabezado_titulo.configure(text=titulo)

        self.limpiar_contenido()

        if modulo == "inicio":
            self.mostrar_panel()
        elif modulo == "calificaciones":
            self.pantalla_calificaciones()
        elif modulo == "asistencia":
            self.pantalla_asistencia()
        elif modulo == "estudiantes":
            self.pantalla_estudiantes()
        elif modulo == "cursos":
            self.pantalla_cursos()
        elif modulo == "docentes":
            self.pantalla_docentes()
        elif modulo == "usuarios":
            self.pantalla_usuarios()
        else:
            self.pantalla_pendiente(titulo)

    # =====================================================
    # PANEL PRINCIPAL
    # =====================================================

    def mostrar_panel(self):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            f"¡Hola, {self.sesion.usuario.nombre}!",
            "Bienvenido al Sistema Escolar Virgen del Carmen.",
        )

        cantidad_estudiantes = len(self.estudiantes_visibles())

        cantidad_cursos = len(self.cursos_visibles())

        cantidad_notas = len(
            self.servicios["consultar_calificaciones"].ejecutar(self.sesion.usuario)
        )

        cantidad_asistencias = sum(
            len(self.servicios["asistencias"].listar_por_estudiante(estudiante.id))
            for estudiante in self.estudiantes_visibles()
        )

        resumen = ctk.CTkFrame(
            padre,
            fg_color="transparent",
        )
        resumen.pack(fill="x", padx=20, pady=5)

        tarjetas = [
            ("Estudiantes", cantidad_estudiantes, "Registros visibles"),
            ("Cursos", cantidad_cursos, "Cursos disponibles"),
            ("Calificaciones", cantidad_notas, "Notas consultables"),
            ("Asistencias", cantidad_asistencias, "Registros visibles"),
        ]

        for columna, datos in enumerate(tarjetas):
            card = self.crear_tarjeta(
                resumen,
                *datos,
            )

            card.grid(
                row=0,
                column=columna,
                padx=7,
                pady=8,
                sticky="nsew",
            )

            resumen.grid_columnconfigure(
                columna,
                weight=1,
            )

        ctk.CTkLabel(
            padre,
            text="TUS MÓDULOS",
            font=(FONT, 14, "bold"),
            text_color=COLOR["text"],
        ).pack(anchor="w", padx=30, pady=(25, 12))

        panel = ctk.CTkFrame(
            padre,
            fg_color="transparent",
        )
        panel.pack(fill="both", expand=True, padx=20)

        for indice, modulo in enumerate(self.sesion.permisos):
            nombre = self.NOMBRES.get(
                modulo,
                modulo.title(),
            )

            card = ctk.CTkFrame(
                panel,
                fg_color=COLOR["surface"],
                corner_radius=16,
                border_width=1,
                border_color=COLOR["border"],
            )

            card.grid(
                row=indice // 2,
                column=indice % 2,
                padx=8,
                pady=8,
                sticky="nsew",
            )

            ctk.CTkLabel(
                card,
                text=self.ICONOS.get(modulo, "MD"),
                width=42,
                height=42,
                corner_radius=12,
                fg_color="#EAF0FF",
                text_color=COLOR["primary"],
                font=(FONT, 13, "bold"),
            ).pack(anchor="w", padx=18, pady=(17, 8))

            ctk.CTkLabel(
                card,
                text=nombre,
                font=(FONT, 15, "bold"),
                text_color=COLOR["text"],
            ).pack(anchor="w", padx=18, pady=3)

            descripcion = {
                "calificaciones": "Consulta y registra el rendimiento académico.",
                "asistencia": "Revisa el seguimiento de asistencia.",
                "estudiantes": "Consulta la información de estudiantes.",
                "cursos": "Consulta los cursos disponibles.",
                "docentes": "Consulta el personal docente.",
                "usuarios": "Consulta las cuentas del sistema.",
                "avisos": "Apartado de comunicación institucional.",
                "calendario": "Apartado de actividades académicas.",
            }.get(
                modulo,
                "Módulo disponible según tu perfil.",
            )

            ctk.CTkLabel(
                card,
                text=descripcion,
                font=(FONT, 10),
                text_color=COLOR["muted"],
                wraplength=390,
                justify="left",
            ).pack(anchor="w", padx=18, pady=4)

            self.crear_boton(
                card,
                "ABRIR MÓDULO",
                lambda m=modulo: self.navegar(m),
                ancho=145,
                alto=34,
            ).pack(anchor="w", padx=18, pady=(12, 17))

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)

    # =====================================================
    # DATOS VISIBLES SEGÚN EL PERFIL
    # =====================================================

    def estudiantes_visibles(self):
        usuario = self.sesion.usuario
        repo = self.servicios["estudiantes"]

        if usuario.rol in (Rol.ADMIN, Rol.DOCENTE):
            return self.servicios["lista_estudiantes"]

        if usuario.rol is Rol.APODERADO:
            return repo.listar_por_apoderado(usuario.id)

        estudiante = repo.obtener_por_usuario(usuario.id)

        return [estudiante] if estudiante else []

    def cursos_visibles(self):
        usuario = self.sesion.usuario
        repo = self.servicios["cursos"]

        if usuario.rol is Rol.DOCENTE:
            return repo.listar_por_docente(usuario.id)

        if usuario.rol is Rol.ADMIN:
            return self.servicios["lista_cursos"]

        return []

    # =====================================================
    # ESTUDIANTES
    # =====================================================

    def pantalla_estudiantes(self):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            "Estudiantes",
            "Información de los estudiantes vinculados a tu perfil.",
        )

        estudiantes = self.estudiantes_visibles()

        panel = self.crear_panel(
            padre,
            "Directorio de estudiantes",
        )
        panel.pack(fill="x", padx=28, pady=8)

        if not estudiantes:
            ctk.CTkLabel(
                panel,
                text="No hay estudiantes disponibles.",
                text_color=COLOR["muted"],
            ).pack(pady=25)
            return

        for estudiante in estudiantes:
            fila = ctk.CTkFrame(
                panel,
                fg_color=COLOR["surface_alt"],
                corner_radius=10,
            )
            fila.pack(fill="x", padx=15, pady=5)

            ctk.CTkLabel(
                fila,
                text=estudiante.nombre,
                font=(FONT, 13, "bold"),
                text_color=COLOR["text"],
            ).pack(side="left", padx=15, pady=13)

            ctk.CTkLabel(
                fila,
                text=(f"{estudiante.grado} {estudiante.seccion}"),
                font=(FONT, 11),
                text_color=COLOR["muted"],
            ).pack(side="right", padx=15)

    # =====================================================
    # CURSOS
    # =====================================================

    def pantalla_cursos(self):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            "Cursos",
            "Listado de cursos disponibles según tu perfil.",
        )

        cursos = self.cursos_visibles()

        panel = self.crear_panel(
            padre,
            "Directorio de cursos",
        )
        panel.pack(fill="x", padx=28, pady=8)

        if not cursos:
            ctk.CTkLabel(
                panel,
                text="No hay cursos disponibles para tu perfil.",
                text_color=COLOR["muted"],
            ).pack(pady=25)
            return

        for curso in cursos:
            docente = next(
                (
                    usuario
                    for usuario in self.servicios["lista_usuarios"]
                    if usuario.id == curso.docente_id
                ),
                None,
            )

            fila = ctk.CTkFrame(
                panel,
                fg_color=COLOR["surface_alt"],
                corner_radius=10,
            )
            fila.pack(fill="x", padx=15, pady=5)

            izquierda = ctk.CTkFrame(
                fila,
                fg_color="transparent",
            )
            izquierda.pack(side="left", padx=15, pady=10)

            ctk.CTkLabel(
                izquierda,
                text=curso.nombre,
                font=(FONT, 13, "bold"),
                text_color=COLOR["text"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                izquierda,
                text=(docente.nombre if docente else "Docente no disponible"),
                font=(FONT, 10),
                text_color=COLOR["muted"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                fila,
                text=curso.id,
                font=(FONT, 10, "bold"),
                text_color=COLOR["primary"],
            ).pack(side="right", padx=18)

    # =====================================================
    # DOCENTES
    # =====================================================

    def pantalla_docentes(self):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            "Docentes",
            "Directorio del personal docente.",
        )

        if self.sesion.usuario.rol is not Rol.ADMIN:
            self.alerta(
                "error",
                "Acceso restringido",
                "Solo el administrador puede consultar este directorio.",
            )
            return

        docentes = [
            usuario for usuario in self.servicios["lista_usuarios"] if usuario.rol is Rol.DOCENTE
        ]

        panel = self.crear_panel(
            padre,
            "Personal docente",
        )
        panel.pack(fill="x", padx=28, pady=8)

        for docente in docentes:
            fila = ctk.CTkFrame(
                panel,
                fg_color=COLOR["surface_alt"],
                corner_radius=10,
            )
            fila.pack(fill="x", padx=15, pady=5)

            ctk.CTkLabel(
                fila,
                text=docente.nombre,
                font=(FONT, 13, "bold"),
                text_color=COLOR["text"],
            ).pack(side="left", padx=15, pady=13)

            ctk.CTkLabel(
                fila,
                text=f"DNI: {docente.dni}",
                font=(FONT, 10),
                text_color=COLOR["muted"],
            ).pack(side="right", padx=15)

    # =====================================================
    # USUARIOS
    # =====================================================

    def pantalla_usuarios(self):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            "Gestión de usuarios",
            "Consulta de cuentas registradas en el sistema.",
        )

        if self.sesion.usuario.rol is not Rol.ADMIN:
            self.alerta(
                "error",
                "Acceso restringido",
                "Solo el administrador puede consultar usuarios.",
            )
            return

        panel = self.crear_panel(
            padre,
            "Usuarios registrados",
        )
        panel.pack(fill="x", padx=28, pady=8)

        for usuario in self.servicios["lista_usuarios"]:
            fila = ctk.CTkFrame(
                panel,
                fg_color=COLOR["surface_alt"],
                corner_radius=10,
            )
            fila.pack(fill="x", padx=15, pady=5)

            izquierda = ctk.CTkFrame(
                fila,
                fg_color="transparent",
            )
            izquierda.pack(side="left", padx=15, pady=10)

            ctk.CTkLabel(
                izquierda,
                text=usuario.nombre,
                font=(FONT, 12, "bold"),
                text_color=COLOR["text"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                izquierda,
                text=usuario.dni,
                font=(FONT, 10),
                text_color=COLOR["muted"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                fila,
                text=usuario.rol.value.upper(),
                font=(FONT, 10, "bold"),
                text_color=COLOR["primary"],
            ).pack(side="right", padx=15)

    # =====================================================
    # MÓDULOS AÚN SIN CASOS DE USO
    # =====================================================

    def pantalla_pendiente(self, titulo):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            titulo,
            "Sistema Escolar Virgen del Carmen.",
        )

        panel = self.crear_panel(padre)
        panel.pack(fill="x", padx=28, pady=12)

        ctk.CTkLabel(
            panel,
            text="En preparación",
            font=(FONT, 20, "bold"),
            text_color=COLOR["warning"],
        ).pack(pady=(28, 8))

        ctk.CTkLabel(
            panel,
            text=(
                "Este módulo todavía no tiene operaciones conectadas "
                "a sus casos de uso y repositorios.\n\n"
                "La interfaz está preparada para incorporar "
                "sus funcionalidades en una siguiente etapa."
            ),
            font=(FONT, 12),
            text_color=COLOR["muted"],
            justify="center",
            wraplength=560,
        ).pack(padx=25, pady=(0, 28))

    # =====================================================
    # CALIFICACIONES
    # =====================================================

    def pantalla_calificaciones(self):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            "Calificaciones",
            "Consulta del rendimiento académico por estudiante y curso.",
        )

        if self.sesion.usuario.rol is Rol.DOCENTE:
            self.formulario_calificacion(padre)

        self.tabla_calificaciones(padre)

    def formulario_calificacion(self, padre):
        estudiantes = self.estudiantes_visibles()
        cursos = self.cursos_visibles()

        if not estudiantes or not cursos:
            return

        formulario = self.crear_panel(
            padre,
            "Registrar calificación",
        )
        formulario.pack(fill="x", padx=28, pady=8)

        campos = ctk.CTkFrame(
            formulario,
            fg_color="transparent",
        )
        campos.pack(fill="x", padx=15, pady=5)

        self.sel_estudiante = ctk.CTkOptionMenu(
            campos,
            values=[f"{e.id} - {e.nombre}" for e in estudiantes],
            height=40,
            corner_radius=9,
        )
        self.sel_estudiante.grid(
            row=0,
            column=0,
            padx=5,
            pady=7,
            sticky="ew",
        )

        self.sel_curso = ctk.CTkOptionMenu(
            campos,
            values=[f"{c.id} - {c.nombre}" for c in cursos],
            height=40,
            corner_radius=9,
        )
        self.sel_curso.grid(
            row=0,
            column=1,
            padx=5,
            pady=7,
            sticky="ew",
        )

        self.sel_periodo = ctk.CTkOptionMenu(
            campos,
            values=["1", "2", "3", "4"],
            height=40,
            corner_radius=9,
        )
        self.sel_periodo.grid(
            row=0,
            column=2,
            padx=5,
            pady=7,
            sticky="ew",
        )

        self.entrada_nota = ctk.CTkEntry(
            campos,
            height=40,
            corner_radius=9,
            placeholder_text="Nota de 0 a 20",
        )
        self.entrada_nota.grid(
            row=0,
            column=3,
            padx=5,
            pady=7,
            sticky="ew",
        )

        for columna in range(4):
            campos.grid_columnconfigure(
                columna,
                weight=1,
            )

        self.crear_boton(
            formulario,
            "GUARDAR CALIFICACIÓN",
            self.guardar_calificacion,
            ancho=220,
        ).pack(anchor="e", padx=20, pady=(5, 17))

    def guardar_calificacion(self):
        if self.sesion.usuario.rol is not Rol.DOCENTE:
            self.alerta(
                "error",
                "Permiso denegado",
                "Solo un docente puede registrar calificaciones.",
            )
            return

        try:
            estudiante_id = self.sel_estudiante.get().split(" - ", 1)[0]

            curso_id = self.sel_curso.get().split(" - ", 1)[0]

            periodo = int(self.sel_periodo.get())

            texto = self.entrada_nota.get().strip()

            if not texto:
                raise ValueError("Debes ingresar una nota.")

            nota = float(texto.replace(",", "."))

            self.servicios["registrar_calificacion"].ejecutar(
                self.sesion.usuario,
                estudiante_id,
                curso_id,
                periodo,
                nota,
            )

            self.alerta(
                "exito",
                "Calificación registrada",
                "La calificación se guardó correctamente.",
            )

            self.navegar("calificaciones")

        except ValueError as error:
            self.alerta(
                "error",
                "Dato inválido",
                str(error),
            )

        except ErrorDeDominio as error:
            self.alerta(
                "error",
                "No se pudo guardar",
                str(error),
            )

    def tabla_calificaciones(self, padre):
        try:
            calificaciones = self.servicios["consultar_calificaciones"].ejecutar(
                self.sesion.usuario
            )

        except ErrorDeDominio as error:
            self.alerta(
                "error",
                "Consulta no disponible",
                str(error),
            )
            return

        panel = self.crear_panel(
            padre,
            "Historial de calificaciones",
        )
        panel.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=10,
        )

        tabla = ctk.CTkScrollableFrame(
            panel,
            fg_color=COLOR["surface_alt"],
            corner_radius=10,
            height=270,
        )
        tabla.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )

        encabezados = [
            ("ESTUDIANTE", 0.34),
            ("CURSO", 0.28),
            ("PERIODO", 0.18),
            ("NOTA", 0.20),
        ]

        self.crear_fila_tabla(
            tabla,
            encabezados,
            encabezado=True,
        )

        if not calificaciones:
            ctk.CTkLabel(
                tabla,
                text="No existen calificaciones para mostrar.",
                text_color=COLOR["muted"],
            ).pack(pady=25)
            return

        for calificacion in calificaciones:
            estudiante = self.servicios["estudiantes"].obtener(calificacion.estudiante_id)

            curso = self.servicios["cursos"].obtener(calificacion.curso_id)

            valores = [
                estudiante.nombre if estudiante else calificacion.estudiante_id,
                curso.nombre if curso else calificacion.curso_id,
                str(calificacion.periodo),
                f"{calificacion.nota:.2f}",
            ]

            fila = self.crear_fila_tabla(
                tabla,
                list(
                    zip(
                        valores,
                        [0.31, 0.25, 0.15, 0.14],
                        strict=True,
                    )
                ),
            )
            if self.sesion.usuario.rol is Rol.DOCENTE:
                ctk.CTkButton(
                    fila,
                    text="Editar",
                    width=72,
                    height=30,
                    corner_radius=8,
                    fg_color=COLOR["primary"],
                    hover_color=COLOR["primary_hover"],
                    font=(FONT, 10, "bold"),
                    command=lambda item=calificacion: self.editar_calificacion(item),
                ).pack(side="right", padx=8, pady=5)

    def editar_calificacion(self, calificacion):
        """Permite al docente modificar una nota de uno de sus cursos."""
        if self.sesion.usuario.rol is not Rol.DOCENTE:
            self.alerta("error", "Permiso denegado", "Solo un docente puede editar calificaciones.")
            return
        if calificacion.docente_id != self.sesion.usuario.id:
            self.alerta(
                "error", "Acceso restringido", "Solo puedes editar tus propias calificaciones."
            )
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar calificación")
        ventana.geometry("390x280")
        ventana.resizable(False, False)
        ventana.configure(fg_color=COLOR["surface"])
        ventana.transient(self)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana, text="Editar calificación", font=(FONT, 20, "bold"), text_color=COLOR["text"]
        ).pack(pady=(24, 8))
        ctk.CTkLabel(
            ventana,
            text=(
                f"Estudiante: {calificacion.estudiante_id} · "
                f"Curso: {calificacion.curso_id} · "
                f"Periodo: {calificacion.periodo}"
            ),
            font=(FONT, 10),
            text_color=COLOR["muted"],
            wraplength=340,
        ).pack(padx=20, pady=8)
        entrada = ctk.CTkEntry(
            ventana, width=220, height=40, placeholder_text="Nueva nota (0 a 20)"
        )
        entrada.pack(pady=12)
        entrada.insert(0, str(calificacion.nota))

        def guardar_cambios():
            try:
                nota = float(entrada.get().strip().replace(",", "."))
                self.servicios["registrar_calificacion"].ejecutar(
                    self.sesion.usuario,
                    calificacion.estudiante_id,
                    calificacion.curso_id,
                    calificacion.periodo,
                    nota,
                )
                ventana.destroy()
                self.alerta(
                    "exito", "Calificación actualizada", "Los cambios se guardaron correctamente."
                )
                self.navegar("calificaciones")
            except ValueError:
                self.alerta("error", "Nota inválida", "Ingresa una nota numérica entre 0 y 20.")
            except ErrorDeDominio as error:
                self.alerta("error", "No se pudo actualizar", str(error))

        self.crear_boton(ventana, "GUARDAR CAMBIOS", guardar_cambios, ancho=220).pack(pady=10)

    # =====================================================
    # ASISTENCIA
    # =====================================================

    def pantalla_asistencia(self):
        padre = self.contenido

        self.titulo_seccion(
            padre,
            "Control de asistencia",
            "Registro y seguimiento de asistencia de estudiantes.",
        )

        if self.sesion.usuario.rol is Rol.DOCENTE:
            self.formulario_asistencia(padre)

        self.tabla_asistencia(padre)

    def formulario_asistencia(self, padre):
        estudiantes = self.estudiantes_visibles()

        if not estudiantes:
            return

        formulario = self.crear_panel(
            padre,
            "Registrar asistencia",
        )
        formulario.pack(fill="x", padx=28, pady=8)

        campos = ctk.CTkFrame(
            formulario,
            fg_color="transparent",
        )
        campos.pack(fill="x", padx=15, pady=5)

        self.asistencia_estudiante = ctk.CTkOptionMenu(
            campos,
            values=[f"{e.id} - {e.nombre}" for e in estudiantes],
            height=40,
            corner_radius=9,
        )
        self.asistencia_estudiante.grid(
            row=0,
            column=0,
            padx=5,
            pady=7,
            sticky="ew",
        )

        self.asistencia_estado = ctk.CTkOptionMenu(
            campos,
            values=[
                "Presente",
                "Falta",
                "Tardanza",
                "Justificada",
            ],
            height=40,
            corner_radius=9,
        )
        self.asistencia_estado.grid(
            row=0,
            column=1,
            padx=5,
            pady=7,
            sticky="ew",
        )

        self.asistencia_fecha = ctk.CTkEntry(
            campos,
            height=40,
            corner_radius=9,
            placeholder_text="AAAA-MM-DD",
        )
        self.asistencia_fecha.insert(
            0,
            date.today().isoformat(),
        )
        self.asistencia_fecha.grid(
            row=0,
            column=2,
            padx=5,
            pady=7,
            sticky="ew",
        )

        for columna in range(3):
            campos.grid_columnconfigure(
                columna,
                weight=1,
            )

        self.crear_boton(
            formulario,
            "REGISTRAR ASISTENCIA",
            self.guardar_asistencia,
            ancho=220,
        ).pack(anchor="e", padx=20, pady=(5, 17))

    def guardar_asistencia(self):
        if self.sesion.usuario.rol is not Rol.DOCENTE:
            self.alerta(
                "error",
                "Permiso denegado",
                "Solo un docente puede registrar asistencia.",
            )
            return

        try:
            estudiante_id = self.asistencia_estudiante.get().split(" - ", 1)[0]

            fecha = date.fromisoformat(self.asistencia_fecha.get().strip())

            estados = {
                "Presente": EstadoAsistencia.PRESENTE,
                "Falta": EstadoAsistencia.FALTA,
                "Tardanza": EstadoAsistencia.TARDANZA,
                "Justificada": EstadoAsistencia.JUSTIFICADA,
            }

            estado = estados[self.asistencia_estado.get()]

            self.servicios["registrar_asistencia"].ejecutar(
                self.sesion.usuario,
                estudiante_id,
                fecha,
                estado,
            )

            self.alerta(
                "exito",
                "Asistencia registrada",
                "El registro se guardó correctamente.",
            )

            self.navegar("asistencia")

        except ValueError:
            self.alerta(
                "error",
                "Fecha o estado inválido",
                "Verifica la fecha y utiliza el formato AAAA-MM-DD.",
            )

        except ErrorDeDominio as error:
            self.alerta(
                "error",
                "No se pudo registrar",
                str(error),
            )

    def editar_asistencia(self, registro):
        """Modifica el estado de una asistencia ya registrada."""
        if self.sesion.usuario.rol is not Rol.DOCENTE:
            self.alerta("error", "Permiso denegado", "Solo un docente puede editar asistencias.")
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar asistencia")
        ventana.geometry("390x300")
        ventana.resizable(False, False)
        ventana.configure(fg_color=COLOR["surface"])
        ventana.transient(self)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana, text="Editar asistencia", font=(FONT, 20, "bold"), text_color=COLOR["text"]
        ).pack(pady=(24, 8))
        ctk.CTkLabel(
            ventana,
            text=f"Estudiante: {registro.estudiante_id} · Fecha: {registro.fecha.isoformat()}",
            font=(FONT, 11),
            text_color=COLOR["muted"],
        ).pack(pady=8)
        opciones = {
            "Presente": EstadoAsistencia.PRESENTE,
            "Falta": EstadoAsistencia.FALTA,
            "Tardanza": EstadoAsistencia.TARDANZA,
            "Justificada": EstadoAsistencia.JUSTIFICADA,
        }
        selector = ctk.CTkOptionMenu(ventana, values=list(opciones.keys()), width=220, height=40)
        selector.set(
            next(
                (nombre for nombre, estado in opciones.items() if estado == registro.estado),
                "Presente",
            )
        )
        selector.pack(pady=14)

        def guardar_cambios():
            try:
                actualizada = Asistencia(
                    registro.estudiante_id, registro.fecha, opciones[selector.get()]
                )
                self.servicios["asistencias"].guardar(actualizada)
                ventana.destroy()
                self.alerta(
                    "exito", "Asistencia actualizada", "Los cambios se guardaron correctamente."
                )
                self.navegar("asistencia")
            except (KeyError, ValueError) as error:
                self.alerta("error", "No se pudo actualizar", str(error))

        self.crear_boton(ventana, "GUARDAR CAMBIOS", guardar_cambios, ancho=220).pack(pady=10)

    def tabla_asistencia(self, padre):
        estudiantes = self.estudiantes_visibles()

        panel = self.crear_panel(
            padre,
            "Seguimiento de asistencia",
        )
        panel.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=10,
        )

        tabla = ctk.CTkScrollableFrame(
            panel,
            fg_color=COLOR["background"],
            corner_radius=10,
            height=350,
        )
        tabla.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )

        if not estudiantes:
            ctk.CTkLabel(
                tabla,
                text="No hay estudiantes vinculados a tu usuario.",
                text_color=COLOR["muted"],
            ).pack(pady=20)
            return

        for estudiante in estudiantes:
            registros = self.servicios["asistencias"].listar_por_estudiante(estudiante.id)

            resumen = self.servicios["consultar_asistencia"].resumen(estudiante.id)

            tarjeta = ctk.CTkFrame(
                tabla,
                fg_color=COLOR["surface"],
                corner_radius=12,
                border_width=1,
                border_color=COLOR["border"],
            )
            tarjeta.pack(fill="x", padx=5, pady=7)

            ctk.CTkLabel(
                tarjeta,
                text=(f"{estudiante.nombre}  ·  {estudiante.grado} {estudiante.seccion}"),
                font=(FONT, 14, "bold"),
                text_color=COLOR["text"],
            ).pack(anchor="w", padx=18, pady=(15, 7))

            color_resumen = COLOR["danger"] if resumen.alerta else COLOR["muted"]

            ctk.CTkLabel(
                tarjeta,
                text=(
                    f"Días registrados: {resumen.total_dias}     "
                    f"Faltas: {resumen.faltas}     "
                    f"Inasistencia: {resumen.porcentaje_inasistencia}%"
                ),
                font=(FONT, 11),
                text_color=color_resumen,
            ).pack(anchor="w", padx=18, pady=4)

            if resumen.alerta:
                ctk.CTkLabel(
                    tarjeta,
                    text="ALERTA: el estudiante supera el límite de faltas.",
                    font=(FONT, 10, "bold"),
                    text_color=COLOR["danger"],
                ).pack(anchor="w", padx=18, pady=5)

            if registros:
                for registro in sorted(
                    registros,
                    key=lambda item: item.fecha,
                    reverse=True,
                ):
                    linea_registro = ctk.CTkFrame(tarjeta, fg_color="transparent")
                    linea_registro.pack(fill="x", padx=20, pady=2)
                    ctk.CTkLabel(
                        linea_registro,
                        text=f"{registro.fecha.isoformat()}     {registro.estado.value.upper()}",
                        font=(FONT, 10),
                        text_color=COLOR["muted"],
                    ).pack(side="left", padx=5)
                    if self.sesion.usuario.rol is Rol.DOCENTE:
                        ctk.CTkButton(
                            linea_registro,
                            text="Editar",
                            width=68,
                            height=26,
                            corner_radius=7,
                            fg_color=COLOR["primary"],
                            hover_color=COLOR["primary_hover"],
                            font=(FONT, 9, "bold"),
                            command=lambda item=registro: self.editar_asistencia(item),
                        ).pack(side="right", padx=5)
            else:
                ctk.CTkLabel(
                    tarjeta,
                    text="Sin registros de asistencia.",
                    font=(FONT, 10),
                    text_color=COLOR["muted"],
                ).pack(anchor="w", padx=25, pady=7)

            ctk.CTkLabel(
                tarjeta,
                text="",
            ).pack(pady=3)

    # =====================================================
    # FILAS DE TABLA
    # =====================================================

    def crear_fila_tabla(
        self,
        padre,
        columnas,
        encabezado=False,
    ):
        fila = ctk.CTkFrame(
            padre,
            fg_color=(COLOR["sidebar"] if encabezado else COLOR["surface"]),
            corner_radius=8,
        )
        fila.pack(fill="x", padx=5, pady=3)

        for texto, proporcion in columnas:
            ctk.CTkLabel(
                fila,
                text=str(texto),
                width=int(650 * proporcion),
                anchor="w",
                font=(
                    FONT,
                    10 if encabezado else 11,
                    "bold" if encabezado else "normal",
                ),
                text_color=("white" if encabezado else COLOR["text"]),
            ).pack(
                side="left",
                padx=8,
                pady=11,
            )
        return fila

    # =====================================================
    # CIERRE DE SESIÓN
    # =====================================================

    def cerrar_sesion(self):
        self.sesion = None
        self.mostrar_password = False
        self.mostrar_login()


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":
    app = AplicacionEscolar()
    app.mainloop()
