# Semáforo Playero Inteligente · Cancún



 **Sistema predictivo de balanceo de carga turística y mitigación de estrés ecológico para las playas de Cancún.**  
 Proyecto desarrollado para el Hackathon **HackMaya** por Christian Alexis Córdova Yam / Abdiel Moreno Ayvar y Gustavo Ortíz Reyes.

---

## ¿Qué es el Semáforo Playero Inteligente?

Cancún recibe millones de visitantes al año, pero el turismo masivo suele concentrarse en unas cuantas playas abiertas al este (como **Playa Delfines** y **Gaviota Azul**), provocando saturación, pisoteo de dunas embrionarias y presión sobre el arrecife de coral, mientras que las playas protegidas de la bahía norte (**Langosta**, **Tortugas**, **Caracol**) permanecen subutilizadas.

**Semáforo Playero Inteligente** no es una simple guía de viajes: es un **motor algorítmico de Capacidad de Carga Costera** que:
1. **Predice la afluencia humana** mediante curvas horarias, días de la semana y festivos.
2. **Evalúa el estrés ecológico del ecosistema** combinando sargazo, temperatura del mar sobre el arrecife, vulnerabilidad dunar y sobrecupo.
3. **Redirige activamente el flujo turístico (*Load Balancing*)**: cuando una playa entra en semáforo **Amarillo** o **Rojo**, el sistema recomienda automáticamente hasta 3 alternativas en **Verde**, indicando la ruta exacta de transporte público (**Bus R-1 / R-2**).
4. **Incorpora Ciencia Ciudadana (*Citizen Science*)**: integra reportes en tiempo real enviados por visitantes mediante códigos QR para recalibrar el semáforo sobre el terreno.

---

## Sustento Científico & Ecológico

El motor de cálculo no utiliza números arbitrarios; está fundamentado en literatura científica y estudios ambientales del Caribe Mexicano:

* **Metodología de Capacidad de Carga Turística (Cifuentes, 1992 / CATIE / UNAM):**  
  Digitalizamos el modelo de **Capacidad de Carga Real (CCR)**, aplicando factores de corrección ambiental dinámicos ($FC_{\text{sargazo}}$, $FC_{\text{térmico}}$, $FC_{\text{fragilidad}}$, $FC_{\text{ocupación}}$) evaluados en milisegundos.
* **Mareas Marrones y Anoxia por Sargazo (Dra. Brigitta van Tussenbroek - ICMyL UNAM Puerto Morelos):**  
  La descomposición masiva de sargazo en la orilla agota el oxígeno disuelto (**anoxia**) y genera lixiviados tóxicos que aniquilan las praderas de pastos marinos (*Thalassia testudinum*). Por ello, el sargazo tiene una ponderación prioritaria del **45%** en el índice de estrés.
* **Estrés Térmico Arrecifal y Sinergia Tóxica de Bloqueadores (NOAA Coral Reef Watch):**  
  Temperaturas marinas $\ge 29.5^\circ\text{C}$ detonan blanqueamiento en el Arrecife Mesoamericano. El sistema detecta estas anomalías térmicas y dispara alertas obligatorias de **protectores biodegradables (Reef-Safe)** libres de oxibenzona y octinoxato.
* **Protección del Sistema Dunar y Temporada de Desove:**  
  Entre **mayo y octubre** (meses 5 al 10), el sistema activa automáticamente restricciones de conservación para proteger los nidos de **Tortuga Blanca (*Chelonia mydas*)** y **Caguama (*Caretta caretta*)** en playas con dunas vulnerables.

---

## Diferenciación: ¿Por qué superamos al Tablero del IMPLAN?

El Ayuntamiento de Benito Juárez cuenta con el *Tablero de Playas del IMPLAN*. Nuestro proyecto lo complementa y supera en 4 aspectos clave:

| Aspecto | Tablero IMPLAN Cancún | Semáforo Playero Inteligente |
| :--- | :--- | :--- |
| **Enfoque** | Seguridad del bañista (banderas de oleaje y guardavidas) | **Estrés ecológico y capacidad de carga integral** (arrecife, dunas, sargazo) |
| **Temporalidad** | **Pasivo / Histórico**: Muestra el estado de hace horas | **Predictivo**: Curva horaria (6 a 20 h), proyección a 2 h (`ocupacion_2h`) y festivos |
| **Gestión de Carga** | Ninguna (solo avisa si la playa está llena) | **Activa (Load Balancing)**: Redirige a playas en Verde con ruta de autobús |
| **Arquitectura** | Portal web municipal cerrado | **API REST Abierta y Ligera** + **Simulación de Ciencia Ciudadana por QR** |

