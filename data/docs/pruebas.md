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
|---|---|---|---|
| 1 | Pendiente | Pendiente | |
| 2 | Pendiente | Pendiente | |
| 3 | Pendiente | Pendiente | |
| 4 | Pendiente | Pendiente | |

## Criterio de aprobación

Un caso se considera aprobado cuando el resultado real coincide con el resultado esperado y no existen errores durante la ejecución.

Los casos deben ejecutarse nuevamente después de modificar las reglas de clasificación.
