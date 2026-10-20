# Sistema Escolar VDC

Gestión de **calificaciones, asistencia y acceso por rol** para la I.E. N° 51037
"Virgen del Carmen" (San Jerónimo, Cusco). Proyecto Integrador de Construcción de Software.

## Arquitectura (Clean Architecture)

```
src/escolar/
├── domain/           # entidades y reglas puras (sin dependencias externas)
├── use_cases/        # casos de uso: orquestan las reglas mediante repositorios
├── infrastructure/   # adaptadores (hoy: repositorios en memoria; luego SQLAlchemy)
└── presentation/     # interfaz de usuario (Capítulo 6)
tests/                # pytest: una prueba por regla de negocio
```

La dependencia siempre apunta hacia adentro: `presentation → use_cases → domain`.
`infrastructure` implementa los repositorios que los casos de uso consumen.

## Product Backlog implementado (Capítulo 3)

| PBI | Historia de usuario | Reglas clave |
|-----|---------------------|--------------|
| PBI-01 | Como usuario quiero iniciar sesión con mi DNI para ver solo mis módulos | DNI de 8 dígitos, clave ≤ 15, inactivos bloqueados, permisos por rol |
| PBI-02 | Como docente quiero registrar calificaciones de mis cursos | Nota 0-20, bimestre 1-4, solo el docente del curso, sin duplicados |
| PBI-03 | Como docente quiero registrar asistencia y como apoderado conocer la inasistencia | Registro inmutable, % de inasistencia, alerta al exceder 6 faltas |
| PBI-04 | Como apoderado/estudiante quiero ver solo mis notas | Visibilidad por rol y por vínculo apoderado-estudiante |

## Cómo ejecutar

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pytest pytest-cov ruff
ruff check . && ruff format --check .
pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

## Flujo de trabajo

GitHub Flow: `main` protegida, ramas `feature/*`, `fix/*`, `docs/*`, Pull Request con CI en
verde y Conventional Commits (`test:` → `feat:` → `refactor:` por cada ciclo TDD).