---

## Documentación de la API

### 1. Consultar Semáforo de Playas (con Geolocalización y Ordenamiento GPS)
`GET /api/playas?fecha={YYYY-MM-DD}&hora={6..20}&festivo={true|false}&lat={float}&lng={float}`

* Si se envían `lat` y `lng` (ubicación GPS del usuario), cada playa incluye `distancia_km` calculada con la fórmula de Haversine y el listado se ordena automáticamente de la playa más cercana a la más lejana. Si se envía solo una coordenada sin su par, responde `HTTP 422`.

**Ejemplo de Petición:**
```bash
curl -X GET "http://localhost:8000/api/playas?fecha=2026-11-21&hora=13&festivo=false&lat=21.15&lng=-86.78"
```

**Ejemplo de Respuesta:**
```json
[
  {
    "id": "delfines",
    "nombre": "Playa Delfines",
    "lat": 21.062,
    "lng": -86.7778,
    "ocupacion": 96,
    "ocupacion_2h": 85,
    "estres": 58,
    "semaforo": "rojo",
    "motivos": [
      "Saturada: 96% de ocupación",
      "Mucho sargazo: riesgo de marea marrón y anoxia en pastos marinos",
      "Zona de dunas protegidas y mirador icónico de Cancún",
      "Protege el arrecife: agua cálida o zona frágil. Prohibido bloqueador químico...",
      "Validado por 6 reportes ciudadanos (QR) en las últimas 3 h"
    ],
    "transporte": "Bus R-1 o R-2 Km 18",
    "distancia_km": 9.8,
    "alternativas": [
      {
        "id": "pez-volador",
        "nombre": "Playa Pez Volador",
        "ocupacion": 28,
        "estres": 21,
        "transporte": "Bus R-1 o R-2 Km 5.5"
      }
    ]
  }
]
```

### 2. Detalle de Playa Individual
`GET /api/playas/{playa_id}?fecha={YYYY-MM-DD}&hora={6..20}&festivo={true|false}&lat={float}&lng={float}`

Devuelve el objeto completo de una playa específica (ideal para vistas de detalle o modales). Si el identificador no existe, responde `HTTP 404`.

### 3. Métrica de Impacto Ecológico Evitado
`GET /api/impacto?fecha={YYYY-MM-DD}&hora={6..20}&festivo={true|false}`

Cuantifica la reducción porcentual de estrés ambiental que se logra al desviar visitantes hacia playas en verde y contabiliza los reportes ciudadanos activos en la ventana de 3 horas.

```json
{
  "playas_evaluadas": 12,
  "playas_en_riesgo": 5,
  "reduccion_promedio_pct": 53,
  "reportes_ciudadanos_activos": 28,
  "detalle": [
    {
      "id": "delfines",
      "nombre": "Playa Delfines",
      "semaforo": "rojo",
      "estres": 58,
      "alternativa_id": "pez-volador",
      "alternativa_nombre": "Playa Pez Volador",
      "estres_alternativa": 21,
      "reduccion_estres_pct": 64
    }
  ]
}
```

### 4. Health Check
`GET /api/salud` -> `{"ok": true}`

---

## Interfaz Web Integrada (Frontend)

El servidor FastAPI sirve automáticamente la interfaz web estática ubicada en `frontend/`:

* **Dos modos de exploración:** *Decide antes de salir* (catálogo completo de las 12 playas) y *Encuentra tu playa ideal* (recomendación automática con el menor índice combinado de ocupación y estrés ecológico).
* **Mapa interactivo (Leaflet + OpenStreetMap):** Marcadores codificados por color del semáforo, ubicación del usuario en tiempo real y enlaces directos a rutas en Google Maps.
* **Filtros en vivo:** Selector de fecha, deslizador de horario (06:00 a 20:00) y casilla de día festivo que recalculan mapa, tarjetas e impacto ambiental al instante.
* **Tarjetas detalladas:** Muestran ocupación actual, pronóstico a 2 horas, índice de estrés ecológico, ruta de autobús R-1/R-2, distancia GPS, motivos científicos y alternativas ecológicas.

---

## Flujo de Ciencia Ciudadana (`reportes.json`)

Para evitar depender exclusivamente de satélites o boletines gubernamentales desactualizados, el sistema contempla **reportes in situ mediante códigos QR**.

