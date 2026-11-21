# Documento de fuentes

**Proyecto:** Monitor de condiciones de playas de Cancún  
**Fecha de consulta de referencia:** 20 de noviembre de 2026

Este documento registra el origen de los datos utilizados por la aplicación. Los valores estimados se identifican expresamente para no presentarlos como mediciones oficiales.

## Fuentes generales

| Dato | Fuente | Uso | ¿Estimado? |
|---|---|---|---|
| Sargazo | [Observatorio Ciudadano del Sargazo](https://observatoriosargazo.com/en/caribe-mexicano/sargazo-cancun/) | Porcentaje de costa afectada por playa, según observación disponible | No, cuando existe observación |
| Temperatura del agua | [SnorkelForecast - Cancún](https://snorkelforecast.com/mexico/cancun/sea-temperature/) | Referencia regional de temperatura superficial del mar | No, es una referencia regional |
| Fragilidad | [Gaceta UNAM - Dunas costeras](https://www.gaceta.unam.mx/dunas-costeras-amenazadas-y-sin-proteccion-legal-en-mexico/) | Criterios de vulnerabilidad de dunas y erosión | Sí, índice elaborado por el equipo |
| Fragilidad | [La Jornada Maya - Deterioro del arrecife](https://www.lajornadamaya.mx/quintanaroo/239481/expertos-confirman-deterioro-del-arrecife-en-foro-de-sostenibilidad-realizado-en-cancun) | Importancia de los arrecifes como protección frente al oleaje | Sí, índice elaborado por el equipo |
| Transporte | [Playas de Cancún - Rutas de autobús](https://playasdecancun.com/en/cancun-beaches-by-bus/) | Referencia de rutas R1, R2, R10 y otras opciones | Verificación mediante guía local |
| Popularidad | [Google Trends](https://trends.google.com/trends/) | Interés relativo de búsqueda | Sí, mientras no se archive la consulta y sus datos |

## Registro de datos

| Playa | Dato | Valor | Fuente | ¿Estimado? |
|---|---|---:|---|---|
| Playa del Niño | Sargazo | 3 | Observatorio Ciudadano del Sargazo | No |
| Playa Las Perlas | Sargazo | 2 | Observatorio Ciudadano del Sargazo | No |
| Playa Langosta | Sargazo | 1 | Observatorio Ciudadano del Sargazo | No |
| Playa Tortugas | Sargazo | 25 | Observatorio Ciudadano del Sargazo | No |
| Playa Caracol | Sargazo | 0 | Observación reportada | No |
| Playa del Niño | Fragilidad | 40 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Las Perlas | Fragilidad | 50 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Langosta | Fragilidad | 50 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Pez Volador | Fragilidad | 60 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Tortugas | Fragilidad | 60 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Caracol | Fragilidad | 50 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Gaviota Azul | Fragilidad | 70 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Chac Mool | Fragilidad | 45 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Marlín | Fragilidad | 50 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Ballenas | Fragilidad | 70 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Delfines | Fragilidad | 70 | Criterio del equipo basado en vulnerabilidad costera | Sí |
| Playa Coral | Fragilidad | 65 | Criterio del equipo basado en vulnerabilidad costera | Sí |

## Consideraciones

- Un valor `null` en sargazo significa que no se dispone de una observación suficiente. No significa que la playa esté libre de sargazo.
- La temperatura de 28.6 °C es una referencia regional, no una medición individual de cada playa.
- La fragilidad es un índice experimental de 0 a 100, no una clasificación oficial.
- Los valores de popularidad deben documentarse con las consultas exactas de Google Trends y su exportación. Hasta entonces deben tratarse como estimaciones provisionales.
- Las rutas de transporte pueden cambiar. La guía consultada es una referencia y no sustituye la confirmación de horarios y recorridos vigentes.

## Enlaces utilizados

1. Observatorio Ciudadano del Sargazo: https://observatoriosargazo.com/en/caribe-mexicano/sargazo-cancun/
2. SnorkelForecast, temperatura del agua en Cancún: https://snorkelforecast.com/mexico/cancun/sea-temperature/
3. Gaceta UNAM, vulnerabilidad de dunas costeras: https://www.gaceta.unam.mx/dunas-costeras-amenazadas-y-sin-proteccion-legal-en-mexico/
4. La Jornada Maya, deterioro de arrecifes: https://www.lajornadamaya.mx/quintanaroo/239481/expertos-confirman-deterioro-del-arrecife-en-foro-de-sostenibilidad-realizado-en-cancun
5. Playas de Cancún, rutas de autobús: https://playasdecancun.com/en/cancun-beaches-by-bus/
6. Google Trends: https://trends.google.com/trends/
