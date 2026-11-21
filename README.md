# Semáforo Playero Inteligente · Cancún

 **Sistema predictivo de balanceo de carga turística y mitigación de estrés ecológico para las playas de Cancún.**  
 Proyecto desarrollado para el Hackathon **HackMaya**.

---

##  ¿Qué es el Semáforo Playero Inteligente?

Cancún recibe millones de visitantes al año, pero el turismo masivo suele concentrarse en unas cuantas playas abiertas al este (como **Playa Delfines** y **Gaviota Azul**), provocando saturación, pisoteo de dunas embrionarias y presión sobre el arrecife de coral, mientras que las playas protegidas de la bahía norte (**Langosta**, **Tortugas**, **Caracol**) permanecen subutilizadas.

**Semáforo Playero Inteligente** no es una simple guía de viajes: es un **motor algorítmico de Capacidad de Carga Costera** que:
1. **Predice la afluencia humana** mediante curvas horarias, días de la semana y festivos.
2. **Evalúa el estrés ecológico del ecosistema** combinando sargazo, temperatura del mar sobre el arrecife, vulnerabilidad dunar y sobrecupo.
3. **Redirige activamente el flujo turístico (*Load Balancing*)**: cuando una playa entra en semáforo **Amarillo** o **Rojo**, el sistema recomienda automáticamente hasta 3 alternativas en **Verde**, indicando la ruta exacta de transporte público (**Bus R-1 / R-2**).
4. **Incorpora Ciencia Ciudadana (*Citizen Science*)**: integra reportes en tiempo real enviados por visitantes mediante códigos QR para recalibrar el semáforo sobre el terreno.

---

##  Sustento Científico & Ecológico

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

### 1. Consultar Semáforo de Playas
`GET /api/playas?fecha={YYYY-MM-DD}&hora={6..20}&festivo={true|false}`

**Ejemplo de Petición:**
```bash
curl -X GET "http://localhost:8000/api/playas?fecha=2026-11-21&hora=13&festivo=false"
```

**Ejemplo de Respuesta:**
```json
[
  {
    "id": "delfines",
    "nombre": "Playa Delfines",
    "lat": 21.062,
    "lng": -86.7778,
    "ocupacion": 100,
    "ocupacion_2h": 85,
    "estres": 57,
    "semaforo": "rojo",
    "motivos": [
      "Saturada: 100% de ocupación",
      "Mucho sargazo: riesgo de marea marrón y anoxia en pastos marinos",
      "Zona de dunas protegidas y mirador icónico de Cancún",
      "Protege el arrecife: agua cálida o zona frágil. Prohibido bloqueador químico...",
      "Validado por 2 reportes ciudadanos (QR) en las últimas 3 h"
    ],
    "transporte": "Bus R-1 o R-2 Km 18",
    "alternativas": [
      {
        "id": "langosta",
        "nombre": "Playa Langosta",
        "ocupacion": 45,
        "estres": 21,
        "transporte": "Bus R-1 o R-2 Km 5"
      }
    ]
  }
]
```

### 2. Métrica de Impacto Ecológico Evitado
`GET /api/impacto?fecha={YYYY-MM-DD}&hora={6..20}&festivo={true|false}`

Cuantifica la reducción porcentual de estrés ambiental que se logra al desviar visitantes hacia playas con menor impacto.

```json
{
  "playas_evaluadas": 12,
  "playas_en_riesgo": 7,
  "reduccion_promedio_pct": 38,
  "reportes_ciudadanos_activos": 2,
  "detalle": [
    {
      "id": "delfines",
      "nombre": "Playa Delfines",
      "semaforo": "rojo",
      "estres": 57,
      "alternativa_id": "langosta",
      "alternativa_nombre": "Playa Langosta",
      "estres_alternativa": 21,
      "reduccion_estres_pct": 63
    }
  ]
}
```

### 3. Health Check
`GET /api/salud` ➡️ `{"ok": true}`

---

##  Flujo de Ciencia Ciudadana (`reportes.json`)

Para evitar depender exclusivamente de satélites o boletines gubernamentales desactualizados, el sistema contempla **reportes in situ mediante códigos QR**.

El archivo `data/reportes.json` simula la ingesta de observaciones directas de los bañistas:

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

Cuando existen reportes en la ventana de las últimas 3 horas respecto a la fecha y hora consultadas, el backend recalibra el sargazo y la afluencia, ajustando el semáforo y mostrando la insignia de validación ciudadana.

---

##  Estructura del Repositorio

```text
semaforo-playero/
├── backend/                  # API REST en FastAPI
│   ├── engine.py             # Motor puro de cálculo ecológico y CCT
│   ├── schemas.py            # Modelos estrictos Pydantic v2
│   ├── main.py               # Endpoints FastAPI, CORS y StaticFiles
│   └── requirements.txt      # Dependencias ligeras (FastAPI, Uvicorn, Pydantic, Pytest, HTTPX)
├── data/                     # Datos estructurados y documentación científica
│   ├── playas.json           # Catálogo maestro de playas de Cancún (12 playas)
│   ├── reportes.json         # Log simulado de reportes ciudadanos por QR
│   ├── validar.py            # Script de validación de integridad de datos
│   └── docs/                 # Sustento bibliográfico y casos de prueba
│       ├── fuentes.md        # Fuentes oficiales de monitoreo (Sargazo, SST, UNAM)
│       └── pruebas.md        # Matriz de casos de prueba
├── frontend/                 # Interfaz de usuario estática (HTML5 / Bootstrap 5 / JS)
│   ├── index.html            # Dashboard interactivo con sliders de fecha y hora
│   └── style.css             # Estilos y tarjetas de semaforización
├── tests/                    # Suite de pruebas automatizadas
│   ├── conftest.py           # Configuración de fixtures
│   └── test_api.py           # 14 pruebas de integración y casos borde
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

---

##  Alineación con los ODS de la ONU

* **ODS 14 (Vida Submarina):** Mitigación del estrés térmico en el Arrecife Mesoamericano, reducción de contaminación química por protectores solares y alerta temprana contra anoxia costera.
* **ODS 12 (Producción y Consumo Responsables):** Fomento de un turismo regenerativo, consciente y no extractivo.
* **ODS 13 (Acción por el Clima):** Adaptación comunitaria ante eventos climáticos extremos y anomalías térmicas en los océanos.

---

##  Equipo (HackMaya 2026)

* **Christian** — *Arquitectura Backend, Motor Matemático de CCT & APIs (Python / FastAPI / Pytest)*
* **Abdiel** — *Desarrollo Frontend & Experiencia de Usuario (HTML / CSS / JS)*
* **Gustavo** — *Investigación de Datos Ecológicos & Georreferenciación Costera*
