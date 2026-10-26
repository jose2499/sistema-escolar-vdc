# Documentación del pipeline de CI/CD

**Responsable:** Deivi  
**Área:** DevOps y QA  
**Proyecto:** Sistema Escolar VDC

## 1. Objetivo

El objetivo de este documento es explicar el funcionamiento del proceso de integración continua del proyecto Sistema Escolar VDC. Este proceso permite revisar automáticamente los cambios realizados por los integrantes del equipo antes de incorporarlos al código principal.

La configuración se encuentra en el archivo `.github/workflows/ci.yml`. Mediante este pipeline se busca detectar errores de programación, ejecutar pruebas automatizadas y comprobar que los cambios cumplan con los criterios de calidad definidos para el proyecto.

## 2. ¿Qué es CI/CD?

La integración continua (CI) consiste en ejecutar comprobaciones automáticas cuando un desarrollador sube cambios al repositorio o actualiza una solicitud de incorporación de cambios (*Pull Request*).

La entrega continua (CD) permite preparar el software para su publicación y, cuando está configurado, automatizar su despliegue. En nuestro proyecto, esta documentación se centra principalmente en las verificaciones de integración continua y en las pruebas automatizadas.

## 3. Funcionamiento de GitHub Actions

GitHub Actions es la herramienta que permite ejecutar automáticamente las tareas definidas en los archivos de configuración del repositorio.

En este proyecto, el archivo principal de configuración es `.github/workflows/ci.yml`.

El pipeline puede incluir las siguientes etapas, según la configuración existente:

1. Detectar un `push` o una actualización de un Pull Request.
2. Preparar el entorno de ejecución.
3. Instalar las dependencias necesarias.
4. Ejecutar Ruff para revisar el código Python.
5. Ejecutar Pytest para comprobar el funcionamiento de las pruebas.
6. Calcular la cobertura de código, si está configurada.
7. Mostrar el resultado de las verificaciones en la pestaña Actions de GitHub.

Si alguna verificación falla, se deben revisar los registros, corregir el problema y volver a ejecutar el pipeline.

## 4. Ruff: análisis estático del código

Ruff es una herramienta de análisis estático para Python. Permite identificar problemas de estilo, importaciones innecesarias y otros errores que pueden detectarse sin ejecutar toda la aplicación.

Su uso ayuda a mantener un código más ordenado, legible y consistente entre los integrantes del equipo.

Un comando habitual para ejecutar esta revisión es:

    ruff check .

Si Ruff detecta problemas que las reglas configuradas consideran errores, la comprobación puede finalizar con un resultado fallido. Por ello, es recomendable ejecutar la herramienta antes de subir los cambios al repositorio.

## 5. Pytest: pruebas automatizadas

Pytest es una herramienta que permite ejecutar pruebas automatizadas en Python. Estas pruebas sirven para comprobar que las funciones y los componentes del sistema produzcan los resultados esperados.

Un comando habitual para ejecutar las pruebas es:

    pytest

Cuando una prueba falla, se debe revisar el mensaje de error, identificar la causa y corregir el código o la propia prueba si corresponde.

La ejecución automática de Pytest permite detectar regresiones y comprobar que los cambios no afecten funcionalidades que ya funcionaban correctamente.

## 6. Cobertura mínima del 70 %

La cobertura de código representa la proporción del código analizado que se ejecuta durante las pruebas automatizadas. Es un indicador útil para identificar partes del sistema que podrían necesitar más pruebas.

Para esta tarea se considera un umbral mínimo del 70 % de cobertura. Para que el pipeline compruebe este requisito, el archivo de configuración debe incluir una herramienta y un comando que calculen la cobertura y hagan fallar la validación si el porcentaje no alcanza el mínimo.

Por ejemplo, si el proyecto utiliza `pytest-cov`, el comando podría ser:

    pytest --cov=src --cov-fail-under=70

Este comando es un ejemplo de referencia. La ruta analizada y las opciones deben coincidir con la estructura real del proyecto y con la configuración existente en `ci.yml`.

Si la cobertura es inferior al 70 %, se deben revisar las partes relevantes que no cuentan con pruebas y agregar casos que comprueben su comportamiento. No basta con aumentar el porcentaje: las pruebas también deben validar resultados correctos, errores y situaciones límite.

## 7. ¿Qué ocurre cuando falla el pipeline?

Cuando una ejecución de GitHub Actions termina con errores, se recomienda seguir este procedimiento:

1. Entrar al repositorio y abrir la pestaña Actions.
2. Seleccionar la ejecución que aparece como fallida.
3. Revisar los registros del primer paso que presenta un error.
4. Si falla Ruff, corregir las observaciones de análisis estático.
5. Si falla Pytest, revisar la prueba y el comportamiento del código relacionado.
6. Si falla la cobertura, comprobar qué partes necesitan pruebas adicionales.
7. Guardar los cambios y volver a ejecutar las verificaciones.
8. Confirmar que el pipeline termine correctamente antes de solicitar la incorporación del código.

Este procedimiento permite identificar los problemas de manera ordenada y evita realizar cambios sin conocer la causa del fallo.

## 8. Buenas prácticas de CI/CD

Para mantener un proceso de desarrollo confiable, se recomienda:

- Ejecutar las pruebas antes de crear o actualizar un Pull Request.
- Mantener las dependencias del proyecto documentadas.
- Escribir pruebas que comprueben el comportamiento real de las funcionalidades.
- Revisar los registros de GitHub Actions cuando una validación falla.
- No almacenar contraseñas, claves ni tokens directamente en el repositorio.
- Mantener actualizada la documentación cuando cambie la configuración del pipeline.
- Evitar integrar cambios que tengan errores pendientes de resolver.

## 9. Conclusión

El pipeline de integración continua ayuda al equipo a detectar errores antes de incorporar los cambios a la rama principal del proyecto. Ruff permite revisar el código Python, Pytest ejecuta las pruebas automatizadas y la cobertura proporciona información sobre la parte del código que ha sido ejecutada durante dichas pruebas.

Como responsable de DevOps y QA, mi aporte consiste en documentar este proceso, comprender los resultados de las verificaciones y contribuir a que los cambios se incorporen de manera ordenada y con criterios de calidad.

Es importante verificar los comandos y las condiciones reales del archivo `.github/workflows/ci.yml` para mantener esta documentación alineada con la implementación del proyecto.
