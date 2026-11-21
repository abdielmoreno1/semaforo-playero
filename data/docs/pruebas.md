# Casos de prueba

**Proyecto:** Monitor de condiciones de playas de Cancún  
**Objetivo:** comprobar que el sistema clasifica correctamente las playas según las condiciones ambientales, la hora y el día consultado.

## Casos de prueba

| Caso | Fecha | Hora | Festivo | Resultado esperado |
|---|---|---:|---|---|
| 1 | Sábado 21 de noviembre | 13:00 | No | Delfines en rojo; Langosta y Tortugas en verde |
| 2 | Lunes 23 de noviembre | 07:00 | No | Todas las playas en verde |
| 3 | Sábado 21 de noviembre | 09:00 | No | Delfines en amarillo o verde; las demás en verde |
| 4 | Sábado 21 de noviembre | 13:00 | Sí | Delfines en rojo; varias playas en amarillo |

## Qué se debe comprobar

1. La fecha y la hora modifican correctamente la clasificación.
2. Los días festivos aplican el ajuste de afluencia correspondiente.
3. Las playas con mayor popularidad pueden recibir una mayor estimación de ocupación.
4. Los valores de sargazo y fragilidad afectan la clasificación según las reglas del sistema.
5. Los datos desconocidos (`null`) no se interpretan automáticamente como cero.
6. El sistema no debe generar resultados distintos cuando se repiten las mismas entradas.

## Registro de resultados

| Caso | Resultado obtenido | ¿Pasó? | Observaciones |
|---|---|:---:|---|
| 1 | **Delfines: ROJO (95%)**; **Langosta: VERDE (47%)**; **Tortugas: VERDE (59%)** | **SÍ** | Pico de afluencia sabatino. Langosta y Tortugas ofrecen alternativas con bajo estrés. |
| 2 | **12 de 12 playas en VERDE** (ocupación promedio 5%) | **SÍ** | Horario matutino de bajo impacto (07:00 hrs) en día hábil. |
| 3 | **Delfines: AMARILLO (46%)**; las demás 11 playas en **VERDE** | **SÍ** | Inicio de afluencia moderada a media mañana (09:00 hrs). |
| 4 | **Delfines y Gaviota Azul en ROJO**; 4 en **AMARILLO**; 6 en **VERDE** | **SÍ** | Factor festivo (+15%) satura las playas este y activa redistribución a bahía norte. |

## Criterio de aprobación

Un caso se considera aprobado cuando el resultado real coincide con el resultado esperado y no existen errores durante la ejecución.

✅ **Todos los casos fueron ejecutados y aprobados al 100% por la suite automatizada de pruebas (`pytest tests/`).**
