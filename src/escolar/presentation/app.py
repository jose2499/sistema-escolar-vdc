from datetime import date

import customtkinter as ctk

from escolar.domain.entities import (
    Calificacion,
    Curso,
    EstadoAsistencia,
    Estudiante,
    Rol,
    Usuario,
)
from escolar.domain.errors import ErrorDeDominio
from escolar.domain.seguridad import hash_password
from escolar.infrastructure.repositorios_memoria import (
    RepositorioAsistenciaMemoria,
    RepositorioCalificacionesMemoria,
    RepositorioCursosMemoria,
    RepositorioEstudiantesMemoria,
    RepositorioUsuariosMemoria,
)
from escolar.use_cases.autenticar import AutenticarUsuario
from escolar.use_cases.consultar_asistencia import ConsultarAsistencia
from escolar.use_cases.consultar_calificaciones import ConsultarCalificaciones
from escolar.use_cases.registrar_asistencia import RegistrarAsistencia
from escolar.use_cases.registrar_calificacion import RegistrarCalificacion

# --------------------------------------------------
# CONFIGURACIÓN VISUAL
# --------------------------------------------------

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL = "#17365D"
AZUL_CLARO = "#3973AC"
FONDO = "#F3F6FB"
BLANCO = "#FFFFFF"
TEXTO = "#263445"
GRIS = "#64748B"
VERDE = "#15803D"
ROJO = "#DC2626"
BORDE = "#DCE5F0"


