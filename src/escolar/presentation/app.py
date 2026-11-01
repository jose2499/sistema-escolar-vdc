
from datetime import date

import customtkinter as ctk

from escolar.domain.entities import (
    Asistencia,
    Calificacion,
    Curso,
    Estudiante,
    EstadoAsistencia,
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


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL = "#17365D"
AZUL_CLARO = "#3973AC"
FONDO = "#F3F6FB"
VERDE = "#15803D"
ROJO = "#DC2626"
GRIS = "#64748B"


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

    # Notas de demostración.
    for estudiante_id in ("E1", "E2", "E3"):
        repo_calificaciones.guardar(
            Calificacion(estudiante_id, "C1", 1, 14, "U2")
        )
        repo_calificaciones.guardar(
            Calificacion(estudiante_id, "C2", 1, 16, "U3")
        )

    # Asistencias de demostración.
    repo_asistencias.guardar(
        Asistencia("E1", date.today(), EstadoAsistencia.PRESENTE)
    )
    repo_asistencias.guardar(
        Asistencia("E2", date.today(), EstadoAsistencia.TARDANZA)
    )

    return {
        "autenticar": AutenticarUsuario(repo_usuarios),
        "estudiantes": repo_estudiantes,
        "cursos": repo_cursos,
        "calificaciones": repo_calificaciones,
        "asistencias": repo_asistencias,
        "registrar_calificacion": RegistrarCalificacion(
            repo_estudiantes, repo_cursos, repo_calificaciones
        ),
        "consultar_calificaciones": ConsultarCalificaciones(
            repo_estudiantes, repo_cursos, repo_calificaciones
        ),
        "registrar_asistencia": RegistrarAsistencia(
            repo_estudiantes, repo_asistencias
        ),
        "consultar_asistencia": ConsultarAsistencia(
            repo_estudiantes, repo_asistencias
        ),
    }


class Alerta(ctk.CTkToplevel):
    def __init__(self, padre, tipo, titulo, mensaje):
        super().__init__(padre)

        self.transient(padre)
        self.grab_set()
        self.resizable(False, False)
        self.configure(fg_color="white")

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

        self.geometry("390x220")
        self.update_idletasks()

        x = padre.winfo_rootx() + (padre.winfo_width() - 390) // 2
        y = padre.winfo_rooty() + (padre.winfo_height() - 220) // 2
        self.geometry(f"390x220+{x}+{y}")

        ctk.CTkLabel(
            self,
            text=iconos.get(tipo, "i"),
            width=55,
            height=55,
            corner_radius=30,
            fg_color=color,
            text_color="white",
            font=("Arial", 28, "bold"),
        ).pack(pady=(20, 8))

        ctk.CTkLabel(
            self,
            text=titulo,
            font=("Arial", 20, "bold"),
            text_color=AZUL,
        ).pack(pady=3)

        ctk.CTkLabel(
            self,
            text=mensaje,
            font=("Arial", 12),
            text_color=GRIS,
            wraplength=330,
        ).pack(pady=5)

        ctk.CTkButton(
            self,
            text="ACEPTAR",
            width=130,
            fg_color=color,
            hover_color=AZUL,
            command=self.destroy,
        ).pack(pady=12)

        self.attributes("-alpha", 0.0)
        self._animar(0.0)

    def _animar(self, opacidad):
        if not self.winfo_exists():
            return

        nueva = min(opacidad + 0.15, 1.0)
        self.attributes("-alpha", nueva)

        if nueva < 1.0:
            self.after(20, lambda: self._animar(nueva))


class AplicacionEscolar(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Escolar VDC")
        self.geometry("1100x720")
        self.minsize(900, 620)
        self.configure(fg_color=FONDO)

        self.servicios = crear_servicios_demo()
        self.sesion = None

        self.mostrar_login()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def alerta(self, tipo, titulo, mensaje):
        Alerta(self, tipo, titulo, mensaje)

    def mostrar_login(self):
        self.limpiar_pantalla()

        contenedor = ctk.CTkFrame(
            self,
            width=440,
            corner_radius=22,
            fg_color="white",
        )
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            contenedor,
            text="SISTEMA ESCOLAR",
            font=("Arial", 29, "bold"),
            text_color=AZUL,
        ).pack(padx=50, pady=(40, 5))

        ctk.CTkLabel(
            contenedor,
            text="VIRGEN DEL CARMEN",
            font=("Arial", 17, "bold"),
            text_color=AZUL_CLARO,
        ).pack(pady=5)

        ctk.CTkLabel(
            contenedor,
            text="Ingresa tus datos para continuar",
            text_color=GRIS,
        ).pack(pady=(5, 25))

        self.dni = ctk.CTkEntry(
            contenedor,
            width=320,
            height=45,
            placeholder_text="Número de DNI",
        )
        self.dni.pack(pady=9)

        self.password = ctk.CTkEntry(
            contenedor,
            width=320,
            height=45,
            placeholder_text="Contraseña",
            show="*",
        )
        self.password.pack(pady=9)

        self.password.bind("<Return>", lambda _: self.iniciar_sesion())

        ctk.CTkButton(
            contenedor,
            text="INICIAR SESIÓN",
            width=320,
            height=45,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.iniciar_sesion,
        ).pack(pady=(20, 12))

        ctk.CTkLabel(
            contenedor,
            text="Acceso de demostración: clave123",
            text_color=GRIS,
            font=("Arial", 11),
        ).pack(pady=(0, 30))

    def iniciar_sesion(self):
        try:
            self.sesion = self.servicios["autenticar"].ejecutar(
                self.dni.get().strip(),
                self.password.get(),
            )
            self.mostrar_panel()

        except ErrorDeDominio as error:
            self.alerta("error", "No se pudo iniciar sesión", str(error))

    def mostrar_encabezado(self, titulo):
        encabezado = ctk.CTkFrame(
            self,
            height=75,
            corner_radius=0,
            fg_color=AZUL,
        )
        encabezado.pack(fill="x")

        ctk.CTkLabel(
            encabezado,
            text=titulo,
            font=("Arial", 23, "bold"),
            text_color="white",
        ).pack(side="left", padx=28, pady=20)

        ctk.CTkButton(
            encabezado,
            text="Cerrar sesión",
            width=130,
            fg_color=ROJO,
            hover_color="#B83232",
            command=self.cerrar_sesion,
        ).pack(side="right", padx=25)

    def mostrar_panel(self):
        self.limpiar_pantalla()
        self.mostrar_encabezado("SISTEMA ESCOLAR VDC")

        usuario = self.sesion.usuario

        ctk.CTkLabel(
            self,
            text=f"Bienvenido, {usuario.nombre}",
            font=("Arial", 27, "bold"),
            text_color=AZUL,
        ).pack(pady=(35, 5))

        ctk.CTkLabel(
            self,
            text=f"Perfil: {usuario.rol.value.upper()}",
            font=("Arial", 14),
            text_color=GRIS,
        ).pack(pady=5)

        ctk.CTkLabel(
            self,
            text="Selecciona un módulo",
            font=("Arial", 20, "bold"),
            text_color=AZUL,
        ).pack(pady=25)

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

        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.pack(pady=10)

        for indice, permiso in enumerate(self.sesion.permisos):
            titulo = nombres.get(permiso, permiso.title())

            ctk.CTkButton(
                panel,
                text=titulo,
                width=250,
                height=70,
                corner_radius=12,
                fg_color="white",
                hover_color="#DCEAF8",
                text_color=AZUL,
                border_width=1,
                border_color="#C5D5E8",
                font=("Arial", 15, "bold"),
                command=lambda m=permiso, t=titulo: self.mostrar_modulo(m, t),
            ).grid(
                row=indice // 2,
                column=indice % 2,
                padx=13,
                pady=10,
            )

    def mostrar_modulo(self, modulo, titulo):
        if modulo == "calificaciones":
            self.pantalla_calificaciones()
        elif modulo == "asistencia":
            self.pantalla_asistencia()
        else:
            self.pantalla_informativa(titulo)

    def crear_contenido(self, titulo):
        self.limpiar_pantalla()
        self.mostrar_encabezado("SISTEMA ESCOLAR VDC")

        contenido = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        contenido.pack(fill="both", expand=True, padx=35, pady=25)

        ctk.CTkLabel(
            contenido,
            text=titulo,
            font=("Arial", 25, "bold"),
            text_color=AZUL,
        ).pack(pady=(20, 15))

        return contenido

    def pantalla_informativa(self, titulo):
        contenido = self.crear_contenido(titulo)

        ctk.CTkLabel(
            contenido,
            text="Este módulo está pendiente de implementación.",
            text_color=GRIS,
            font=("Arial", 15),
        ).pack(pady=30)

        ctk.CTkButton(
            contenido,
            text="VOLVER AL PANEL",
            command=self.mostrar_panel,
        ).pack(pady=20)

    def estudiantes_visibles(self):
        usuario = self.sesion.usuario
        repo = self.servicios["estudiantes"]

        if usuario.rol is Rol.ADMIN or usuario.rol is Rol.DOCENTE:
            return list(repo._por_id.values())

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
            return list(repo._por_id.values())

        return []

    def pantalla_calificaciones(self):
        contenido = self.crear_contenido("MÓDULO DE CALIFICACIONES")

        usuario = self.sesion.usuario

        if usuario.rol is Rol.DOCENTE:
            self.formulario_calificacion(contenido)

        ctk.CTkLabel(
            contenido,
            text="Calificaciones disponibles para tu perfil",
            font=("Arial", 15, "bold"),
            text_color=AZUL,
        ).pack(pady=(15, 5))

        self.tabla_calificaciones(contenido)

        ctk.CTkButton(
            contenido,
            text="VOLVER AL PANEL",
            command=self.mostrar_panel,
        ).pack(pady=15)

    def formulario_calificacion(self, padre):
        estudiantes = self.estudiantes_visibles()
        cursos = self.cursos_visibles()

        if not estudiantes or not cursos:
            return

        formulario = ctk.CTkFrame(padre, fg_color=FONDO, corner_radius=12)
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
            width=280,
        )
        self.sel_estudiante.pack(pady=5)

        self.sel_curso = ctk.CTkOptionMenu(
            formulario,
            values=[f"{c.id} - {c.nombre}" for c in cursos],
            width=280,
        )
        self.sel_curso.pack(pady=5)

        self.sel_periodo = ctk.CTkOptionMenu(
            formulario,
            values=["1", "2", "3", "4"],
            width=280,
        )
        self.sel_periodo.pack(pady=5)

        self.entrada_nota = ctk.CTkEntry(
            formulario,
            placeholder_text="Nota de 0 a 20",
            width=280,
        )
        self.entrada_nota.pack(pady=5)

        ctk.CTkButton(
            formulario,
            text="GUARDAR CALIFICACIÓN",
            command=self.guardar_calificacion,
        ).pack(pady=12)

    def guardar_calificacion(self):
        try:
            estudiante_id = self.sel_estudiante.get().split(" - ")[0]
            curso_id = self.sel_curso.get().split(" - ")[0]
            periodo = int(self.sel_periodo.get())
            nota = float(self.entrada_nota.get().replace(",", "."))

            self.servicios["registrar_calificacion"].ejecutar(
                self.sesion.usuario,
                estudiante_id,
                curso_id,
                periodo,
                nota,
            )

            self.alerta("exito", "Calificación guardada", "La nota se registró correctamente.")
            self.pantalla_calificaciones()

        except ValueError:
            self.alerta("error", "Dato incorrecto", "Ingresa una nota numérica válida.")
        except ErrorDeDominio as error:
            self.alerta("error", "No se pudo guardar", str(error))

    def tabla_calificaciones(self, padre):
        calificaciones = self.servicios["consultar_calificaciones"].ejecutar(
            self.sesion.usuario
        )

        tabla = ctk.CTkScrollableFrame(
            padre,
            fg_color=FONDO,
            height=180,
        )
        tabla.pack(fill="both", expand=True, padx=25, pady=10)

        encabezado = "ESTUDIANTE                 CURSO                    BIMESTRE       NOTA"
        ctk.CTkLabel(
            tabla,
            text=encabezado,
            font=("Consolas", 12, "bold"),
            text_color=AZUL,
        ).pack(anchor="w", padx=10, pady=8)

        if not calificaciones:
            ctk.CTkLabel(
                tabla,
                text="No hay calificaciones disponibles.",
                text_color=GRIS,
            ).pack(pady=15)
            return

        estudiantes = self.servicios["estudiantes"]
        cursos = self.servicios["cursos"]

        for cal in calificaciones:
            estudiante = estudiantes.obtener(cal.estudiante_id)
            curso = cursos.obtener(cal.curso_id)

            nombre = estudiante.nombre if estudiante else cal.estudiante_id
            nombre_curso = curso.nombre if curso else cal.curso_id

            linea = (
                f"{nombre[:22]:22}  {nombre_curso[:20]:20}  "
                f"{cal.periodo:^8}  {cal.nota:>5.2f}"
            )

            ctk.CTkLabel(
                tabla,
                text=linea,
                font=("Consolas", 12),
                text_color="#334155",
            ).pack(anchor="w", padx=10, pady=5)

    def pantalla_asistencia(self):
        contenido = self.crear_contenido("MÓDULO DE ASISTENCIA")

        if self.sesion.usuario.rol is Rol.DOCENTE:
            self.formulario_asistencia(contenido)

        ctk.CTkLabel(
            contenido,
            text="Resumen de asistencia",
            font=("Arial", 16, "bold"),
            text_color=AZUL,
        ).pack(pady=10)

        self.tabla_asistencia(contenido)

        ctk.CTkButton(
            contenido,
            text="VOLVER AL PANEL",
            command=self.mostrar_panel,
        ).pack(pady=15)

    def formulario_asistencia(self, padre):
        estudiantes = self.estudiantes_visibles()

        if not estudiantes:
            return

        formulario = ctk.CTkFrame(padre, fg_color=FONDO, corner_radius=12)
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
            width=280,
        )
        self.asistencia_estudiante.pack(pady=5)

        self.asistencia_estado = ctk.CTkOptionMenu(
            formulario,
            values=["Presente", "Falta", "Tardanza", "Justificada"],
            width=280,
        )
        self.asistencia_estado.pack(pady=5)

        self.asistencia_fecha = ctk.CTkEntry(
            formulario,
            width=280,
            placeholder_text="Fecha AAAA-MM-DD",
        )
        self.asistencia_fecha.insert(0, date.today().isoformat())
        self.asistencia_fecha.pack(pady=5)

        ctk.CTkButton(
            formulario,
            text="REGISTRAR ASISTENCIA",
            command=self.guardar_asistencia,
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

            self.alerta("exito", "Asistencia registrada", "El registro se guardó correctamente.")
            self.pantalla_asistencia()

        except ValueError:
            self.alerta("error", "Fecha incorrecta", "Utiliza el formato AAAA-MM-DD.")
        except ErrorDeDominio as error:
            self.alerta("error", "No se pudo registrar", str(error))

    def tabla_asistencia(self, padre):
        tabla = ctk.CTkScrollableFrame(
            padre,
            fg_color=FONDO,
            height=210,
        )
        tabla.pack(fill="both", expand=True, padx=25, pady=10)

        for estudiante in self.estudiantes_visibles():
            registros = self.servicios["asistencias"].listar_por_estudiante(
                estudiante.id
            )
            resumen = self.servicios["consultar_asistencia"].resumen(estudiante.id)

            texto = (
                f"{estudiante.nombre} | Días: {resumen.total_dias} | "
                f"Faltas: {resumen.faltas} | "
                f"Inasistencia: {resumen.porcentaje_inasistencia}%"
            )

            if resumen.alerta:
                texto += " | ALERTA"

            ctk.CTkLabel(
                tabla,
                text=texto,
                text_color=ROJO if resumen.alerta else "#334155",
                font=("Arial", 12, "bold" if resumen.alerta else "normal"),
            ).pack(anchor="w", padx=10, pady=8)

            for registro in registros:
                detalle = (
                    f"    {registro.fecha.isoformat()} - "
                    f"{registro.estado.value.upper()}"
                )
                ctk.CTkLabel(
                    tabla,
                    text=detalle,
                    text_color=GRIS,
                    font=("Arial", 11),
                ).pack(anchor="w", padx=15, pady=2)

    def cerrar_sesion(self):
        self.sesion = None
        self.mostrar_login()


if __name__ == "__main__":
    aplicacion = AplicacionEscolar()
    aplicacion.mainloop()
