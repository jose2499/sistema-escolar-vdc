# Wireframes de baja fidelidad — Sistema Escolar VDC

Estos wireframes representan la capa de presentación (CustomTkinter) y la relación de campos con el dominio/modelos indicada en el requerimiento. Son prototipos de interfaz, no evidencia de persistencia ni de que todas las acciones estén conectadas.

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
| DNI | `Usuario.dni` (cadena de 8 dígitos; único según requerimiento) |
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
| Bimestre/periodo | Modelo ORM indicado: `CalificacionModel.bimestre`; dominio: `Calificacion.periodo` |
| Nota | `CalificacionModel.nota` / `Calificacion.nota`; validación de dominio 0–20 |
| Guardar | Validar nota y periodo antes de persistir |

**Nota de consistencia:** el requerimiento menciona `bimestre` y el modelo de dominio inspeccionado previamente usa `periodo`. Confirmar si el adaptador mapea ambos nombres. El wireframe conserva el nombre ORM pedido por el máster y deja visible la correspondencia con el dominio.

### PBI-03 — Registro de asistencia
| Campo | Modelo o lógica |
|---|---|
| Estudiante | `Asistencia.estudiante_id` → estudiante seleccionado |
| Fecha | `Asistencia.fecha` |
| Estado | `Asistencia.estado`: `PRESENTE`, `FALTA`, `TARDANZA`, `JUSTIFICADA` |
| Alerta | `domain/asistencia.py`: alerta cuando faltas > 6 |
| Inmutabilidad | La asistencia registrada no se edita; persistencia DB se deja para un PBI futuro, según requerimiento |

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

## Observaciones para revisar contra el código
1. En el modelo ORM compartido anteriormente no se alcanzó a confirmar un `CheckConstraint` para `CalificacionModel.nota`. Verificar el archivo completo antes de afirmar que la restricción existe en base de datos; la validación de dominio 0–20 sí está descrita en `reglas_calificacion.py`.
2. El wireframe no afirma que la persistencia de asistencia esté implementada. El requerimiento la deja para un PBI futuro.
3. Los datos de ejemplo son marcadores visuales; deben reemplazarse por datos reales conectados a servicios.
