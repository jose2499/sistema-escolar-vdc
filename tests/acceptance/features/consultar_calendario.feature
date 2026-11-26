Feature: Consultar calendario academico (PBI-09)
  Como estudiante del colegio
  quiero consultar el calendario academico del periodo
  para visualizar las fechas programadas de examenes y actividades

  Scenario Outline: Visualizar fechas academicas programadas por periodo
    Given que el estudiante "<estudiante>" ingresa al sistema
    And existen fechas programadas para el periodo "<periodo>"
    When consulta el calendario academico del periodo "<periodo>"
    Then el sistema muestra <cantidad> actividades programadas

    Examples:
      | estudiante | periodo | cantidad |
      | Ana Perez  | 2026-I  | 2        |
      | Luis Gomez | 2026-II | 1        |

  Scenario: Rechazar consulta de un periodo sin fechas o invalido
    Given que el estudiante "Ana Perez" ingresa al sistema
    When consulta el calendario academico del periodo ""
    Then el sistema rechaza la consulta con el mensaje "El periodo academico es obligatorio"