# --------------------------------------------------
# SERVICIOS Y DATOS DE DEMOSTRACIÓN
# --------------------------------------------------


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
    repo_calificaciones = RepositorioCalificacionesMemoria()
    repo_asistencias = RepositorioAsistenciaMemoria()

    # Calificaciones de demostración.
    for estudiante_id in ("E1", "E2", "E3"):
        repo_calificaciones.guardar(Calificacion(estudiante_id, "C1", 1, 14, "U2"))
        repo_calificaciones.guardar(Calificacion(estudiante_id, "C2", 1, 16, "U3"))

    return {
        "autenticar": AutenticarUsuario(repo_usuarios),
        "estudiantes": repo_estudiantes,
        "cursos": repo_cursos,
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


# --------------------------------------------------
# VENTANA DE ALERTAS
# --------------------------------------------------


class Alerta(ctk.CTkToplevel):
    def __init__(self, padre, tipo, titulo, mensaje):
        super().__init__(padre)

        self.transient(padre)
        self.grab_set()
        self.resizable(False, False)
        self.configure(fg_color=BLANCO)

        colores = {
            "exito": VERDE,
            "error": ROJO,
            "info": AZUL_CLARO,
        }

        iconos = {
            "exito": "✓",
            "error": "!",
            "info": "i",
        }

        color = colores.get(tipo, AZUL_CLARO)

        ancho = 400
        alto = 250

        self.update_idletasks()

        x = padre.winfo_rootx() + (padre.winfo_width() - ancho) // 2
        y = padre.winfo_rooty() + (padre.winfo_height() - alto) // 2

        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        ctk.CTkLabel(
            self,
            text=iconos.get(tipo, "i"),
            width=60,
            height=60,
            corner_radius=30,
            fg_color=color,
            text_color=BLANCO,
            font=("Arial", 28, "bold"),
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            self,
            text=titulo,
            font=("Arial", 21, "bold"),
            text_color=AZUL,
        ).pack(pady=5)

        ctk.CTkLabel(
            self,
            text=mensaje,
            font=("Arial", 13),
            text_color=GRIS,
            wraplength=340,
        ).pack(pady=8)

        ctk.CTkButton(
            self,
            text="ACEPTAR",
            width=140,
            height=38,
            fg_color=color,
            hover_color=AZUL,
            command=self.destroy,
        ).pack(pady=12)

        self.attributes("-alpha", 0.0)
        self.animar(0.0)

    def animar(self, opacidad):
        if not self.winfo_exists():
            return

        nueva = min(opacidad + 0.15, 1.0)
        self.attributes("-alpha", nueva)

        if nueva < 1:
            self.after(20, lambda: self.animar(nueva))


# --------------------------------------------------
# APLICACIÓN PRINCIPAL
# --------------------------------------------------


class AplicacionEscolar(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Escolar VDC")
        self.geometry("1150x760")
        self.minsize(950, 650)
        self.configure(fg_color=FONDO)

        self.servicios = crear_servicios_demo()
        self.sesion = None
        self.mostrar_password = False

        self.mostrar_login()

    # --------------------------------------------------
    # FUNCIONES GENERALES
    # --------------------------------------------------

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def alerta(self, tipo, titulo, mensaje):
        Alerta(self, tipo, titulo, mensaje)

    def crear_titulo(self, padre, titulo, subtitulo=None):
        ctk.CTkLabel(
            padre,
            text=titulo,
            font=("Arial", 25, "bold"),
            text_color=AZUL,
        ).pack(anchor="w", padx=25, pady=(20, 5))

        if subtitulo:
            ctk.CTkLabel(
                padre,
                text=subtitulo,
                font=("Arial", 13),
                text_color=GRIS,
            ).pack(anchor="w", padx=25, pady=(0, 15))

    def boton(self, padre, texto, funcion, color=AZUL, ancho=180):
        return ctk.CTkButton(
            padre,
            text=texto,
            command=funcion,
            width=ancho,
            height=42,
            corner_radius=9,
            fg_color=color,
            hover_color=AZUL_CLARO,
            font=("Arial", 13, "bold"),
        )

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    def mostrar_login(self):
        self.limpiar_pantalla()

        contenedor = ctk.CTkFrame(
            self,
            width=470,
            corner_radius=22,
            fg_color=BLANCO,
            border_width=1,
            border_color=BORDE,
        )
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            contenedor,
            text="VDC",
            width=85,
            height=85,
            corner_radius=22,
            fg_color=AZUL,
            text_color=BLANCO,
            font=("Arial", 30, "bold"),
        ).pack(pady=(35, 15))

        ctk.CTkLabel(
            contenedor,
            text="SISTEMA ESCOLAR",
            font=("Arial", 27, "bold"),
            text_color=AZUL,
        ).pack(pady=4)

        ctk.CTkLabel(
            contenedor,
            text="VIRGEN DEL CARMEN",
            font=("Arial", 15, "bold"),
            text_color=AZUL_CLARO,
        ).pack(pady=4)

        ctk.CTkLabel(
            contenedor,
            text="Ingresa tus credenciales para continuar",
            text_color=GRIS,
            font=("Arial", 12),
        ).pack(pady=(8, 20))

        self.dni = ctk.CTkEntry(
            contenedor,
            width=340,
            height=45,
            placeholder_text="Número de DNI",
            corner_radius=9,
        )
        self.dni.pack(pady=9)

        fila_password = ctk.CTkFrame(
            contenedor,
            fg_color="transparent",
        )
        fila_password.pack(pady=9)

        self.password = ctk.CTkEntry(
            fila_password,
            width=275,
            height=45,
            placeholder_text="Contraseña",
            show="*",
            corner_radius=9,
        )
        self.password.pack(side="left", padx=(0, 5))

        self.boton_ver = ctk.CTkButton(
            fila_password,
            text="Ver",
            width=60,
            height=45,
            fg_color="#E7EEF7",
            hover_color="#D2DFEF",
            text_color=AZUL,
            command=self.alternar_password,
        )
        self.boton_ver.pack(side="left")

        self.password.bind(
            "<Return>",
            lambda _: self.iniciar_sesion(),
        )

        self.dni.bind(
            "<Return>",
            lambda _: self.password.focus(),
        )

        self.boton(
            contenedor,
            "INICIAR SESIÓN",
            self.iniciar_sesion,
            ancho=340,
        ).pack(pady=(18, 12))

        ctk.CTkLabel(
            contenedor,
            text="Cuenta de demostración: clave123",
            text_color=GRIS,
            font=("Arial", 11),
        ).pack(pady=(5, 30))

        self.dni.focus()

    def alternar_password(self):
        self.mostrar_password = not self.mostrar_password

        if self.mostrar_password:
            self.password.configure(show="")
            self.boton_ver.configure(text="Ocultar")
        else:
            self.password.configure(show="*")
            self.boton_ver.configure(text="Ver")

    def iniciar_sesion(self):
        try:
            dni = self.dni.get().strip()
            password = self.password.get()

            self.sesion = self.servicios["autenticar"].ejecutar(
                dni,
                password,
            )

            self.mostrar_panel()

        except ErrorDeDominio as error:
            self.alerta(
                "error",
                "Acceso denegado",
                str(error),
            )

    # --------------------------------------------------
    # ENCABEZADO Y NAVEGACIÓN
    # --------------------------------------------------

    def mostrar_encabezado(self, titulo):
        encabezado = ctk.CTkFrame(
            self,
            height=75,
            corner_radius=0,
            fg_color=AZUL,
        )
        encabezado.pack(fill="x")

        encabezado.pack_propagate(False)

        ctk.CTkLabel(
            encabezado,
            text="VDC  |  " + titulo,
            font=("Arial", 21, "bold"),
            text_color=BLANCO,
        ).pack(side="left", padx=25)

        ctk.CTkButton(
            encabezado,
            text="Cerrar sesión",
            width=130,
            height=38,
            fg_color=ROJO,
            hover_color="#B83232",
            command=self.cerrar_sesion,
        ).pack(side="right", padx=25)

    def crear_contenido(self, titulo, subtitulo=None):
        self.limpiar_pantalla()
        self.mostrar_encabezado("SISTEMA ESCOLAR")

        contenido = ctk.CTkFrame(
            self,
            fg_color=BLANCO,
            corner_radius=18,
        )
        contenido.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25,
        )

        self.crear_titulo(contenido, titulo, subtitulo)

        return contenido

    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    def mostrar_panel(self):
        self.limpiar_pantalla()
        self.mostrar_encabezado("PANEL PRINCIPAL")

        usuario = self.sesion.usuario

        bienvenida = ctk.CTkFrame(
            self,
            fg_color=BLANCO,
            corner_radius=18,
        )
        bienvenida.pack(
            fill="x",
            padx=30,
            pady=(25, 15),
        )

        ctk.CTkLabel(
            bienvenida,
            text=f"¡Bienvenido, {usuario.nombre}!",
            font=("Arial", 26, "bold"),
            text_color=AZUL,
        ).pack(anchor="w", padx=25, pady=(20, 5))

        ctk.CTkLabel(
            bienvenida,
            text=f"Perfil: {usuario.rol.value.upper()}",
            font=("Arial", 14),
            text_color=GRIS,
        ).pack(anchor="w", padx=25, pady=(0, 20))

        ctk.CTkLabel(
            self,
            text="MÓDULOS DISPONIBLES",
            font=("Arial", 19, "bold"),
            text_color=AZUL,
        ).pack(anchor="w", padx=35, pady=15)

        nombres = {
            "usuarios": "Gestión de usuarios",
            "estudiantes": "Estudiantes",
            "docentes": "Docentes",
            "cursos": "Cursos",
            "calificaciones": "Calificaciones",
            "asistencia": "Asistencia",
            "avisos": "Avisos",
            "calendario": "Calendario",
        }

        iconos = {
            "usuarios": "👥",
            "estudiantes": "🎓",
            "docentes": "👨‍🏫",
            "cursos": "📚",
            "calificaciones": "📝",
            "asistencia": "📅",
            "avisos": "🔔",
            "calendario": "🗓",
        }

        panel = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        panel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=5,
        )

        for indice, permiso in enumerate(self.sesion.permisos):
            titulo = nombres.get(permiso, permiso.title())
            icono = iconos.get(permiso, "•")

            tarjeta = ctk.CTkFrame(
                panel,
                fg_color=BLANCO,
                corner_radius=14,
                border_width=1,
                border_color=BORDE,
                width=270,
                height=115,
            )
            tarjeta.grid(
                row=indice // 3,
                column=indice % 3,
                padx=10,
                pady=10,
                sticky="nsew",
            )
            tarjeta.grid_propagate(False)

            ctk.CTkLabel(
                tarjeta,
                text=icono,
                font=("Arial", 25),
            ).pack(pady=(12, 2))

            ctk.CTkButton(
                tarjeta,
                text=titulo,
                height=35,
                fg_color="transparent",
                hover_color="#E7EEF7",
                text_color=AZUL,
                font=("Arial", 13, "bold"),
                command=lambda m=permiso, t=titulo: self.mostrar_modulo(m, t),
            ).pack(fill="x", padx=10, pady=5)

        for columna in range(3):
            panel.grid_columnconfigure(columna, weight=1)

    def mostrar_modulo(self, modulo, titulo):
        if modulo == "calificaciones":
            self.pantalla_calificaciones()
        elif modulo == "asistencia":
            self.pantalla_asistencia()
        else:
            self.pantalla_informativa(titulo)

    def pantalla_informativa(self, titulo):
        contenido = self.crear_contenido(
            titulo,
            "Módulo del Sistema Escolar VDC",
        )

        ctk.CTkLabel(
            contenido,
            text="Este módulo está pendiente de implementación.",
            font=("Arial", 15),
            text_color=GRIS,
        ).pack(pady=40)

        self.boton(
            contenido,
            "VOLVER AL PANEL",
            self.mostrar_panel,
        ).pack(pady=15)

    # --------------------------------------------------
    # ESTUDIANTES Y CURSOS VISIBLES
    # --------------------------------------------------

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

    # --------------------------------------------------
    # CALIFICACIONES
    # --------------------------------------------------

    def pantalla_calificaciones(self):
        contenido = self.crear_contenido(
            "CALIFICACIONES",
            "Consulta y gestión del rendimiento académico.",
        )

        if self.sesion.usuario.rol is Rol.DOCENTE:
            self.formulario_calificacion(contenido)

        self.tabla_calificaciones(contenido)

        self.boton(
            contenido,
            "VOLVER AL PANEL",
            self.mostrar_panel,
        ).pack(pady=15)

    def formulario_calificacion(self, padre):
        estudiantes = self.estudiantes_visibles()
        cursos = self.cursos_visibles()

        if not estudiantes or not cursos:
            ctk.CTkLabel(
                padre,
                text="No hay estudiantes o cursos disponibles.",
                text_color=GRIS,
            ).pack(pady=10)
            return

        formulario = ctk.CTkFrame(
            padre,
            fg_color=FONDO,
            corner_radius=12,
        )
        formulario.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(
            formulario,
            text="Registrar calificación",
            font=("Arial", 17, "bold"),
            text_color=AZUL,
        ).pack(pady=10)

        self.sel_estudiante = ctk.CTkOptionMenu(
            formulario,
            values=[f"{e.id} - {e.nombre}" for e in estudiantes],
            width=300,
        )
        self.sel_estudiante.pack(pady=5)

        self.sel_curso = ctk.CTkOptionMenu(
            formulario,
            values=[f"{c.id} - {c.nombre}" for c in cursos],
            width=300,
        )
        self.sel_curso.pack(pady=5)

        self.sel_periodo = ctk.CTkOptionMenu(
            formulario,
            values=["1", "2", "3", "4"],
            width=300,
        )
        self.sel_periodo.pack(pady=5)

        self.entrada_nota = ctk.CTkEntry(
            formulario,
            width=300,
            placeholder_text="Nota entre 0 y 20",
        )
        self.entrada_nota.pack(pady=5)

        self.boton(
            formulario,
            "GUARDAR CALIFICACIÓN",
            self.guardar_calificacion,
            ancho=300,
        ).pack(pady=12)

    def guardar_calificacion(self):
        try:
            estudiante_id = self.sel_estudiante.get().split(" - ")[0]
            curso_id = self.sel_curso.get().split(" - ")[0]
            periodo = int(self.sel_periodo.get())

            nota = float(self.entrada_nota.get().strip().replace(",", "."))

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
                "La nota se guardó correctamente.",
            )

            self.pantalla_calificaciones()

        except ValueError:
            self.alerta(
                "error",
                "Dato incorrecto",
                "Ingresa un número válido para la calificación.",
            )

        except ErrorDeDominio as error:
            self.alerta(
                "error",
                "No se pudo registrar",
                str(error),
            )

    def tabla_calificaciones(self, padre):
        calificaciones = self.servicios["consultar_calificaciones"].ejecutar(self.sesion.usuario)

        tabla = ctk.CTkScrollableFrame(
            padre,
            fg_color=FONDO,
            height=220,
        )
        tabla.pack(fill="both", expand=True, padx=25, pady=10)

        encabezado = ctk.CTkFrame(
            tabla,
            fg_color=AZUL,
            corner_radius=8,
        )
        encabezado.pack(fill="x", padx=5, pady=5)

        columnas = [
            ("ESTUDIANTE", 0.32),
            ("CURSO", 0.30),
            ("BIMESTRE", 0.18),
            ("NOTA", 0.20),
        ]

        for texto, proporcion in columnas:
            ctk.CTkLabel(
                encabezado,
                text=texto,
                text_color=BLANCO,
                font=("Arial", 11, "bold"),
                width=int(650 * proporcion),
            ).pack(side="left", padx=3, pady=12)

        if not calificaciones:
            ctk.CTkLabel(
                tabla,
                text="No hay calificaciones disponibles.",
                text_color=GRIS,
            ).pack(pady=20)
            return

        repo_estudiantes = self.servicios["estudiantes"]
        repo_cursos = self.servicios["cursos"]

        for cal in calificaciones:
            estudiante = repo_estudiantes.obtener(cal.estudiante_id)
            curso = repo_cursos.obtener(cal.curso_id)

            nombre = estudiante.nombre if estudiante else cal.estudiante_id
            nombre_curso = curso.nombre if curso else cal.curso_id

            fila = ctk.CTkFrame(
                tabla,
                fg_color=BLANCO,
                corner_radius=7,
            )
            fila.pack(fill="x", padx=5, pady=3)

            valores = [
                (nombre, 0.32),
                (nombre_curso, 0.30),
                (str(cal.periodo), 0.18),
                (f"{cal.nota:.2f}", 0.20),
            ]

            for texto, proporcion in valores:
                ctk.CTkLabel(
                    fila,
                    text=texto,
                    text_color=TEXTO,
                    font=("Arial", 12),
                    width=int(650 * proporcion),
                ).pack(side="left", padx=3, pady=10)

    # --------------------------------------------------
    # ASISTENCIA
    # --------------------------------------------------

    def pantalla_asistencia(self):
        contenido = self.crear_contenido(
            "CONTROL DE ASISTENCIA",
            "Registro y seguimiento de asistencia de estudiantes.",
        )

        if self.sesion.usuario.rol is Rol.DOCENTE:
            self.formulario_asistencia(contenido)

        self.tabla_asistencia(contenido)

        self.boton(
            contenido,
            "VOLVER AL PANEL",
            self.mostrar_panel,
        ).pack(pady=15)

    def formulario_asistencia(self, padre):
        estudiantes = self.estudiantes_visibles()

        if not estudiantes:
            return

        formulario = ctk.CTkFrame(
            padre,
            fg_color=FONDO,
            corner_radius=12,
        )
        formulario.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(
            formulario,
            text="Registrar asistencia",
            font=("Arial", 17, "bold"),
            text_color=AZUL,
        ).pack(pady=10)

        self.asistencia_estudiante = ctk.CTkOptionMenu(
            formulario,
            values=[f"{e.id} - {e.nombre}" for e in estudiantes],
            width=300,
        )
        self.asistencia_estudiante.pack(pady=5)

        self.asistencia_estado = ctk.CTkOptionMenu(
            formulario,
            values=["Presente", "Falta", "Tardanza", "Justificada"],
            width=300,
        )
        self.asistencia_estado.pack(pady=5)

        self.asistencia_fecha = ctk.CTkEntry(
            formulario,
            width=300,
            placeholder_text="Fecha AAAA-MM-DD",
        )
        self.asistencia_fecha.insert(0, date.today().isoformat())
        self.asistencia_fecha.pack(pady=5)

        self.boton(
            formulario,
            "REGISTRAR ASISTENCIA",
            self.guardar_asistencia,
            ancho=300,
        ).pack(pady=12)

    def guardar_asistencia(self):
        try:
            estudiante_id = self.asistencia_estudiante.get().split(" - ")[0]

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

            self.pantalla_asistencia()

        except ValueError:
            self.alerta(
                "error",
                "Fecha incorrecta",
                "Utiliza el formato AAAA-MM-DD.",
            )

        except ErrorDeDominio as error:
            self.alerta(
                "error",
                "No se pudo registrar",
                str(error),
            )

    def tabla_asistencia(self, padre):
        tabla = ctk.CTkScrollableFrame(
            padre,
            fg_color=FONDO,
            height=230,
        )
        tabla.pack(fill="both", expand=True, padx=25, pady=10)

        estudiantes = self.estudiantes_visibles()

        if not estudiantes:
            ctk.CTkLabel(
                tabla,
                text="No hay estudiantes disponibles.",
                text_color=GRIS,
            ).pack(pady=20)
            return

        for estudiante in estudiantes:
            registros = self.servicios["asistencias"].listar_por_estudiante(estudiante.id)

            resumen = self.servicios["consultar_asistencia"].resumen(estudiante.id)

            tarjeta = ctk.CTkFrame(
                tabla,
                fg_color=BLANCO,
                corner_radius=10,
            )
            tarjeta.pack(fill="x", padx=8, pady=6)

            titulo = f"{estudiante.nombre}  |  Grado: {estudiante.grado} {estudiante.seccion}"

            ctk.CTkLabel(
                tarjeta,
                text=titulo,
                font=("Arial", 14, "bold"),
                text_color=AZUL,
            ).pack(anchor="w", padx=15, pady=(12, 5))

            resumen_texto = (
                f"Días registrados: {resumen.total_dias}    "
                f"Faltas: {resumen.faltas}    "
                f"Inasistencia: {resumen.porcentaje_inasistencia}%"
            )

            ctk.CTkLabel(
                tarjeta,
                text=resumen_texto,
                font=("Arial", 12),
                text_color=ROJO if resumen.alerta else GRIS,
            ).pack(anchor="w", padx=15, pady=4)

            if resumen.alerta:
                ctk.CTkLabel(
                    tarjeta,
                    text="ALERTA: revisar inasistencias del estudiante.",
                    text_color=ROJO,
                    font=("Arial", 11, "bold"),
                ).pack(anchor="w", padx=15, pady=3)

            if registros:
                for registro in registros:
                    detalle = f"{registro.fecha.isoformat()}  -  {registro.estado.value.upper()}"

                    ctk.CTkLabel(
                        tarjeta,
                        text=detalle,
                        font=("Arial", 11),
                        text_color=GRIS,
                    ).pack(anchor="w", padx=22, pady=2)
            else:
                ctk.CTkLabel(
                    tarjeta,
                    text="Todavía no existen registros de asistencia.",
                    font=("Arial", 11),
                    text_color=GRIS,
                ).pack(anchor="w", padx=22, pady=5)

    # --------------------------------------------------
    # CIERRE DE SESIÓN
    # --------------------------------------------------

    def cerrar_sesion(self):
        self.sesion = None
        self.mostrar_login()


# --------------------------------------------------
# EJECUCIÓN
# --------------------------------------------------

if __name__ == "__main__":
    aplicacion = AplicacionEscolar()
    aplicacion.mainloop()