El archivo `data/reportes.json` incluye **50 reportes simulados** distribuidos en las 12 playas de Cancún:

```json
[
  {
    "id": "rep-001",
    "playa_id": "delfines",
    "fecha_hora": "2026-11-21T12:45:00",
    "sargazo": 80,
    "ocupacion": 90,
    "origen": "qr_sitio"
  }
]
```

Cuando existen reportes dentro de la ventana causal de las últimas 3 horas hasta el cierre de la hora consultada (`[hora - 3h, hora:59:59]`), el backend recalibra el sargazo y la afluencia, ajustando el semáforo y mostrando la insignia de validación ciudadana.

---

## Estructura del Repositorio

```text
semaforo-playero/
├── backend/                  # API REST en FastAPI
│   ├── engine.py             # Motor puro de cálculo ecológico, CCT y distancia Haversine
│   ├── schemas.py            # Modelos estrictos Pydantic v2
│   ├── main.py               # Endpoints FastAPI, CORS, validación GPS y StaticFiles
│   └── requirements.txt      # Dependencias ligeras (FastAPI, Uvicorn, Pydantic, Pytest, HTTPX)
├── data/                     # Datos estructurados y documentación científica
│   ├── playas.json           # Catálogo maestro de playas de Cancún (12 playas validadas)
│   ├── reportes.json         # Log simulado con 50 reportes ciudadanos por QR
│   ├── validar.py            # Script de validación de integridad de datos
│   └── docs/                 # Sustento bibliográfico y casos de prueba
│       ├── fuentes.md        # Fuentes oficiales de monitoreo (Sargazo, SST, UNAM)
│       └── pruebas.md        # Matriz de 4 casos de prueba aprobados
├── frontend/                 # Interfaz web estática (HTML5 / CSS3 / Bootstrap / Leaflet / JS)
│   ├── index.html            # Landing page, vista previa móvil, controles de filtro y mapa
│   ├── app.js                # Consumo asíncrono de APIs, mapa Leaflet, GPS y tarjetas
│   ├── style.css             # Estilos responsivos y semaforización visual
│   └── images/               # Recursos gráficos y logotipos de la aplicación
├── tests/                    # Suite de pruebas automatizadas
│   ├── conftest.py           # Configuración de fixtures
│   └── test_api.py           # 17 pruebas de integración, GPS, reportes QR y casos borde
└── README.md
```

---

## Instalación y Ejecución Local

### Prerrequisitos
* Python 3.11 o superior
* Git

### En Linux / macOS:
```bash
# 1. Clonar el repositorio y entrar al backend
cd backend

# 2. Crear y activar el entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la suite de pruebas
pytest -v ../tests

# 5. Levantar el servidor de desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### En Windows (PowerShell / CMD):
```powershell
# 1. Entrar a backend
cd backend

# 2. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Correr pruebas
pytest -v ..\tests

# 5. Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

* **Interfaz Web:** Abre en tu navegador [http://localhost:8000/](http://localhost:8000/)
* **Documentación Interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Probar desde un celular

1. Conecta el celular y la laptop a la misma red Wi-Fi.
2. En Windows, ejecuta `ipconfig` y busca la dirección IPv4 de la conexión Wi-Fi.
3. Inicia el servidor con `uvicorn main:app --reload --host 0.0.0.0 --port 8000`.
4. En el celular, abre `http://<IPv4-de-la-laptop>:8000` (reemplaza el texto entre `< >` por la dirección real).

Si Windows pregunta, permite Python/Uvicorn en redes privadas. No desactives el firewall.

---

## Alineación con los ODS de la ONU

* **ODS 14 (Vida Submarina):** Mitigación del estrés térmico en el Arrecife Mesoamericano, reducción de contaminación química por protectores solares y alerta temprana contra anoxia costera.
* **ODS 12 (Producción y Consumo Responsables):** Fomento de un turismo regenerativo, consciente y no extractivo.
* **ODS 13 (Acción por el Clima):** Adaptación comunitaria ante eventos climáticos extremos y anomalías térmicas en los océanos.

---

## Equipo (HackMaya 2026)

* **Christian** — *Arquitectura Backend, Motor Matemático de CCT & APIs (Python / FastAPI / Pytest)*
* **Abdiel** — *Desarrollo Frontend & Experiencia de Usuario (HTML / CSS / JS)*
* **Gustavo** — *Investigación de Datos Ecológicos & Georreferenciación Costera*
