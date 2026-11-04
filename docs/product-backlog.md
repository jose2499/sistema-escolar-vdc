# Product Backlog – Sistema Escolar VDC

Estimación en puntos de historia (escala Fibonacci). Cada PBI tiene su issue en GitHub.

| ID | Issue | Historia de usuario | Prior. | Pts | Estado |
|---|---|---|---|---|---|
| PBI-01 | #10 | Como usuario quiero iniciar sesión con mi DNI para ver solo los módulos de mi rol. | Alta | 5 | Hecho |
| PBI-02 | #11 | Como docente quiero registrar las calificaciones de mis cursos para llevar el control por bimestre. | Alta | 5 | Hecho |
| PBI-03 | #14 | Como docente quiero registrar la asistencia diaria, y como apoderado saber cuántas faltas lleva mi hijo. | Alta | 8 | Hecho |
| PBI-04 | #15 | Como apoderado o estudiante quiero ver solo mis calificaciones para proteger la privacidad. | Alta | 5 | Hecho |
| PBI-05 | #17 | Como docente o administrador quiero enviar avisos a las familias. | Media | 5 | Pendiente |
| PBI-06 | #12 | Como administrador quiero que los datos persistan en base de datos. | Alta | 8 | Hecho |
| PBI-07 | #16 | Como usuario quiero una interfaz clara para operar el sistema. | Media | 8 | En curso |
| PBI-08 | #18 | Como administrador quiero gestionar (crear, editar, desactivar) usuarios, estudiantes, docentes y cursos. | Media | 8 | Pendiente |
| PBI-09 | #19 | Como estudiante quiero ver el calendario académico. | Baja | 5 | Pendiente |

## Criterios de aceptación (Dado / Cuando / Entonces)

**PBI-01** – Dado que un usuario ingresa su DNI de 8 dígitos y una clave válida, cuando presiona el botón de ingresar, entonces el sistema le muestra solo los módulos de su rol.

**PBI-02** – Dado que un docente está registrando una calificación, cuando ingresa una nota fuera del rango 0-20 o un bimestre inválido, entonces el sistema impide el guardado y muestra un error.

**PBI-03** – Dado que un docente registra la asistencia diaria, cuando intenta modificar un registro ya guardado, entonces el sistema bloquea la edición. Dado que un apoderado consulta, cuando su hijo supera las 6 faltas, entonces el sistema muestra una alerta.

**PBI-04** – Dado que un apoderado o estudiante inicia sesión, cuando intenta consultar calificaciones de un estudiante que no le corresponde por su rol, entonces el sistema deniega el acceso.

**PBI-05** – Dado que un docente redacta un aviso, cuando presiona enviar, entonces el sistema simula el envío (mock) por correo a los apoderados correspondientes.

**PBI-06** – Dado que el administrador ingresa datos al sistema, cuando guarda la información, entonces los datos persisten correctamente en los modelos de SQLAlchemy.

**PBI-07** – Dado que un usuario ingresa al sistema, cuando navega por las pantallas, entonces la interfaz se muestra clara y adaptada a su rol, facilitando su operación.

**PBI-08** – Dado que el administrador gestiona usuarios o cursos, cuando realiza una baja, entonces el sistema aplica una baja lógica sin eliminar los datos permanentemente.

**PBI-09** – Dado que un estudiante ingresa al sistema, cuando consulta el calendario, entonces puede visualizar las fechas académicas programadas.

## Trazabilidad con el código

| PBI | Evidencia en el repositorio |
|---|---|
| PBI-01 | Ciclo TDD en `main`: RED `8f9da5a`, GREEN `abc904a`, REFACTOR `c0ea1eb` |
| PBI-02 | Ciclo TDD en `main`: RED `8180929`, GREEN `9fc0895`, REFACTOR `ab834bb` |
| PBI-03 | Ciclo TDD en `main`: RED `a25d494` y `fd094c8`, GREEN `51c678f` y `d1e241c`, REFACTOR `168fc7c` |
| PBI-04 | Ciclo TDD en `main`: RED `bd36021`, GREEN `55b172f`, REFACTOR `823f920` |
| PBI-06 | PR #7 (persistencia ORM, relación 1:N y cascada) y PR #13 (restricción de nota 0-20) |
| PBI-07 | PR #8 (GUI de login y dashboard) y PR #20 (wireframes en `docs/wireframes/`) |

Los PBI-05, 08 y 09 están planificados para los siguientes sprints.
