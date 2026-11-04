# Wireframes de baja fidelidad — Sistema Escolar VDC

Estos wireframes representan la capa de presentación (CustomTkinter) y la relación de campos con el dominio/modelos. Son prototipos de interfaz, no evidencia de persistencia ni de que todas las acciones estén conectadas.

## Archivos
- `wireframe-login-pbi-01.png` — Inicio de sesión (PBI-01)
- `wireframe-panel-pbi-07.png` — Panel por rol (PBI-07)
- `wireframe-calificaciones-pbi-02.png` — Registro de calificaciones (PBI-02)
- `wireframe-asistencia-pbi-03.png` — Registro de asistencia (PBI-03)
- `wireframe-consulta-pbi-04.png` — Consulta de calificaciones por rol (PBI-04)

## Mapeo campo–modelo / dominio

### PBI-01 — Inicio de sesión
| Campo/elemento | Modelo o lógica |
|---|---|
| DNI | `Usuario.dni` (cadena de 8 dígitos; único) |
| Contraseña | Se verifica contra `Usuario.password_hash`; no se muestra ni almacena en texto plano |
| Ingresar | Invoca autenticación; el acceso requiere `Usuario.activo == True` |
| Módulos posteriores | Se determinan por `Usuario.rol` y permisos |

### PBI-07 — Panel principal
| Elemento | Modelo o lógica |
|---|---|
| Bienvenida | `Usuario.nombre` |
| Perfil | `Usuario.rol` (`ADMIN`, `DOCENTE`, `APODERADO`, `ESTUDIANTE`) |
| Módulos | `domain/permisos.py`; disponibilidad según rol |

### PBI-02 — Registro de calificaciones
| Campo | Modelo o lógica |
|---|---|
| Estudiante | `CalificacionModel.estudiante_id` relacionado con `EstudianteModel.nombre`; en dominio `Calificacion.estudiante_id` |
| Curso | `CursoModel.nombre`; la entidad de dominio `Calificacion` usa `curso_id` |
| Bimestre/periodo | ORM: `CalificacionModel.bimestre`; dominio: `Calificacion.periodo` |
| Nota | `CalificacionModel.nota` con CheckConstraint 0-20 (PR #13); validacion de dominio 0-20 |
| Guardar | Validar nota y periodo antes de persistir |

**Nota de consistencia:** el dominio usa periodo y el modelo ORM usa bimestre; ambos representan el bimestre(1-4).

### PBI-03 — Registro de asistencia
| Campo | Modelo o lógica |
|---|---|
| Estudiante | `Asistencia.estudiante_id` → estudiante seleccionado |
| Fecha | `Asistencia.fecha` |
| Estado | `Asistencia.estado`: `PRESENTE`, `FALTA`, `TARDANZA`, `JUSTIFICADA` |
| Alerta | `domain/asistencia.py`: alerta cuando faltas > 6 |
| Inmutabilidad | La asistencia registrada no se edita; persistencia DB se deja para un PBI futuro |

### PBI-04 — Consulta por rol
| Vista/elemento | Modelo o lógica |
|---|---|
| Apoderado | Filtrar por `Estudiante.apoderado_id == Usuario.id`; solo hijos vinculados |
| Estudiante | Solo su propio registro mediante `Estudiante.usuario_id == Usuario.id` |
| Docente | Solo calificaciones de sus cursos |
| Acceso no permitido | Denegar la consulta si el estudiante/curso no pertenece al ámbito del usuario |
| Tabla | Estudiante, curso, bimestre/periodo y nota |

## Reglas que deben quedar reflejadas
- DNI: exactamente 8 dígitos.
- Usuario inactivo: no puede iniciar sesión.
- Nota: rango 0–20; fuera de rango, error y no guardar.
- Bimestre/periodo: 1–4.
- Asistencia: estados presente, falta, tardanza y justificada.
- Alerta de inasistencia: más de 6 faltas.
- Visibilidad de calificaciones restringida por rol.


